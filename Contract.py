import os
import re
import sys
import json
import base64
import time
from pyteal import *
from Crypto.Hash import SHA256
from algosdk import mnemonic
from algosdk.v2client import algod, indexer
from algosdk.future import transaction

class Contract():
    def __init__(self, API_key, algod_address, index_address, passphrase):
        # contract client info
        self.API_key = API_key
        self.algod_address = algod_address
        self.index_address = index_address
        self.passphrase = passphrase
        self.account_public_key = mnemonic.to_public_key(self.passphrase)
        self.account_private_key = mnemonic.to_private_key(self.passphrase)
        self.categories = [
            "Category1",
            "Category2",
            "Category3",
            "Category4",
            "Category5",
            "Category6",
            "Category7",
            "Category8",
            "Category9",
            "Category10",
        ]

        self.TEAL_approve_condition = None
        self.TEAL_clear_condition = None
        self.TEAL_approve_code = None
        self.TEAL_clear_code = None
        self.TEAL_approve_program = None
        self.TEAL_clear_program = None

        purestake_token = {'X-API-key': self.API_key}
        self.contract_client = algod.AlgodClient(
            self.API_key, 
            self.algod_address, 
            headers=purestake_token)
        self.indexer_client = indexer.IndexerClient(
            self.API_key, 
            self.index_address, 
            headers=purestake_token)

        self.log_file = "debug.log"
        self.search_file = "search.log"
        self.verify_file = "verify.log"
        self.directory = os.path.dirname(__file__)

    def create_code(self):
        create_content = Seq([
            App.globalPut(Bytes("Creator"), Txn.sender()),
            App.globalPut(Bytes("Hash"), Sha256(Bytes("None"))),
            App.globalPut(Bytes("Index"), Int(0)),
            App.globalPut(Bytes("Category"), Txn.application_args[1]),
            Return(Int(1))
        ])

        opt_in = If(
            Txn.application_args[1] == App.globalGet(Bytes("Category")),
            Seq([
                App.globalPut(Bytes("Hash"), Sha256(Concat(
                    App.globalGet(Bytes("Hash")),
                    Txn.application_args[2],
                    Txn.application_args[3]
                ))),
                App.globalPut(Bytes("Index"), App.globalGet(Bytes("Index")) + Int(1)),
                App.localPut(Int(0), Bytes("OptedAppId"), Txn.application_args[2]),
                App.localPut(Int(0), Bytes("AdvertiserUrl"), Txn.application_args[3]),
                App.localPut(Int(0), Bytes("Index"), App.globalGet(Bytes("Index"))),
                Return(Int(1))
            ]),
            Return(Int(0))   
        )

        close_out = Seq([
            App.localDel(Int(0), Bytes("OptedAppId")),
            App.localDel(Int(0), Bytes("AdvertiserUrl")),
            Return(Int(1))
        ])

        is_creator = Txn.sender() == App.globalGet(Bytes("Creator"))

        program = Cond(
            # if Txn.application _id() == 0 then it is the creation of this application.
            [Txn.application_id() == Int(0), create_content],
            [Txn.on_completion() == OnComplete.DeleteApplication, Return(is_creator)],
            [Txn.on_completion() == OnComplete.OptIn, opt_in],
            [Txn.on_completion() == OnComplete.CloseOut, close_out],
        )
        self.TEAL_approve_condition = program

        # clear state is similar to close out, meaning to wipe out all state records in the account if close out is failed
        clear_state = Seq([
            App.localDel(Int(0), Bytes("OptedAppId")),
            App.localDel(Int(0), Bytes("AdvertiserUrl")),
            Return(Int(1))
        ])
        program = clear_state
        self.TEAL_clear_condition = program

    def compile_code(self):
        code = compileTeal(self.TEAL_approve_condition, Mode.Application)
        self.TEAL_approve_code = code
        self.TEAL_approve_program = base64.b64decode(self.contract_client.compile(self.TEAL_approve_code)['result'])
        with open(os.path.join(self.directory, 'content_approval.teal'), 'w') as f:
            f.write(code)

        code = compileTeal(self.TEAL_clear_condition, Mode.Application)
        self.TEAL_clear_code = code
        self.TEAL_clear_program = base64.b64decode(self.contract_client.compile(self.TEAL_clear_code)['result'])
        with open(os.path.join(self.directory,'content_clear_state.teal'), 'w') as f:
            f.write(code)

    def wait_for_confirmation(self, txid):
        last_round = self.contract_client.status().get('last-round')
        txinfo = self.contract_client.pending_transaction_info(txid)
        while not (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0):
            with open(os.path.join(self.directory, self.log_file), "a+") as fp:
                fp.write("Waiting for confirmation...\n")
            last_round += 1
            self.contract_client.status_after_block(last_round)
            txinfo = self.contract_client.pending_transaction_info(txid)
        with open(os.path.join(self.directory, self.log_file), "a+") as fp:
            fp.write("Transaction {} confirmed in round {}.".format(txid, txinfo.get('confirmed-round')) + "\n")        

    def create_content_app(self, input_category):
        on_complete = transaction.OnComplete.NoOpOC.real
        params = self.contract_client.suggested_params()
        params.flat_fee = True
        params.fee = 0.1

        global_schema = transaction.StateSchema(5, 16)
        local_schema = transaction.StateSchema(6, 6)

        app_args = [
            b'Create',
            bytes(input_category, "utf-8"),
        ]

        # create / sign / verify transaction
        txn = transaction.ApplicationCreateTxn(
            self.account_public_key, params, on_complete, \
            self.TEAL_approve_program, self.TEAL_clear_program, \
            global_schema, local_schema, app_args)
        signed_txn = txn.sign(self.account_private_key)
        tx_id = signed_txn.transaction.get_txid()
        self.contract_client.send_transactions([signed_txn])
        self.wait_for_confirmation(tx_id)

        # display results
        transaction_response = self.contract_client.pending_transaction_info(tx_id)
        curr_app_id = transaction_response['application-index']
        with open(os.path.join(self.directory, self.log_file), "a+") as fp:
            fp.write("Created new app: " + str(curr_app_id) + "\n")
            
    def opt_in_app(self, opt_in_advertiser):
        apps = opt_in_advertiser.algod_client.account_info(self.account_public_key)['created-apps']
        app_id = None
        matched = False
        for app in apps:
            if 'application' in app:
                global_states = app['application']['params']['global-state']
            else:
                global_states = app['params']['global-state']

            for state in global_states:
                if base64.b64decode(state['key']).decode("utf-8") == "Category":
                    if base64.b64decode(state['value']['bytes']).decode("utf-8") == opt_in_advertiser.category:
                        matched = True
                        app_id = int(app['id'])
                        break
            if matched is True:
                break
        assert(type(app_id) is int)
        assert(matched is True)

        params = self.contract_client.suggested_params()
        params.flat_fee = True
        params.fee = 0.1
        app_args = [
            b'Opt-in',
            bytes(opt_in_advertiser.category, 'utf-8'),
            bytes(str(app_id), 'utf-8'),
            bytes("Url: " + str(opt_in_advertiser.account_public_key), 'utf-8'),
        ]

        txn = transaction.ApplicationOptInTxn(opt_in_advertiser.account_public_key, params, app_id, app_args=app_args)
        signed_txn = txn.sign(opt_in_advertiser.account_private_key)
        tx_id = signed_txn.transaction.get_txid()
        self.contract_client.send_transactions([signed_txn])
        self.wait_for_confirmation(tx_id)

        transaction_response = self.contract_client.pending_transaction_info(tx_id)
        with open(os.path.join(self.directory, self.log_file), "a+") as fp:
            fp.write("Opted-in and write to app: " + str(transaction_response['txn']['txn']['apid']) + "\n")

    def close_out_app(self, close_out_advertiser):
        apps = close_out_advertiser.algod_client.account_info(self.account_public_key)['created-apps']
        app_id = None
        matched = False
        for app in apps:
            if 'application' in app:
                global_states = app['application']['params']['global-state']
            else:
                global_states = app['params']['global-state']

            for state in global_states:
                if base64.b64decode(state['key']).decode("utf-8") == "Category":
                    if base64.b64decode(state['value']['bytes']).decode("utf-8") == close_out_advertiser.category:
                        matched = True
                        app_id = int(app['id'])
                        break
            if matched is True:
                break
        assert(type(app_id) is int)
        assert(matched is True)

        params = self.contract_client.suggested_params()
        params.flat_fee = True
        params.fee = 0.1
        app_args = [
            b'Close_Out',
        ]
            
        txn = transaction.ApplicationCloseOutTxn(close_out_advertiser.account_public_key, params, app_id, app_args=app_args)
        signed_txn = txn.sign(close_out_advertiser.account_private_key)
        tx_id = signed_txn.transaction.get_txid()
        self.contract_client.send_transactions([signed_txn])
        self.wait_for_confirmation(tx_id)

        transaction_response = self.contract_client.pending_transaction_info(tx_id)
        with open(os.path.join(self.directory, self.log_file), "a+") as fp:
            fp.write("Closed out app: " + str(transaction_response['txn']['txn']['apid']) + "\n")
            
    def clear_app(self, cleared_advertiser):
        apps = cleared_advertiser.algod_client.account_info(self.account_public_key)['created-apps']
        app_id = None
        matched = False
        for app in apps:
            if 'application' in app:
                global_states = app['application']['params']['global-state']
            else:
                global_states = app['params']['global-state']

            for state in global_states:
                if base64.b64decode(state['key']).decode("utf-8") == "Category":
                    if base64.b64decode(state['value']['bytes']).decode("utf-8") == cleared_advertiser.category:
                        matched = True
                        app_id = int(app['id'])
                        break
            if matched is True:
                break
        assert(type(app_id) is int)
        assert(matched is True)

        params = self.contract_client.suggested_params()
        params.flat_fee = True
        params.fee = 0.1
        app_args = [
            b'Clear',
        ]

        txn = transaction.ApplicationClearStateTxn(cleared_advertiser.account_public_key, params, app_id, app_args=app_args)
        signed_txn = txn.sign(cleared_advertiser.account_private_key)
        tx_id = signed_txn.transaction.get_txid()
        self.contract_client.send_transactions([signed_txn])
        self.wait_for_confirmation(tx_id)

        transaction_response = self.contract_client.pending_transaction_info(tx_id)
        with open(os.path.join(self.directory, self.log_file), "a+") as fp:
            fp.write("Cleared app: " + str(transaction_response['txn']['txn']['apid']) + "\n")    

    def delete_content_app(self, app_id):
        apps = self.contract_client.account_info(self.account_public_key)['created-apps']
        for app in apps:
            app_id = int(app['id'])
            params = self.contract_client.suggested_params()
            params.flat_fee = True
            params.fee = 0.1
            app_args = [
                b'Delete',
            ]

            txn = transaction.ApplicationDeleteTxn(self.account_public_key, params, app_id, app_args=app_args)
            signed_txn = txn.sign(self.account_private_key)
            tx_id = signed_txn.transaction.get_txid()
            self.contract_client.send_transactions([signed_txn])
            self.wait_for_confirmation(tx_id)

            transaction_response = self.contract_client.pending_transaction_info(tx_id)
            with open(os.path.join(self.directory, self.log_file), "a+") as fp:
                fp.write("Deleted app: " + str(transaction_response['txn']['txn']['apid']) + "\n")

    def init_content_contract(self, category_num):
        with open(os.path.join(self.directory, self.log_file), "a+") as fp:
            fp.write("Start initializing contract application\n")

        for x in range(1, 1 + category_num):
            idx = str(x)
            category = "Category" + idx
            self.create_content_app(category)

        with open(os.path.join(self.directory, self.log_file), "a+") as fp:
            fp.write("Contract initialized\n")

    def full_search(self, user, input_category):
        if input_category not in self.categories:
            sys.exit("Wrong search input!")

        apps = user.algod_client.account_info(self.account_public_key)['created-apps']
        app_id = None
        matched = False
        for app in apps:
            if 'application' in app:
                global_states = app['application']['params']['global-state']
            else:
                global_states = app['params']['global-state']

            for state in global_states:
                if base64.b64decode(state['key']).decode("utf-8") == "Category":
                    if base64.b64decode(state['value']['bytes']).decode("utf-8") == input_category:
                        matched = True
                        app_id = int(app['id'])
                        break
            if matched is True:
                break
        assert(type(app_id) is int)
        assert(matched is True)

        opted_in_accounts = user.indexer_client.accounts(limit=1000, application_id = app_id)['accounts']
        results = []
        for account in opted_in_accounts:
            local_states = account['apps-local-state'][0]['key-value']
            for state in local_states:
                if base64.b64decode(state['key']).decode("utf-8") != "Index":
                    results.append(base64.b64decode(state['value']['bytes']).decode("utf-8"))
        
        with open(os.path.join(self.directory, self.search_file), "a+") as fp:
            for result in results:
                fp.write(str(result))
                fp.write("\n")

    def create_hash_local_file(self, user):
        all_app_results = {}
        apps = user.algod_client.account_info(self.account_public_key)['created-apps']
        apps_info = []
        for app in apps:
            if 'application' in app:
                global_states = app['application']['params']['global-state']
            else:
                global_states = app['params']['global-state']
            for state in global_states:
                if base64.b64decode(state['key']).decode("utf-8") == "Category":
                    apps_info.append((app['id'], base64.b64decode(state['value']['bytes']).decode("utf-8")))
            
        for app_info in apps_info:
            opted_in_accounts = user.indexer_client.accounts(limit=1000, application_id = app_info[0])['accounts']
            results = []
            results.append((0, ["None"]))
            for account in opted_in_accounts:
                local_states = account['apps-local-state'][0]['key-value']
                index = None
                opted_id = None
                content = None
                for state in local_states:
                    if base64.b64decode(state['key']).decode("utf-8") == "Index":
                        index = int(state['value']['uint'])
                    elif base64.b64decode(state['key']).decode("utf-8") == "OptedAppId":
                        opted_id = base64.b64decode(state['value']['bytes']).decode("utf-8")
                    elif base64.b64decode(state['key']).decode("utf-8") == "AdvertiserUrl":
                        content = base64.b64decode(state['value']['bytes']).decode("utf-8")
                assert(type(index) is int)
                assert(type(opted_id) is str)
                assert(type(content) is str)
                results.append((index, [opted_id, content]))

            app_results = [{x[0]: x[1]} for x in sorted(results, key= lambda x: x[0])]
            all_app_results[app_info[1]] = app_results
            time.sleep(3)

        with open(os.path.join(self.directory, self.verify_file), "a+") as fp:
            fp.write(json.dumps(all_app_results))

    def compute_local_hash(self, user, input_category):
        if input_category not in self.categories:
            sys.exit("Wrong search input!")

        with open(os.path.join(self.directory, self.verify_file), "r") as fp:
            contents = json.loads(fp.readline())[input_category]

        local_digest = b""
        count = 0
        for content in contents:
            local_hash = SHA256.new()
            if len(local_digest) > 0:
                local_hash.update(local_digest)
            for item in content[str(count)]:
                local_hash.update(bytes(item, 'utf-8'))
            count += 1
            local_digest = local_hash.digest()
        
        return local_digest.hex()

    def search_hash(self, user, input_category):
        apps = user.algod_client.account_info(self.account_public_key)['created-apps']
        app_id = None
        matched = False
        for app in apps:
            if 'application' in app:
                global_states = app['application']['params']['global-state']
            else:
                global_states = app['params']['global-state']

            for state in global_states:
                if base64.b64decode(state['key']).decode("utf-8") == "Category":
                    if base64.b64decode(state['value']['bytes']).decode("utf-8") == input_category:
                        matched = True
                        app_id = int(app['id'])
                        break
            if matched is True:
                break
        assert(type(app_id) is int)
        assert(matched is True)

        app = user.indexer_client.applications(app_id)
        if 'application' in app:
            global_states = app['application']['params']['global-state']
        else:
            global_states = app['params']['global-state']
            
        for state in global_states:
            if base64.b64decode(state['key']) == b'Hash':
                online_digest = base64.b64decode(state['value']['bytes'])
                break
        return online_digest.hex()
        
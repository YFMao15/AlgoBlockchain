import os
import json
import base64
import re
from pyteal import *
from algosdk import mnemonic
from algosdk.v2client import algod, indexer
from algosdk.future import transaction

class Contract():
    def __init__(self, API_key, contract_address, passphrase):
        # contract client info
        self.API_key = API_key
        self.contract_address = contract_address
        self.passphrase = passphrase
        self.app_id = None
        self.head_app_id = None
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
            "Category11",
            "Category12"
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
            self.contract_address, 
            headers=purestake_token)
        self.indexer_client = indexer.IndexerClient(
            self.API_key, 
            self.contract_address, 
            headers=purestake_token)

    def create_code(self):
        create = Seq([
            App.globalPut(Bytes("Creator"), Txn.sender()),
            App.globalPut(Bytes("NextApp"), Bytes("None")),
            App.globalPut(Bytes("Category1"), Bytes("None")),
            App.globalPut(Bytes("Category2"), Bytes("None")),
            App.globalPut(Bytes("Category3"), Bytes("None")),
            App.globalPut(Bytes("Category4"), Bytes("None")),
            App.globalPut(Bytes("Category5"), Bytes("None")),
            App.globalPut(Bytes("Category6"), Bytes("None")),
            App.globalPut(Bytes("Category7"), Bytes("None")),
            App.globalPut(Bytes("Category8"), Bytes("None")),
            App.globalPut(Bytes("Category9"), Bytes("None")),
            App.globalPut(Bytes("Category10"), Bytes("None")),
            App.globalPut(Bytes("Category11"), Bytes("None")),
            App.globalPut(Bytes("Category12"), Bytes("None")),
            Return(Int(1))
        ])

        opt_in = Seq([
            Return(Int(1))
        ])

        # for advertiser
        write = Seq([
            App.globalPut(Txn.application_args[1], Txn.application_args[2]),
            If(
                App.optedIn(Int(0), App.id()),
                Seq([
                    App.localPut(Int(0), Bytes("OptedAppId"), App.id()),
                    App.localPut(Int(0), Bytes("AdvertiserUrl"), Txn.application_args[3]),
                ]),
                Return(Int(0))
            ),
            Return(Int(1))
        ])

        chain = Seq([
            App.globalPut(Bytes("NextApp"), Txn.application_args[1]),
            Return(Int(1))
        ])

        close_out = Seq([
            App.localDel(Int(0), Bytes("OptedAppId")),
            App.localDel(Int(0), Bytes("OptedAppAddr")),
            App.localDel(Int(0), Bytes("AdvertiserUrl")),
            App.globalPut(Txn.application_args[1], Bytes("None")),
            Return(Int(1))
        ])

        is_creator = Txn.sender() == App.globalGet(Bytes("Creator"))

        program = Cond(
            # if Txn.application _id() == 0 then it is the creation of this application.
            [Txn.application_id() == Int(0), create],
            [Txn.on_completion() == OnComplete.DeleteApplication, Return(is_creator)],
            [Txn.on_completion() == OnComplete.OptIn, opt_in],
            [Txn.on_completion() == OnComplete.CloseOut, close_out],
            [Txn.on_completion() == OnComplete.NoOp, Cond(
                [Txn.application_args[0] == Bytes("Chain"), chain],
                [Txn.application_args[0] == Bytes("Write"), write]
            )]
        )
        self.TEAL_approve_condition = program

        # clear state is similar to close out, meaning to wipe out all state records in the account if close out is failed
        clear_state = Seq([
            App.localDel(Int(0), Bytes("OptedAppId")),
            App.localDel(Int(0), Bytes("OptedAppAddr")),
            App.localDel(Int(0), Bytes("AdvertiserUrl")),
            App.globalPut(Txn.application_args[1], Bytes("None")),
            Return(Int(1))
        ])
        program = clear_state
        self.TEAL_clear_condition = program

    def compile_code(self):
        dir_name = os.path.dirname(__file__)
        code = compileTeal(self.TEAL_approve_condition, Mode.Application)
        self.TEAL_approve_code = code
        with open(os.path.join(dir_name, 'asset_approval.teal'), 'w') as f:
            f.write(code)

        code = compileTeal(self.TEAL_clear_condition, Mode.Application)
        self.TEAL_clear_code = code
        with open(os.path.join(dir_name,'asset_clear_state.teal'), 'w') as f:
            f.write(code)

    def wait_for_confirmation(self, txid):
        last_round = self.contract_client.status().get('last-round')
        txinfo = self.contract_client.pending_transaction_info(txid)
        while not (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0):
            print("Waiting for confirmation...")
            last_round += 1
            self.contract_client.status_after_block(last_round)
            txinfo = self.contract_client.pending_transaction_info(txid)
        print("Transaction {} confirmed in round {}.".format(txid, txinfo.get('confirmed-round')))

    def read_head_app_id(self):        
        if os.path.exists(os.path.join(os.path.dirname(__file__), str(mnemonic.to_public_key(self.passphrase))+".txt" )):
            with open(os.path.join(os.path.dirname(__file__), str(mnemonic.to_public_key(self.passphrase))+".txt"), 'r') as fp:
                try:
                    self.indexer_client.applications(int(fp.readline()))
                except:
                    self.head_app_id = "None"
                    pass
                
            if self.head_app_id != "None":
                with open(os.path.join(os.path.dirname(__file__), str(mnemonic.to_public_key(self.passphrase))+".txt"), 'r') as fp:
                    self.head_app_id = str(fp.readline())
            else:
                os.remove(os.path.join(os.path.dirname(__file__), str(mnemonic.to_public_key(self.passphrase))+".txt"))
                self.head_app_id = "None"
        else:
            self.head_app_id = "None"

    def write_head_app_id(self):
        with open(os.path.join(os.path.dirname(__file__), str(mnemonic.to_public_key(self.passphrase))+".txt"), 'w') as fp:
            fp.write(str(self.head_app_id))

    def search_blank(self, category_input):
        self.read_head_app_id()
        print("Searching blank area for category " + str(category_input))
        if self.head_app_id != "None":
            prev_app_id = self.head_app_id + ""
            next_app_id = prev_app_id + ""
            while next_app_id != "None":
                prev_app_id = next_app_id + ""
                app = self.indexer_client.applications(int(prev_app_id))
                if 'application' in app:
                    global_states = app['application']['params']['global-state']
                else:
                    global_states = app['params']['global-state']
                for state in global_states:
                    if base64.b64decode(state['key']) == b'NextApp':
                        next_app_id = base64.b64decode(state['value']['bytes']).decode('utf-8')
                    if base64.b64decode(state['key']) == bytes(category_input, 'utf-8'):
                        if base64.b64decode(state['value']['bytes']).decode('utf-8') == "None":
                            return int(prev_app_id)
            return None
        else:
            return None

    def create_contract_app(self):
        # compile the code into client
        self.TEAL_approve_program = base64.b64decode(self.contract_client.compile(self.TEAL_approve_code)['result'])
        self.TEAL_clear_program = base64.b64decode(self.contract_client.compile(self.TEAL_clear_code)['result'])

        creator = mnemonic.to_public_key(self.passphrase)
        on_complete = transaction.OnComplete.NoOpOC.real
        params = self.contract_client.suggested_params()
        params.flat_fee = True
        params.fee = 0.1

        global_schema = transaction.StateSchema(5, 15)
        local_schema = transaction.StateSchema(6, 6)
        app_args = [
            b'Create',
        ]

        # create / sign / verify transaction
        txn = transaction.ApplicationCreateTxn(
            creator, params, on_complete, \
            self.TEAL_approve_program, self.TEAL_clear_program, \
            global_schema, local_schema, app_args)
        signed_txn = txn.sign(mnemonic.to_private_key(self.passphrase))
        tx_id = signed_txn.transaction.get_txid()
        self.contract_client.send_transactions([signed_txn])
        self.wait_for_confirmation(tx_id)

        # display results
        transaction_response = self.contract_client.pending_transaction_info(tx_id)
        self.app_id = transaction_response['application-index']
        print("Created new app-id:", self.app_id)

    def opt_in_app(self, opt_in_advertiser):
        print("Opt in app from account: ", opt_in_advertiser.account_public_key)
        params = self.contract_client.suggested_params()
        params.flat_fee = True
        params.fee = 0.1
        app_args = [
            b'Opt-in',
        ]

        txn = transaction.ApplicationOptInTxn(opt_in_advertiser.account_public_key, params, self.app_id, app_args=app_args)
        signed_txn = txn.sign(opt_in_advertiser.account_private_key)
        tx_id = signed_txn.transaction.get_txid()
        self.contract_client.send_transactions([signed_txn])
        self.wait_for_confirmation(tx_id)

        transaction_response = self.contract_client.pending_transaction_info(tx_id)
        print("OptIn to app-id:", transaction_response['txn']['txn']['apid'])
            
    def write_app(self, writing_advertiser):
        prev_app_id = self.head_app_id
        next_app_id = prev_app_id + ""
        while next_app_id != "None":
            prev_app_id = next_app_id + ""
            app = self.indexer_client.applications(int(prev_app_id))
            if 'application' in app:
                global_states = app['application']['params']['global-state']
            else:
                global_states = app['params']['global-state']
            for state in global_states:
                if base64.b64decode(state['key']) == b'NextApp':
                    next_app_id = base64.b64decode(state['value']['bytes']).decode('utf-8')
                if base64.b64decode(state['key']) == bytes(writing_advertiser.category, 'utf-8'):
                    app_category_content = base64.b64decode(state['value']['bytes']).decode('utf-8')
                    if app_category_content == "None":
                        next_app_id = "None"
                        break

        print("Write advertiser info from account:", writing_advertiser.account_public_key)
        params = self.contract_client.suggested_params()
        params.flat_fee = True
        params.fee = 0.1
        app_args = [
            b'Write',
            bytes(str(writing_advertiser.category), 'utf-8'),
            bytes(str(writing_advertiser.account_public_key), 'utf-8'),
            bytes("Url: " + str(writing_advertiser.account_public_key), 'utf-8'),
        ]

        txn = transaction.ApplicationNoOpTxn(writing_advertiser.account_public_key, params, int(prev_app_id), app_args=app_args)
        signed_txn = txn.sign(writing_advertiser.account_private_key)
        tx_id = signed_txn.transaction.get_txid()
        self.contract_client.send_transactions([signed_txn])
        self.wait_for_confirmation(tx_id)

        transaction_response = self.contract_client.pending_transaction_info(tx_id)
        print("Write to app-id:",transaction_response['txn']['txn']['apid'])

    def chain_app(self, app_id):
        creator = mnemonic.to_public_key(self.passphrase)
        prev_app_id = self.head_app_id
        if prev_app_id == "None":
            self.head_app_id = str(self.app_id)
            self.write_head_app_id()
        else:
            next_app_id = prev_app_id + ""
            while next_app_id != "None":
                prev_app_id = next_app_id + ""
                app = self.indexer_client.applications(int(prev_app_id))
                if 'application' in app:
                    global_states = app['application']['params']['global-state']
                else:
                    global_states = app['params']['global-state']
                for state in global_states:
                    if base64.b64decode(state['key']) == b'NextApp':
                        next_app_id = base64.b64decode(state['value']['bytes']).decode('utf-8')

            print("Chain app from account:", creator)
            params = self.contract_client.suggested_params()
            params.flat_fee = True
            params.fee = 0.1
            app_args = [
                b'Chain',
                bytes(str(self.app_id), 'utf-8')
            ]
            txn = transaction.ApplicationNoOpTxn(creator, params, int(prev_app_id), app_args=app_args)
            signed_txn = txn.sign(mnemonic.to_private_key(self.passphrase))
            tx_id = signed_txn.transaction.get_txid()
            self.contract_client.send_transactions([signed_txn])
            self.wait_for_confirmation(tx_id)

            transaction_response = self.contract_client.pending_transaction_info(tx_id)
            print("Chain to app-id:",transaction_response['txn']['txn']['apid'])

    def add_adv_into_app(self, advertiser):
        self.read_head_app_id()
        result = self.search_blank(advertiser.category)
        # self.app_id -> opt-in, write, close_out, delete 
        self.app_id = result
        self.opt_in_app(advertiser)
        self.write_app(advertiser)

    def close_out_app(self, close_out_advertiser):
        print("Close out app from account:", close_out_advertiser.account_public_key)
        params = self.contract_client.suggested_params()
        params.flat_fee = True
        params.fee = 0.1
        app_args = [
            b'Close_Out',
            bytes(close_out_advertiser.category, 'utf-8'),
        ]
            
        txn = transaction.ApplicationCloseOutTxn(close_out_advertiser.account_public_key, params, self.app_id, app_args=app_args)
        signed_txn = txn.sign(close_out_advertiser.account_private_key)
        tx_id = signed_txn.transaction.get_txid()
        self.contract_client.send_transactions([signed_txn])
        self.wait_for_confirmation(tx_id)

        transaction_response = self.contract_client.pending_transaction_info(tx_id)
        print("Closed out to app-id: ",transaction_response['txn']['txn']['apid'])
            
    def clear_app(self, clear_advertiser):
        print("Clear app from account:", clear_advertiser.account_public_key)
        params = self.contract_client.suggested_params()
        params.flat_fee = True
        params.fee = 0.1
        app_args = [
            b'Clear',
            bytes(clear_advertiser.category, 'utf-8'),
        ]

        txn = transaction.ApplicationClearStateTxn(clear_advertiser.account_public_key, params, self.app_id, app_args=app_args)
        signed_txn = txn.sign(clear_advertiser.account_private_key)
        tx_id = signed_txn.transaction.get_txid()
        self.contract_client.send_transactions([signed_txn])
        self.wait_for_confirmation(tx_id)

        transaction_response = self.contract_client.pending_transaction_info(tx_id)
        print("Cleared app-id:", transaction_response['txn']['txn']['apid'])    

    def delete_contract_app(self):
        creator = mnemonic.to_public_key(self.passphrase)
        params = self.contract_client.suggested_params()
        params.flat_fee = True
        params.fee = 0.1
        app_args = [
            b'Delete',
        ]

        txn = transaction.ApplicationDeleteTxn(creator, params, self.app_id, app_args=app_args)
        signed_txn = txn.sign(mnemonic.to_private_key(self.passphrase))
        tx_id = signed_txn.transaction.get_txid()
        self.contract_client.send_transactions([signed_txn])
        self.wait_for_confirmation(tx_id)

        transaction_response = self.contract_client.pending_transaction_info(tx_id)
        print("Deleted app-id:", transaction_response['txn']['txn']['apid'])
        # clear all info
        self.app_id = None

    def external_search(self, user, category_input):
        self.read_head_app_id()
        results = []
        print("Searching for category " + str(category_input))
        if self.head_app_id != "None":
            prev_app_id = self.head_app_id + ""
            next_app_id = prev_app_id + ""
            while next_app_id != "None":
                prev_app_id = next_app_id + ""
                app = user.indexer_client.applications(int(prev_app_id))
                if 'application' in app:
                    global_states = app['application']['params']['global-state']
                else:
                    global_states = app['params']['global-state']
                for state in global_states:
                    if base64.b64decode(state['key']) == b'NextApp':
                        next_app_id = base64.b64decode(state['value']['bytes']).decode('utf-8')
                    if base64.b64decode(state['key']) == bytes(category_input, 'utf-8'):
                        if base64.b64decode(state['value']['bytes']).decode('utf-8') != "None":
                            results.append(base64.b64decode(state['value']['bytes']).decode('utf-8'))
                            local_vars = user.user_client.account_info(base64.b64decode(state['value']['bytes']).decode('utf-8'))['apps-local-state']
                            for local_var in local_vars:
                                if local_var['id'] == int(prev_app_id):
                                    for x in local_var['key-value']:
                                        key = base64.b64decode(x['key']).decode('utf-8')
                                        value = x['value']
                                        if len(value['bytes']) == 0:
                                            results.append({key: value['uint']})
                                        else:
                                            results.append({key:  base64.b64decode(value['bytes']).decode('utf-8')})
                                    break        
            return results
        else:
            print("Head app is not existed!")
    
if __name__ == "__main__":
    contract_client = Contract(
        API_key = "afETOBfGPz3JfzIY3B1VG48kIGsMrlxO67VdEeOC",
        contract_address = "https://testnet-algorand.api.purestake.io/ps2",
        passphrase = "guilt ensure again delay cream rude detect blanket athlete flock cram return eager skate behind scene chase action stock mask cricket tail pistol above ankle")
    contract_client.create_code()
    contract_client.compile_code()
    contract_client.create_contract_app()
    contract_client.delete_contract_app()
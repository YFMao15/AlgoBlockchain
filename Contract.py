import os
import sys
import json
import time
import base64
import string
import datetime
import numpy as np
from pyteal import *
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
        # algoexplorer_token = {}
        # self.contract_client =  algod.AlgodClient(
        #     self.API_key, 
        #     self.algod_address, 
        #     headers=algoexplorer_token)
        # self.indexer_client = indexer.IndexerClient(
        #     self.API_key, 
        #     self.index_address, 
        #     headers=algoexplorer_token)

        self.log_file = "debug.log"
        self.search_file = "search.log"
        self.directory = os.path.dirname(__file__)

    def create_code(self):
        create_content = Seq([
            App.globalPut(Bytes("Index"), Int(0)),
            App.globalPut(Bytes("Category"), Txn.application_args[1]),
            Return(Int(1))
        ])

        opt_in = If(
            Txn.application_args[0] == App.globalGet(Bytes("Category")),
            Seq([
                App.globalPut(Bytes("Index"), App.globalGet(Bytes("Index")) + Int(1)),
                App.localPut(Int(0), Bytes("Index"), App.globalGet(Bytes("Index"))),
                App.localPut(Int(0), Bytes("Share1"), Txn.application_args[1]),
                App.localPut(Int(0), Bytes("Share2"), Txn.application_args[2]),
                App.localPut(Int(0), Bytes("Share3"), Txn.application_args[3]),
                App.localPut(Int(0), Bytes("Share4"), Txn.application_args[4]),
                App.localPut(Int(0), Bytes("Share5"), Txn.application_args[5]),
                App.localPut(Int(0), Bytes("Share6"), Txn.application_args[6]),
                App.localPut(Int(0), Bytes("Share7"), Txn.application_args[7]),
                App.localPut(Int(0), Bytes("Share8"), Txn.application_args[8]),
                App.localPut(Int(0), Bytes("Share9"), Txn.application_args[9]),
                App.localPut(Int(0), Bytes("Share10"), Txn.application_args[10]),
                App.localPut(Int(0), Bytes("Share11"), Txn.application_args[11]),
                App.localPut(Int(0), Bytes("Share12"), Txn.application_args[12]),
                App.localPut(Int(0), Bytes("Share13"), Txn.application_args[13]),
                App.localPut(Int(0), Bytes("Share14"), Txn.application_args[14]),
                App.localPut(Int(0), Bytes("Share15"), Txn.application_args[15]),
                Return(Int(1))
            ]),
            Return(Int(0))   
        )
        
        update = If(
            App.optedIn(Int(0), App.id()),
            Seq([
                App.localPut(Int(0), Bytes("Share1"), Txn.application_args[1]),
                App.localPut(Int(0), Bytes("Share2"), Txn.application_args[2]),
                App.localPut(Int(0), Bytes("Share3"), Txn.application_args[3]),
                App.localPut(Int(0), Bytes("Share4"), Txn.application_args[4]),
                App.localPut(Int(0), Bytes("Share5"), Txn.application_args[5]),
                App.localPut(Int(0), Bytes("Share6"), Txn.application_args[6]),
                App.localPut(Int(0), Bytes("Share7"), Txn.application_args[7]),
                App.localPut(Int(0), Bytes("Share8"), Txn.application_args[8]),
                App.localPut(Int(0), Bytes("Share9"), Txn.application_args[9]),
                App.localPut(Int(0), Bytes("Share10"), Txn.application_args[10]),
                App.localPut(Int(0), Bytes("Share11"), Txn.application_args[11]),
                App.localPut(Int(0), Bytes("Share12"), Txn.application_args[12]),
                App.localPut(Int(0), Bytes("Share13"), Txn.application_args[13]),
                App.localPut(Int(0), Bytes("Share14"), Txn.application_args[14]),
                App.localPut(Int(0), Bytes("Share15"), Txn.application_args[15]),
                Return(Int(1))
            ]),
            Return(Int(0))
        )

        close_out = If(
            App.optedIn(Int(0), App.id()),
            Seq([
                App.localDel(Int(0), Bytes("Index")),
                App.localDel(Int(0), Bytes("Share1")),
                App.localDel(Int(0), Bytes("Share2")),
                App.localDel(Int(0), Bytes("Share3")),
                App.localDel(Int(0), Bytes("Share4")),
                App.localDel(Int(0), Bytes("Share5")),
                App.localDel(Int(0), Bytes("Share6")),
                App.localDel(Int(0), Bytes("Share7")),
                App.localDel(Int(0), Bytes("Share8")),
                App.localDel(Int(0), Bytes("Share9")),
                App.localDel(Int(0), Bytes("Share10")),
                App.localDel(Int(0), Bytes("Share11")),
                App.localDel(Int(0), Bytes("Share12")),
                App.localDel(Int(0), Bytes("Share13")),
                App.localDel(Int(0), Bytes("Share14")),
                App.localDel(Int(0), Bytes("Share15")),
                Return(Int(1))
            ]),
            Return(Int(0))
        )

        program = Cond(
            # if Txn.application _id() == 0 then it is the creation of this application.
            [Txn.application_id() == Int(0), create_content],
            [Txn.on_completion() == OnComplete.OptIn, opt_in],
            [Txn.on_completion() == OnComplete.CloseOut, close_out],
            [Txn.on_completion() == OnComplete.NoOp, update]
        )
        self.TEAL_approve_condition = program

        # clear state is similar to close out, meaning to wipe out all state records in the account if close out is failed
        clear_state = Seq([
                App.localDel(Int(0), Bytes("Index")),
                App.localDel(Int(0), Bytes("Share1")),
                App.localDel(Int(0), Bytes("Share2")),
                App.localDel(Int(0), Bytes("Share3")),
                App.localDel(Int(0), Bytes("Share4")),
                App.localDel(Int(0), Bytes("Share5")),
                App.localDel(Int(0), Bytes("Share6")),
                App.localDel(Int(0), Bytes("Share7")),
                App.localDel(Int(0), Bytes("Share8")),
                App.localDel(Int(0), Bytes("Share9")),
                App.localDel(Int(0), Bytes("Share10")),
                App.localDel(Int(0), Bytes("Share11")),
                App.localDel(Int(0), Bytes("Share12")),
                App.localDel(Int(0), Bytes("Share13")),
                App.localDel(Int(0), Bytes("Share14")),
                App.localDel(Int(0), Bytes("Share15")),
                Return(Int(1))
            ])
            
        program = clear_state
        self.TEAL_clear_condition = program

    def compile_code(self):
        self.TEAL_approve_code = compileTeal(self.TEAL_approve_condition, Mode.Application)
        self.TEAL_approve_program = base64.b64decode(self.contract_client.compile(self.TEAL_approve_code)['result'])
        with open(os.path.join(self.directory, 'content_approval.teal'), 'w') as f:
            f.write(self.TEAL_approve_code)

        self.TEAL_clear_code = compileTeal(self.TEAL_clear_condition, Mode.Application)
        self.TEAL_clear_program = base64.b64decode(self.contract_client.compile(self.TEAL_clear_code)['result'])
        with open(os.path.join(self.directory,'content_clear_state.teal'), 'w') as f:
            f.write(self.TEAL_clear_code)

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
        return True

    # def intToBytes(self, integer):
    #     lower8 = (1 << 8) - 1
    #     char_list = [
    #         (integer >> (8*7)) & lower8,
    #         (integer >> (8*6)) & lower8,
    #         (integer >> (8*5)) & lower8,
    #         (integer >> (8*4)) & lower8,
    #         (integer >> (8*3)) & lower8,
    #         (integer >> (8*2)) & lower8,
    #         (integer >> (8*1)) & lower8,
    #         integer & lower8
    #     ]
    #     string = ''.join(chr(c) for c in char_list)
    #     return string.encode('latin1')

    def create_content_app(self, input_category):
        on_complete = transaction.OnComplete.NoOpOC.real
        params = self.contract_client.suggested_params()
        params.flat_fee = True
        params.fee = 0.1

        global_schema = transaction.StateSchema(6, 6)
        local_schema = transaction.StateSchema(1, 15)

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
        with open(os.path.join(self.directory, self.log_file), "a+") as fp:
            fp.write("Created new app: " + str(transaction_response['application-index']) + "\n")
            
    def opt_in_app(self, opt_in_advertiser):
        for category in opt_in_advertiser.category:
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
                        if base64.b64decode(state['value']['bytes']).decode("utf-8") == category:
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
                bytes(category, 'utf-8'),
            ] + [opt_in_advertiser.content[x*64: (x+1)*64] for x in range(15)]

            txn = transaction.ApplicationOptInTxn(opt_in_advertiser.account_public_key, params, app_id, app_args=app_args)
            signed_txn = txn.sign(opt_in_advertiser.account_private_key)
            tx_id = signed_txn.transaction.get_txid()
            self.contract_client.send_transactions([signed_txn])
            self.wait_for_confirmation(tx_id)

            transaction_response = self.contract_client.pending_transaction_info(tx_id)
            with open(os.path.join(self.directory, self.log_file), "a+") as fp:
                fp.write("Opted-in and write to app: " + str(transaction_response['txn']['txn']['apid']) + "\n")

    def update_app(self, update_advertiser):
        for category in update_advertiser.category:
            apps = update_advertiser.algod_client.account_info(self.account_public_key)['created-apps']
            app_id = None
            matched = False
            for app in apps:
                if 'application' in app:
                    global_states = app['application']['params']['global-state']
                else:
                    global_states = app['params']['global-state']

                for state in global_states:
                    if base64.b64decode(state['key']).decode("utf-8") == "Category":
                        if base64.b64decode(state['value']['bytes']).decode("utf-8") == category:
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
                bytes(category, 'utf-8'),
            ] + [update_advertiser.content[x*64: (x+1)*64] for x in range(15)]

            txn = transaction.ApplicationNoOpTxn(update_advertiser.account_public_key, params, app_id, app_args=app_args)
            signed_txn = txn.sign(update_advertiser.account_private_key)
            tx_id = signed_txn.transaction.get_txid()
            self.contract_client.send_transactions([signed_txn])
            self.wait_for_confirmation(tx_id)

            transaction_response = self.contract_client.pending_transaction_info(tx_id)
            with open(os.path.join(self.directory, self.log_file), "a+") as fp:
                fp.write("Update app: " + str(transaction_response['txn']['txn']['apid']) + "\n")
        
    def close_out_app(self, close_out_advertiser):
        for category in close_out_advertiser.category:
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
                        if base64.b64decode(state['value']['bytes']).decode("utf-8") == category:
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
                b'Close_Out'
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
        for category in cleared_advertiser.category:
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
                        if base64.b64decode(state['value']['bytes']).decode("utf-8") == category:
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
    
    def init_contract(self, category_num):
        with open(os.path.join(self.directory, self.log_file), "a+") as fp:
            fp.write("Start initializing contract application\n")

        for x in range(1, 1 + category_num):
            idx = str(x)
            category = "Category" + idx
            self.create_content_app(category)

        with open(os.path.join(self.directory, self.log_file), "a+") as fp:
            fp.write("Contract initialized\n")
    
    def check_contract(self, category, advertiser_num):
        with open(os.path.join(self.directory, self.log_file), "a+") as fp:
            fp.write("Checking existed contract application\n")

        apps = self.contract_client.account_info(self.account_public_key)['created-apps']
        app_found = False
        for app in apps:
            if 'application' in app:
                global_states = app['application']['params']['global-state']
            else:
                global_states = app['params']['global-state']
            for state in global_states:
                if base64.b64decode(state['key']).decode("utf-8") == "Category":
                    if base64.b64decode(state['value']['bytes']).decode("utf-8") == category:
                        app_found = True
                        break
            if app_found is True:
                break
                
        if 'application' in app:
            global_states = app['application']['params']['global-state']
        else:
            global_states = app['params']['global-state']
        for state in global_states:        
            if base64.b64decode(state['key']).decode("utf-8") == "Index":
                existed_advertiser_num = state['value']['uint']
                break
        assert(advertiser_num >= existed_advertiser_num)
        return existed_advertiser_num

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

        txns_dict = {}
        txns = self.indexer_client.search_transactions(application_id=app_id)['transactions']
        for txn in txns:
            txn_args = txn['application-transaction']['application-args']
            txn_plain_args = []
            for txn_arg in txn_args:
                txn_plain_args.append(base64.b64decode(txn_arg))
            # txn['round-time'] assumes the time zone as UTC+0 by default
            txns_dict[txn['round-time']] = txn_args
        
        with open(os.path.join(self.directory, self.search_file), "a+") as fp:
            fp.write(json.dumps(txns_dict))
        
    def search_by_time(self, user, input_category, timestamp):
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

        assert(type(timestamp) is datetime.datetime)
        assert(timestamp.tzinfo is datetime.timezone.utc)
        txns_dict = {}
        txns = self.indexer_client.search_transactions(application_id=app_id, start_time=timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ"))['transactions']
        for txn in txns:
            txn_args = txn['application-transaction']['application-args']
            txn_plain_args = []
            for txn_arg in txn_args:
                txn_plain_args.append(base64.b64decode(txn_arg))
            # txn['round-time'] assumes the time zone as UTC+0 by default
            txns_dict[txn['round-time']] = txn_args
        
        with open(os.path.join(self.directory, self.search_file), "a+") as fp:
            fp.write(json.dumps(txns_dict))
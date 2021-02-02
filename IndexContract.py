import os
import re
import json
import base64
import time
import sys
from pyteal import *
from algosdk import mnemonic
from algosdk.v2client import algod, indexer
from algosdk.future import transaction

class IndexContract():
    def __init__(self, API_key, contract_address, passphrase):
        # contract client info
        self.API_key = API_key
        self.contract_address = contract_address
        self.passphrase = passphrase
        self.account_public_key = mnemonic.to_public_key(self.passphrase)
        self.account_private_key = mnemonic.to_private_key(self.passphrase)
        # app storing the head ids
        self.head_app_id = None
        # app storing the end ids
        self.end_app_id = None
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
        self.head_app_of_categories = {}
        self.end_app_of_categories = {}

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
        self.log_file = None
        self.index_folder = None
        self.directory = None
        
    def create_code(self):
        create_head = Seq([
            App.globalPut(Bytes("Creator"), Txn.sender()),
            Return(Int(1))
        ])

        create_end = Seq([
            App.globalPut(Bytes("Creator"), Txn.sender()),
            Return(Int(1))
        ])

        write_head = Seq([
            App.globalPut(Txn.application_args[2], Txn.application_args[3]),
            Return(Int(1))
        ])

        write_end = Seq([
            App.globalPut(Txn.application_args[2], Txn.application_args[3]),
            Return(Int(1))
        ])

        is_creator = Txn.sender() == App.globalGet(Bytes("Creator"))

        program = Cond(
            # if Txn.application _id() == 0 then it is the creation of this application.
            [Txn.application_id() == Int(0), Cond(
                [Txn.application_args[1] == Bytes("Head"), create_head],
                [Txn.application_args[1] == Bytes("End"), create_end],
            )],
            [Txn.on_completion() == OnComplete.DeleteApplication, Return(is_creator)],
            [Txn.on_completion() == OnComplete.NoOp, Cond(
                [Txn.application_args[0] == Bytes("Write"), Cond(
                    [Txn.application_args[1] == Bytes("Head"), write_head],
                    [Txn.application_args[1] == Bytes("End"), write_end],
                )]
            )]
        )
        self.TEAL_approve_condition = program

        clear_state = Seq([
            Return(Int(1))
        ])
        program = clear_state
        self.TEAL_clear_condition = program

    def compile_code(self):
        code = compileTeal(self.TEAL_approve_condition, Mode.Application)
        self.TEAL_approve_code = code
        self.TEAL_approve_program = base64.b64decode(self.contract_client.compile(self.TEAL_approve_code)['result'])
        with open(os.path.join(self.directory, 'index_approval.teal'), 'w') as f:
            f.write(code)

        code = compileTeal(self.TEAL_clear_condition, Mode.Application)
        self.TEAL_clear_code = code
        self.TEAL_clear_program = base64.b64decode(self.contract_client.compile(self.TEAL_clear_code)['result'])
        with open(os.path.join(self.directory,'index_clear_state.teal'), 'w') as f:
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

    def init_index_contract(self):
        self.read_head_app_from_local()
        self.read_end_app_from_local()

        if (self.head_app_id is None) or (self.end_app_id is None):
            self.create_head_app()
            self.create_end_app()
        else:
            app = self.indexer_client.applications(self.head_app_id)
            if 'application' in app:
                global_states = app['application']['params']['global-state']
            else:
                global_states = app['params']['global-state']
            for state in global_states:
                temp_category = base64.b64decode(state['key']).decode("utf-8")
                if temp_category in self.categories:
                    self.head_app_of_categories[temp_category] = int(base64.b64decode(state['value']['bytes']).decode("utf-8"))
            
            app = self.indexer_client.applications(self.end_app_id)
            if 'application' in app:
                global_states = app['application']['params']['global-state']
            else:
                global_states = app['params']['global-state']
            for state in global_states:
                temp_category = base64.b64decode(state['key']).decode("utf-8")
                if temp_category in self.categories:
                    self.end_app_of_categories[temp_category] = int(base64.b64decode(state['value']['bytes']).decode("utf-8"))

            if sorted(list(self.head_app_of_categories.keys())) != sorted(list(self.end_app_of_categories.keys())):
                sys.exit("Head App and End App does not match!")
    
    def read_head_app_from_local(self):  
        if not os.path.exists(os.path.join(self.directory, self.index_folder)):
            os.mkdir(os.path.join(self.directory, self.index_folder))  
           
        head_path = os.path.join(self.directory, self.index_folder, "head-app-id")
        if os.path.exists(head_path):
            with open(head_path, "r") as fp:
                self.head_app_id = int(fp.readline())
        else:
            self.head_app_id = None
    
    def read_end_app_from_local(self):  
        if not os.path.exists(os.path.join(self.directory, self.index_folder)):
            os.mkdir(os.path.join(self.directory, self.index_folder))  
           
        end_path = os.path.join(self.directory, self.index_folder, "end-app-id")
        if os.path.exists(end_path):
            with open(end_path, "r") as fp:
                self.end_app_id = int(fp.readline())
        else:
            self.end_app_id = None
        
    def write_head_app_to_local(self):
        with open(os.path.join(self.directory, self.index_folder, "head-app-id"), 'w') as fp:
            fp.write(str(self.head_app_id))

    def write_end_app_to_local(self):
        with open(os.path.join(self.directory, self.index_folder, "end-app-id"), 'w') as fp:
            fp.write(str(self.end_app_id))

    def create_head_app(self):
        creator = mnemonic.to_public_key(self.passphrase)
        on_complete = transaction.OnComplete.NoOpOC.real
        params = self.contract_client.suggested_params()
        params.flat_fee = True
        params.fee = 0.1

        global_schema = transaction.StateSchema(5, 16)
        local_schema = transaction.StateSchema(6, 6)

        app_args = [
            b'Create',
            b'Head',
        ]

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
        self.head_app_id = transaction_response['application-index']
        self.write_head_app_to_local()
        with open(os.path.join(self.directory, self.log_file), "a+") as fp:
            fp.write("Created Head app:" + str(self.head_app_id) + "\n")

    def create_end_app(self):
        creator = mnemonic.to_public_key(self.passphrase)
        on_complete = transaction.OnComplete.NoOpOC.real
        params = self.contract_client.suggested_params()
        params.flat_fee = True
        params.fee = 0.1

        global_schema = transaction.StateSchema(5, 16)
        local_schema = transaction.StateSchema(6, 6)

        app_args = [
            b'Create',
            b'End',
        ]

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
        self.end_app_id = transaction_response['application-index']
        self.write_end_app_to_local()
        with open(os.path.join(self.directory, self.log_file), "a+") as fp:
            fp.write("Created End app:" + str(self.end_app_id) + "\n")

    def write_category_head(self, app_id, input_category):
        params = self.contract_client.suggested_params()
        params.flat_fee = True
        params.fee = 0.1
        app_args = [
            b'Write',
            b'Head',
            bytes(str(input_category), "utf-8"),
            bytes(str(app_id), "utf-8"),
        ]

        txn = transaction.ApplicationNoOpTxn(self.account_public_key, params, int(self.head_app_id), app_args=app_args)
        signed_txn = txn.sign(self.account_private_key)
        tx_id = signed_txn.transaction.get_txid()
        self.contract_client.send_transactions([signed_txn])
        self.wait_for_confirmation(tx_id)

        transaction_response = self.contract_client.pending_transaction_info(tx_id)
        with open(os.path.join(self.directory, self.log_file), "a+") as fp:
            fp.write("Write head app id of category " + input_category + " to app: " + str(transaction_response['txn']['txn']['apid']) + "\n")
        self.head_app_of_categories[input_category] = int(app_id)

    def write_category_end(self, app_id, input_category):
        params = self.contract_client.suggested_params()
        params.flat_fee = True
        params.fee = 0.1
        app_args = [
            b'Write',
            b'End',
            bytes(str(input_category), "utf-8"),
            bytes(str(app_id), "utf-8"),
        ]

        txn = transaction.ApplicationNoOpTxn(self.account_public_key, params, int(self.end_app_id), app_args=app_args)
        signed_txn = txn.sign(self.account_private_key)
        tx_id = signed_txn.transaction.get_txid()
        self.contract_client.send_transactions([signed_txn])
        self.wait_for_confirmation(tx_id)

        transaction_response = self.contract_client.pending_transaction_info(tx_id)
        with open(os.path.join(self.directory, self.log_file), "a+") as fp:
            fp.write("Write end app id of category " + input_category + " to app: " + str(transaction_response['txn']['txn']['apid']) + "\n")
        self.end_app_of_categories[input_category] = int(app_id)    

    def delete_index_app(self):
        params = self.contract_client.suggested_params()
        params.flat_fee = True
        params.fee = 0.1
        app_args = [
            b'Delete',
        ]

        txn = transaction.ApplicationDeleteTxn(self.account_public_key, params, int(self.head_app_id), app_args=app_args)
        signed_txn = txn.sign(self.account_private_key)
        tx_id = signed_txn.transaction.get_txid()
        self.contract_client.send_transactions([signed_txn])
        self.wait_for_confirmation(tx_id)

        transaction_response = self.contract_client.pending_transaction_info(tx_id)
        with open(os.path.join(self.directory, self.log_file), "a+") as fp:
            fp.write("Deleted head app: " + str(transaction_response['txn']['txn']['apid']) + "\n")

        txn = transaction.ApplicationDeleteTxn(self.account_public_key, params, int(self.end_app_id), app_args=app_args)
        signed_txn = txn.sign(self.account_private_key)
        tx_id = signed_txn.transaction.get_txid()
        self.contract_client.send_transactions([signed_txn])
        self.wait_for_confirmation(tx_id)

        transaction_response = self.contract_client.pending_transaction_info(tx_id)
        with open(os.path.join(self.directory, self.log_file), "a+") as fp:
            fp.write("Deleted end app: " + str(transaction_response['txn']['txn']['apid']) + "\n")

import os
import re
import sys
import json
import base64
import time
from pyteal import *
from algosdk import mnemonic
from algosdk.v2client import algod, indexer
from algosdk.future import transaction

class ContentContract():
    def __init__(self, API_key, contract_address, passphrase):
        # contract client info
        self.API_key = API_key
        self.contract_address = contract_address
        self.passphrase = passphrase
        self.account_public_key = mnemonic.to_public_key(self.passphrase)
        self.account_private_key = mnemonic.to_private_key(self.passphrase)
        # the lastest created app id
        self.max_client_per_app = 12
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
            self.contract_address, 
            headers=purestake_token)
        self.indexer_client = indexer.IndexerClient(
            self.API_key, 
            self.contract_address, 
            headers=purestake_token)
        self.log_file = None
        self.search_file = None
        self.verify_file = None
        self.directory = None

    def create_code(self):
        create_content = Seq([
            App.globalPut(Bytes("Hash"), Sha256(Bytes("None"))),
            App.globalPut(Bytes("NextApp"), Bytes("None")),
            App.globalPut(Bytes("Category"), Txn.application_args[2]),
            App.globalPut(Bytes("key 01"), Bytes("None")),
            App.globalPut(Bytes("key 02"), Bytes("None")),
            App.globalPut(Bytes("key 03"), Bytes("None")),
            App.globalPut(Bytes("key 04"), Bytes("None")),
            App.globalPut(Bytes("key 05"), Bytes("None")),
            App.globalPut(Bytes("key 06"), Bytes("None")),
            App.globalPut(Bytes("key 07"), Bytes("None")),
            App.globalPut(Bytes("key 08"), Bytes("None")),
            App.globalPut(Bytes("key 09"), Bytes("None")),
            App.globalPut(Bytes("key 10"), Bytes("None")),
            App.globalPut(Bytes("key 11"), Bytes("None")),
            App.globalPut(Bytes("key 12"), Bytes("None")),
            Return(Int(1))
        ])

        opt_in = Seq([
            App.globalPut(Txn.application_args[2], Txn.application_args[3]),
            App.globalPut(Bytes("Hash"), Sha256(Concat(
                App.globalGet(Bytes("Hash")),
                Txn.application_args[4],
                Txn.application_args[5]
            ))),
            Seq([
                App.localPut(Int(0), Bytes("OptedAppId"), Txn.application_args[4]),
                App.localPut(Int(0), Bytes("AdvertiserUrl"), Txn.application_args[5]),
                Return(Int(1))
            ]),
            Return(Int(1))
        ])

        update_hash = Seq([
            App.globalPut(Bytes("Hash"), Txn.application_args[1]),
            Return(Int(1))
        ])

        chain = Seq([
            App.globalPut(Bytes("NextApp"), Txn.application_args[1]),
            Return(Int(1))
        ])

        close_out = Seq([
            App.localDel(Int(0), Bytes("OptedAppId")),
            App.localDel(Int(0), Bytes("AdvertiserUrl")),
            Return(Int(1))
        ])

        is_creator = Txn.sender() == App.globalGet(Bytes("Creator"))

        program = Cond(
            # if Txn.application _id() == 0 then it is the creation of this application.
            [Txn.application_id() == Int(0), Cond(
                [Txn.application_args[1] == Bytes("Content"), create_content]
            )],
            [Txn.on_completion() == OnComplete.DeleteApplication, Return(is_creator)],
            [Txn.on_completion() == OnComplete.OptIn, opt_in],
            [Txn.on_completion() == OnComplete.CloseOut, close_out],
            [Txn.on_completion() == OnComplete.NoOp, Cond(
                [Txn.application_args[0] == Bytes("Chain"), chain],
                [Txn.application_args[0] == Bytes("Hash"), update_hash],
            )]
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
    
    def content_app_is_full(self, app_id):
        app = self.indexer_client.applications(app_id)
        if 'application' in app:
            global_states = app['application']['params']['global-state']
        else:
            global_states = app['params']['global-state']
        for state in global_states:
            if base64.b64decode(state['key']).decode("utf-8") == "key 12":
                if base64.b64decode(state['value']['bytes']).decode("utf-8") == "None":
                    return False
            if base64.b64decode(state['key']).decode("utf-8") == "Hash":
                hash_result = base64.b64decode(state['value']['bytes'])
        return hash_result

    def create_content_app(self, input_category):
        on_complete = transaction.OnComplete.NoOpOC.real
        params = self.contract_client.suggested_params()
        params.flat_fee = True
        params.fee = 0.1

        global_schema = transaction.StateSchema(5, 16)
        local_schema = transaction.StateSchema(6, 6)

        app_args = [
            b'Create',
            b'Content',
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
        return int(curr_app_id)
            
    def opt_in_app(self, opt_in_advertiser, app_id):
        app = self.indexer_client.applications(app_id)
        if 'application' in app:
            global_states = app['application']['params']['global-state']
        else:
            global_states = app['params']['global-state']
        keys = []
        for state in global_states:
            if (base64.b64decode(state['key']).decode("utf-8") not in ["NextApp", "Category", "Hash"]) and (base64.b64decode(state['value']['bytes']).decode("utf-8") != "None"):
                key_index = int(base64.b64decode(state['key']).decode("utf-8")[-2:])
                keys.append(key_index)
        next_key_index = ('0' + str(len(keys) + 1))[-2:]

        params = self.contract_client.suggested_params()
        params.flat_fee = True
        params.fee = 0.1
        app_args = [
            b'Opt-in',
            b'Content',
            bytes("key " + next_key_index, 'utf-8'),
            bytes(str(opt_in_advertiser.account_public_key), 'utf-8'),
            bytes(str(app_id), 'utf-8'),
            bytes("Url: " + str(opt_in_advertiser.account_public_key), 'utf-8'),
        ]

        txn = transaction.ApplicationOptInTxn(opt_in_advertiser.account_public_key, params, int(app_id), app_args=app_args)
        signed_txn = txn.sign(opt_in_advertiser.account_private_key)
        tx_id = signed_txn.transaction.get_txid()
        self.contract_client.send_transactions([signed_txn])
        self.wait_for_confirmation(tx_id)

        transaction_response = self.contract_client.pending_transaction_info(tx_id)
        with open(os.path.join(self.directory, self.log_file), "a+") as fp:
            fp.write("Opted-in and write to app: " + str(transaction_response['txn']['txn']['apid']) + "\n")
            fp.write("Write to key index: " + "key " + next_key_index + "\n")

        with open(os.path.join(self.directory, self.verify_file), "a+") as fp:
            fp.write(opt_in_advertiser.category + "\n")
            fp.write(str(app_id) + "Url: " + str(opt_in_advertiser.account_public_key) + "\n")

    def write_category_hash(self, prev_hash, app_id, input_category):
        params = self.contract_client.suggested_params()
        params.flat_fee = True
        params.fee = 0.1
        app_args = [
            b'Hash',
            prev_hash,
        ]

        txn = transaction.ApplicationNoOpTxn(self.account_public_key, params, int(app_id), app_args=app_args)
        signed_txn = txn.sign(self.account_private_key)
        tx_id = signed_txn.transaction.get_txid()
        self.contract_client.send_transactions([signed_txn])
        self.wait_for_confirmation(tx_id)

        transaction_response = self.contract_client.pending_transaction_info(tx_id)
        with open(os.path.join(self.directory, self.log_file), "a+") as fp:
            fp.write("Write hash of category " + input_category + " to app: " + str(transaction_response['txn']['txn']['apid']) + "\n")

    def chain_content_app(self, new_app_id, end_app_id):
        params = self.contract_client.suggested_params()
        params.flat_fee = True
        params.fee = 0.1
        app_args = [
            b'Chain',
            bytes(str(new_app_id), 'utf-8')
        ]
        
        txn = transaction.ApplicationNoOpTxn(self.account_public_key, params, int(end_app_id), app_args=app_args)
        signed_txn = txn.sign(self.account_private_key)
        tx_id = signed_txn.transaction.get_txid()
        self.contract_client.send_transactions([signed_txn])
        self.wait_for_confirmation(tx_id)

        transaction_response = self.contract_client.pending_transaction_info(tx_id)
        with open(os.path.join(self.directory, self.log_file), "a+") as fp:
            fp.write("Chain to app: " + str(transaction_response['txn']['txn']['apid']) + "\n")

    def close_out_app(self, close_out_advertiser, app_id):
        params = self.contract_client.suggested_params()
        params.flat_fee = True
        params.fee = 0.1
        app_args = [
            b'Close_Out',
            bytes(close_out_advertiser.category, 'utf-8'),
        ]
            
        txn = transaction.ApplicationCloseOutTxn(close_out_advertiser.account_public_key, params, app_id, app_args=app_args)
        signed_txn = txn.sign(close_out_advertiser.account_private_key)
        tx_id = signed_txn.transaction.get_txid()
        self.contract_client.send_transactions([signed_txn])
        self.wait_for_confirmation(tx_id)

        transaction_response = self.contract_client.pending_transaction_info(tx_id)
        with open(os.path.join(self.directory, self.log_file), "a+") as fp:
            fp.write("Closed out app: " + str(transaction_response['txn']['txn']['apid']) + "\n")
            
    def clear_app(self, clear_advertiser, app_id):
        params = self.contract_client.suggested_params()
        params.flat_fee = True
        params.fee = 0.1
        app_args = [
            b'Clear',
            bytes(clear_advertiser.category, 'utf-8'),
        ]

        txn = transaction.ApplicationClearStateTxn(clear_advertiser.account_public_key, params, app_id, app_args=app_args)
        signed_txn = txn.sign(clear_advertiser.account_private_key)
        tx_id = signed_txn.transaction.get_txid()
        self.contract_client.send_transactions([signed_txn])
        self.wait_for_confirmation(tx_id)

        transaction_response = self.contract_client.pending_transaction_info(tx_id)
        with open(os.path.join(self.directory, self.log_file), "a+") as fp:
            fp.write("Cleared app: " + str(transaction_response['txn']['txn']['apid']) + "\n")    

    def delete_content_app(self, app_id):
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
    
if __name__ == "__main__":
    contract_client = ContentContract(
        API_key = "afETOBfGPz3JfzIY3B1VG48kIGsMrlxO67VdEeOC",
        contract_address = "https://testnet-algorand.api.purestake.io/ps2",
        passphrase = "guilt ensure again delay cream rude detect blanket athlete flock cram return eager skate behind scene chase action stock mask cricket tail pistol above ankle")
    contract_client.create_code()
    contract_client.compile_code()
    temp_id = contract_client.create_content_app("Category1")
    contract_client.delete_content_app(temp_id)
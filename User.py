import os
from algosdk import account
from algosdk import mnemonic
from algosdk.v2client import algod, indexer

class User():
    def __init__(self, API_key, algod_address, index_address, passphrase):
        self.API_key = API_key
        self.algod_address = algod_address
        self.index_address = index_address
        self.passphrase = passphrase
        self.log_file = "debug.log"
        self.account_public_key = None
        self.account_private_key = None
        self.algod_client = None
        self.indexer_client = None
        
    def login(self):
        purestake_token = {'X-API-key': self.API_key}
        self.account_private_key = mnemonic.to_private_key(self.passphrase)
        self.account_public_key = mnemonic.to_public_key(self.passphrase)
        self.algod_client = algod.AlgodClient(self.API_key, self.algod_address, headers=purestake_token)
        self.indexer_client = indexer.IndexerClient(self.API_key, self.index_address, headers=purestake_token)
        with open(os.path.join(os.path.dirname(__file__), self.log_file), "a+") as fp:
            fp.write("The user logins into account " + str(self.account_public_key) + "\n")
        
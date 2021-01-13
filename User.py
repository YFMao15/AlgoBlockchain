import json
import base64
from pyteal import *
from Contract import *
from algosdk import encoding
from algosdk import account
from algosdk import mnemonic
from algosdk.v2client import algod
from algosdk.future import transaction


class User():
    def __init__(self, API_key, user_address, passphrase):
        self.API_key = API_key
        self.user_address = user_address
        self.passphrase = passphrase
        self.log_file = "test.log"
        self.account_public_key = None
        self.account_private_key = None
        self.indexer_client = None
        self.user_client = None

    def login(self):
        purestake_token = {'X-API-key': self.API_key}
        self.account_private_key = mnemonic.to_private_key(self.passphrase)
        self.account_public_key = mnemonic.to_public_key(self.passphrase)
        self.indexer_client = indexer.IndexerClient(self.API_key, self.user_address, headers=purestake_token)
        self.user_client =  algod.AlgodClient(self.API_key, self.user_address, headers=purestake_token)
        self.log_file = "test.log"
        with open(os.path.join(os.path.dirname(__file__), self.log_file), "a+") as fp:
            fp.write("The user logins into account " + str(self.account_public_key) + "\n")
        
if __name__ == "__main__":
    user1 = User(
        API_key = "afETOBfGPz3JfzIY3B1VG48kIGsMrlxO67VdEeOC",
        user_address = "https://testnet-algorand.api.purestake.io/idx2",
        passphrase = "fine hope logic together enough biology sock delay all suit badge awake suggest cook spread grab airport moment isolate fold immense busy wedding abstract rail")
    user1.login()
import os
import json
import base64
from pyteal import *
from algosdk import encoding
from algosdk import account
from algosdk import mnemonic
from algosdk.v2client import algod, indexer
from algosdk.future import transaction

class Advertiser():
    def __init__(self, API_key, algod_address, index_address, passphrase):
        # Init params
        self.API_key = API_key
        self.algod_address = algod_address
        self.index_address = index_address
        self.passphrase = passphrase
        self.log_file = "debug.log"
        self.account_public_key = None
        self.account_private_key = None
        self.algod_client = None
        self.indexer_client = None
        self.category = None

    def login(self):
        purestake_token = {'X-API-key': self.API_key}
        self.account_private_key = mnemonic.to_private_key(self.passphrase)
        self.account_public_key = mnemonic.to_public_key(self.passphrase)
        self.algod_client = algod.AlgodClient(self.API_key, self.algod_address, headers=purestake_token)
        self.indexer_client = indexer.IndexerClient(self.API_key, self.index_address, headers=purestake_token)
        with open(os.path.join(os.path.dirname(__file__), self.log_file), "a+") as fp:
            fp.write("The advertiser logins into account " + str(self.account_public_key) + "\n")

    def assign_category(self, category):
        self.category = category
        with open(os.path.join(os.path.dirname(__file__), self.log_file), "a+") as fp:
            fp.write("The advertiser account is included in " + category + " category\n")

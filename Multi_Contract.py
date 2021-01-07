import os
import json
import base64
import re
from pyteal import *
from algosdk import mnemonic
from algosdk.v2client import algod, indexer
from algosdk.future import transaction
from Contract import *

class Multi_Contract():
    def __init__(self, contract_list):
        self.contract_list = contract_list
        self.max_client_per_account = 10

    def create_list(self):
        for count in range(len(self.contract_list)):
            contract = self.contract_list[count]
            if contract.head_app_id == "None":
                for _ in range(self.max_client_per_account):
                    contract.create_contract_app()
                    contract.chain_app(contract.app_id)
            
    def add_adv_into_list(self, advertiser):
        for contract in self.contract_list:
            result = contract.search_blank(advertiser.category)
            if result is None:
                continue
            else:
                contract.add_adv_into_app(advertiser)
                break

    def external_search_list(self, user, category_input):
        results = []
        for contract in self.contract_list:
            temp_result = contract.external_search(user, category_input)
            results += temp_result
        print("The searching results from multi-contracts of category " + str(category_input) +" are: ")
        print(results)



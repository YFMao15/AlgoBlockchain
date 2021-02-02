import os
import re
import json
import base64
import time

from pyteal import *
from algosdk import mnemonic
from Crypto.Hash import SHA256
from algosdk.v2client import algod, indexer
from algosdk.future import transaction
from IndexContract import *
from ContentContract import *

class MultiContract():
    def __init__(self, init):
        self.log_file = "debug.log"
        self.search_file = "search.log"
        self.verify_file = "verify.log"
        self.directory = os.path.dirname(__file__)
        self.index_account = None
        self.content_account = None
        self.last_app_ids = {}

        if init is True:
            with open(os.path.join(self.directory, self.verify_file), "a+") as fp:
                fp.write("None" + "\n")

    def add_index_account(self, index_account):
        self.index_account = index_account
        self.index_account.log_file = self.log_file
        self.index_account.index_folder = "index"
        self.index_account.directory = self.directory

    def add_content_account(self, content_account):
        self.content_account = content_account
        self.content_account.log_file = self.log_file
        self.content_account.search_file = self.search_file
        self.content_account.verify_file = self.verify_file
        self.content_account.directory = self.directory
        self.content_account.create_code()
        self.content_account.compile_code()

        for x in range(1, 11):
            idx = str(x)
            category = "Category" + idx
            if category not in self.index_account.head_app_of_categories:
                temp_app_id = content_account.create_content_app(category)
                self.index_account.write_category_head(temp_app_id, category)
                self.index_account.write_category_end(temp_app_id, category)
                self.last_app_ids[category] = temp_app_id
            else:
                temp_app_id = self.content_account.create_content_app(category)
                self.content_account.chain_content_app(int(temp_app_id), int(self.last_app_ids[category]))
                self.last_app_ids[category] = temp_app_id

    def add_adv_into_content_apps(self, advertiser):
        if advertiser.category not in self.index_account.categories:
            sys.exit("Wrong advertiser category!")

        end_app_id = self.index_account.end_app_of_categories[advertiser.category]
        result = self.content_account.content_app_is_full(end_app_id)
        if result is False:
            pass
        else:
            app = self.index_account.indexer_client.applications(end_app_id)
            if 'application' in app:
                global_states = app['application']['params']['global-state']
            else:
                global_states = app['params']['global-state']
            for state in global_states:
                if base64.b64decode(state['key']).decode("utf-8") == "NextApp":
                    next_app_id = base64.b64decode(state['value']['bytes']).decode("utf-8")
            self.index_account.write_category_end(int(next_app_id), advertiser.category)  
            self.content_account.write_category_hash(result, int(next_app_id), advertiser.category)
                   
        end_app_id = self.index_account.end_app_of_categories[advertiser.category]
        self.content_account.opt_in_app(advertiser, end_app_id)
        
    def full_search(self, user, input_category):
        if input_category not in self.index_account.categories:
            sys.exit("Wrong search input!")

        results = []
        prev_app_id = self.index_account.head_app_of_categories[input_category]
        next_app_id = int(prev_app_id) + 0

        while next_app_id != "None":
            time.sleep(0.2)
            prev_app_id = int(next_app_id) + 0
            app = user.indexer_client.applications(int(prev_app_id))
            if 'application' in app:
                global_states = app['application']['params']['global-state']
            else:
                global_states = app['params']['global-state']
            
            for state in global_states:
                if base64.b64decode(state['key']) == b'NextApp':
                    next_app_id = base64.b64decode(state['value']['bytes']).decode('utf-8')
                elif base64.b64decode(state['key']) not in [b'NextApp', b'Category', b'Hash']:
                    time.sleep(0.07)
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
        
        with open(os.path.join(self.directory, self.search_file), "a+") as fp:
            for result in results:
                fp.write(str(result))
                fp.write("\n")

    def verify_hash(self, user, input_category):
        if input_category not in self.index_account.categories:
            sys.exit("Wrong search input!")

        with open(os.path.join(self.directory, self.verify_file), "r") as fp:
            contents = fp.readlines()
            
        local_hash = SHA256.new()
        local_hash.update(bytes("None", 'utf-8'))
        local_digest = local_hash.digest()

        idx = 1
        while idx < len(contents):
            if (idx % 2 == 1) and (contents[idx][:-1] != input_category):
                idx += 1
            elif idx % 2 == 0:
                content = b""
                content += local_digest
                content += bytes(contents[idx][:-1], 'utf-8')
                
                local_hash = SHA256.new()
                local_hash.update(content)
                local_digest = local_hash.digest()
            idx += 1

        end_app_id = self.index_account.end_app_of_categories[input_category]
        app = user.indexer_client.applications(int(end_app_id))
        if 'application' in app:
            global_states = app['application']['params']['global-state']
        else:
            global_states = app['params']['global-state']
            
        for state in global_states:
            if base64.b64decode(state['key']) == b'Hash':
                online_digest = base64.b64decode(state['value']['bytes']).hex()
                break
        
        print(local_digest.hex())
        print(online_digest)
        assert(local_digest.hex() == online_digest)
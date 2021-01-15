import time
import random
from User import *
from Advertiser import *
from Contract import *
from Multi_Contract import *

if __name__ == "__main__":
    API_key = "afETOBfGPz3JfzIY3B1VG48kIGsMrlxO67VdEeOC"
    address = "https://testnet-algorand.api.purestake.io/ps2"
    with open(os.path.join(os.path.dirname(__file__), "advertiser_info.log"), "r") as fp:
        advertiser_passphrases = fp.readlines()
    with open(os.path.join(os.path.dirname(__file__), "contract_info.log"), "r") as fp:
        contract_passphrases = fp.readlines()

    adv_count = len(advertiser_passphrases)
    contract_count = len(contract_passphrases)

    contract_list = []
    start = time.time()
    sleep = 5
    for passphrase in contract_passphrases:
        temp_contract = Contract(API_key, address, passphrase[:-1])
        temp_contract.read_head_app_id()
        temp_contract.create_code()
        temp_contract.compile_code()
        contract_list.append(temp_contract)

    multi_contract = Multi_Contract(contract_list)
    multi_contract.create_list()

    temp_info = account.generate_account()
    user = User(API_key, address, mnemonic.from_private_key(temp_info[0]))
    user.login()
        
    start = time.time()
    multi_contract.external_search_list(user, "Category1")
    with open(os.path.join(os.path.dirname(__file__), "test.log"), "a+") as fp:
        fp.write("The time cost of searching is: " + str(time.time() - start) + "\n")

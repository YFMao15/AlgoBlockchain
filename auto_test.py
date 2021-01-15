import time
import random
from User import *
from Advertiser import *
from Contract import *
from Multi_Contract import *


def send_money(sender, receiver):
    def wait_for_confirmation(algodclient, txid):
        last_round = algodclient.status().get('last-round')
        txinfo = algodclient.pending_transaction_info(txid)
        while not (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0):
            last_round += 1
            algodclient.status_after_block(last_round)
            txinfo = algodclient.pending_transaction_info(txid)
        with open(os.path.join(os.path.dirname(__file__), "test.log"), "a+") as fp:
            fp.write("Money transferring transaction {} confirmed in round {}.".format(txid, txinfo.get('confirmed-round')) + "\n")

    params = sender.algod_client.suggested_params()
    # 20 algorands
    send_amount = 20000000

    txn = transaction.PaymentTxn(sender.account_public_key, params, receiver.account_public_key, send_amount)
    signed_txn = txn.sign(sender.account_private_key)
    sender.algod_client.send_transactions([signed_txn])
    wait_for_confirmation(sender.algod_client, txid = signed_txn.transaction.get_txid())

if __name__ == "__main__":
    API_key = "afETOBfGPz3JfzIY3B1VG48kIGsMrlxO67VdEeOC"
    address = "https://testnet-algorand.api.purestake.io/ps2"
    init = False

    dir_content = os.listdir(os.path.dirname(__file__))
    if ("test.log" not in dir_content) or ("advertiser_info.log" not in dir_content) and ("contract_info.log" not in dir_content):
        init = True
        for filename in dir_content:
            if (filename == "contract-app"):
                app_content = os.listdir(os.path.join(os.path.dirname(__file__), "contract-app"))
                for app in app_content:
                    os.remove(os.path.join(os.path.dirname(__file__), "contract-app", app))
                os.rmdir(os.path.join(os.path.dirname(__file__), "contract-app"))
            if (len(filename.split(".")) == 2) and (filename.split(".")[1] == "log"):
                os.remove(os.path.join(os.path.dirname(__file__), filename))
        
    
    temp_info = account.generate_account()
    user = User(API_key, address, mnemonic.from_private_key(temp_info[0]))
    user.login()

    banker = Advertiser(
        API_key = "afETOBfGPz3JfzIY3B1VG48kIGsMrlxO67VdEeOC",
        advertiser_address = "https://testnet-algorand.api.purestake.io/ps2",
        passphrase = "code thrive mouse code badge example pride stereo sell viable adjust planet text close erupt embrace nature upon february weekend humble surprise shrug absorb faint")
    banker.login()

    # restart by deleting all previous records above
    if init:
        contract_num = 10
        contract_list = []
        start = time.time()
        sleep = 5
        for _ in range(contract_num):
            temp_info = account.generate_account()
            temp_contract = Advertiser(API_key, address, mnemonic.from_private_key(temp_info[0]))
            temp_contract.login()
            send_money(banker, temp_contract)
            temp_contract = Contract(API_key, address, mnemonic.from_private_key(temp_info[0]))
            temp_contract.read_head_app_id()
            temp_contract.create_code()
            temp_contract.compile_code()
            contract_list.append(temp_contract)
            time.sleep(sleep)
        multi_contract = Multi_Contract(contract_list)
        multi_contract.create_list()
        with open(os.path.join(os.path.dirname(__file__), "test.log"), "a+") as fp:
            fp.write("The time cost of initializing " + str(len(contract_list)) + " contracts is: " + str(time.time() - start - sleep * contract_num) + "\n")
        with open(os.path.join(os.path.dirname(__file__), "contract_info.log"), "w+") as fp:
            for contract in contract_list:
                fp.write(contract.passphrase)
                fp.write("\n")

        adv_num = 100
        adv_index_list = list(range(1, 1 + adv_num))
        random.shuffle(adv_index_list)
        start = time.time()
        for idx in range(adv_num):
            temp_info = account.generate_account()
            temp_adv = Advertiser(API_key, address, mnemonic.from_private_key(temp_info[0]))
            temp_adv.login()
            temp_adv.assign_category("Category" + str(adv_index_list[idx] % 12))
            send_money(banker, temp_adv)
            multi_contract.add_adv_into_list(temp_adv)
            with open(os.path.join(os.path.dirname(__file__), "advertiser_info.log"), "a+") as fp:
                fp.write(temp_adv.passphrase)
                fp.write("\n")
            with open(os.path.join(os.path.dirname(__file__), "test.log"), "a+") as fp:
                fp.write("The time cost of opting in " + str(idx+1) + " advertisers is: " + str(time.time() - start - sleep * adv_num) + "\n")
            time.sleep(sleep)

        start = time.time()
        multi_contract.external_search_list(user, "Category1")
        with open(os.path.join(os.path.dirname(__file__), "test.log"), "a+") as fp:
            fp.write("The time cost of searching is: " + str(time.time() - start) + "\n")

    # not restarted, continuing from the last running
    else:
        with open(os.path.join(os.path.dirname(__file__), "advertiser_info.log"), "r") as fp:
            advertiser_passphrases = fp.readlines()
        with open(os.path.join(os.path.dirname(__file__), "contract_info.log"), "r") as fp:
            contract_passphrases = fp.readlines()

        adv_count = len(advertiser_passphrases)
        contract_count = len(contract_passphrases)

        if adv_count < (contract_count - 5) * 120:
            contract_num = 0
        else:
            contract_num = 5
        contract_list = []
        start = time.time()
        sleep = 5
        for passphrase in contract_passphrases:
            temp_contract = Contract(API_key, address, passphrase[:-1])
            temp_contract.read_head_app_id()
            temp_contract.create_code()
            temp_contract.compile_code()
            contract_list.append(temp_contract)

        for _ in range(contract_num):
            temp_info = account.generate_account()
            temp_contract = Advertiser(API_key, address, mnemonic.from_private_key(temp_info[0]))
            temp_contract.login()
            send_money(banker, temp_contract)
            temp_contract = Contract(API_key, address, mnemonic.from_private_key(temp_info[0]))
            temp_contract.read_head_app_id()
            temp_contract.create_code()
            temp_contract.compile_code()
            contract_list.append(temp_contract)
            time.sleep(sleep)
        multi_contract = Multi_Contract(contract_list)
        multi_contract.create_list()
        if contract_num > 0:
            with open(os.path.join(os.path.dirname(__file__), "test.log"), "a+") as fp:
                fp.write("The time cost of adding " + str(contract_num) + " contracts is: " + str(time.time() - start - sleep * contract_num) + "\n")
            with open(os.path.join(os.path.dirname(__file__), "contract_info.log"), "w+") as fp:
                for contract in contract_list:
                    fp.write(contract.passphrase)
                    fp.write("\n")
        
        start = time.time()
        multi_contract.external_search_list(user, "Category1")
        with open(os.path.join(os.path.dirname(__file__), "test.log"), "a+") as fp:
            fp.write("The time cost of searching is: " + str(time.time() - start) + "\n")

        adv_num = 50
        adv_index_list = list(range(1 + adv_count, 1 + adv_num + adv_count))
        random.shuffle(adv_index_list)
        start = time.time()
        for idx in range(adv_num):
            temp_info = account.generate_account()
            temp_adv = Advertiser(API_key, address, mnemonic.from_private_key(temp_info[0]))
            temp_adv.login()
            temp_adv.assign_category("Category" + str(adv_index_list[idx] % 12))
            send_money(banker, temp_adv)
            multi_contract.add_adv_into_list(temp_adv)
            with open(os.path.join(os.path.dirname(__file__), "advertiser_info.log"), "a+") as fp:
                fp.write(temp_adv.passphrase)
                fp.write("\n")
            with open(os.path.join(os.path.dirname(__file__), "test.log"), "a+") as fp:
                fp.write("The time cost of opting in" + str(idx+1) + " advertisers is: " + str(time.time() - start - sleep * adv_num) + "\n")
            time.sleep(sleep)

        start = time.time()
        multi_contract.external_search_list(user, "Category1")
        with open(os.path.join(os.path.dirname(__file__), "test.log"), "a+") as fp:
            fp.write("The time cost of searching is: " + str(time.time() - start) + "\n")



    

    
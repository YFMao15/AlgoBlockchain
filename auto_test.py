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

    if os.path.exists(os.path.join(os.path.dirname(__file__), "test.log")):
        dir_content = os.listdir(os.path.dirname(__file__))
        os.remove(os.path.join(os.path.dirname(__file__), "test.log"))
        for filename in dir_content:
            if (len(filename.split(".")) == 2) and (filename.split(".")[1] == "txt"):
                os.remove(os.path.join(os.path.dirname(__file__), filename))
    
    temp_info = account.generate_account()
    user = User(API_key, address, mnemonic.from_private_key(temp_info[0]))
    user.login()

    banker = Advertiser(
        API_key = "afETOBfGPz3JfzIY3B1VG48kIGsMrlxO67VdEeOC",
        advertiser_address = "https://testnet-algorand.api.purestake.io/ps2",
        passphrase = "code thrive mouse code badge example pride stereo sell viable adjust planet text close erupt embrace nature upon february weekend humble surprise shrug absorb faint")
    banker.login()

    contract_num = 10
    contract_list = []
    start = time.time()
    sleep = 10
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

    print("Contract init completed")
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
        time.sleep(sleep)
    with open(os.path.join(os.path.dirname(__file__), "test.log"), "a+") as fp:
        fp.write("The time cost of opting in" + str(adv_num) + " advertisers is: " + str(time.time() - start - sleep * adv_num) + "\n")

    start = time.time()
    multi_contract.external_search_list(user, "Category1")
    with open(os.path.join(os.path.dirname(__file__), "test.log"), "a+") as fp:
        fp.write("The time cost of searching is: " + str(time.time() - start) + "\n")

    with open(os.path.join(os.path.dirname(__file__), "contract_info.log"), "a+") as fp:
        for contract in contract_list:
            fp.write(contract.passphrase)
            fp.write("\n")
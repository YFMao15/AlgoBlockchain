import os
import time
import random
from User import *
from Advertiser import *
from Contract import *


def send_money(sender, receiver):
    def wait_for_confirmation(algodclient, txid):
        last_round = algodclient.status().get('last-round')
        txinfo = algodclient.pending_transaction_info(txid)
        while not (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0):
            last_round += 1
            algodclient.status_after_block(last_round)
            txinfo = algodclient.pending_transaction_info(txid)
        with open(os.path.join(os.path.dirname(__file__), "debug.log"), "a+") as fp:
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
    algod_address = "https://testnet-algorand.api.purestake.io/ps2"
    index_address = "https://testnet-algorand.api.purestake.io/idx2"

    """
    CHANGE PARAMS HERE TO LAUNCH DIFFERENT MODE
    """
    init = True
    cate_num = 1
    adv_num = 10

    if init is True:
        if os.path.exists(os.path.join(os.path.dirname(__file__), "debug.log")):
            os.remove(os.path.join(os.path.dirname(__file__), "debug.log"))
        if os.path.exists(os.path.join(os.path.dirname(__file__), "account.txt")):
            os.remove(os.path.join(os.path.dirname(__file__), "account.txt"))

    if os.path.exists(os.path.join(os.path.dirname(__file__), "verify.log")):
            os.remove(os.path.join(os.path.dirname(__file__), "verify.log"))
    if os.path.exists(os.path.join(os.path.dirname(__file__), "search.log")):
        os.remove(os.path.join(os.path.dirname(__file__), "search.log"))

    temp_info = account.generate_account()
    user = User(API_key, algod_address, index_address, mnemonic.from_private_key(temp_info[0]))
    user.login()

    banker = Advertiser(
        API_key = "afETOBfGPz3JfzIY3B1VG48kIGsMrlxO67VdEeOC",
        algod_address = algod_address,
        index_address = index_address,
        passphrase = "code thrive mouse code badge example pride stereo sell viable adjust planet text close erupt embrace nature upon february weekend humble surprise shrug absorb faint")
    banker.login()

    print("Building contract app...\n")
    if init is True:
        content_info = mnemonic.from_private_key(account.generate_account()[0])
        temp = Advertiser(API_key, algod_address, index_address, content_info)
        temp.login()
        send_money(banker, temp)
        contract = Contract(API_key, algod_address, index_address, content_info)
        contract.create_code()
        contract.compile_code()
        contract.init_content_contract(cate_num)
        with open(os.path.join(os.path.dirname(__file__), "account.txt"), "w") as fp:
            fp.write(content_info)
    else: 
        with open(os.path.join(os.path.dirname(__file__), "account.txt"), "r") as fp:
            content_info = fp.readline()
        contract = Contract(API_key, algod_address, index_address, content_info)
        contract.create_code()
        contract.compile_code()
    # print("Contract mneumonic passphrase: ")
    # print(content_info)
    print("Contract application building complete\n")

    print("Adding advertisers...\n")
    start = time.time()
    for count in range(1, 1 + cate_num):
        for _ in range(adv_num):
            info = account.generate_account()
            adv = Advertiser(API_key, algod_address, index_address, mnemonic.from_private_key(info[0]))
            adv.login()
            adv.assign_category("Category" + str(count))
            send_money(banker, adv)
            contract.opt_in_app(adv)
        print("Category" + str(count) + " opted-in\n")
    with open(os.path.join(contract.directory, contract.log_file), "a+") as fp:
        fp.write("The time cost of opting in " + str(cate_num * adv_num) + " advertisers in each category is: " + str(time.time() - start) + "\n")
    print("Advertiser opting-in complete\n")
    time.sleep(10)
    
    print("Testing searching capability of smart contract...\n")
    search_category = "Category1"
    start = time.time()
    contract.full_search(user, search_category)
    with open(os.path.join(contract.directory, contract.log_file), "a+") as fp:
        fp.write("The time cost of search " + search_category + " is: " + str(time.time() - start) + "\n")

    time.sleep(3)
    start = time.time()
    contract.create_hash_local_file(user)
    with open(os.path.join(contract.directory, contract.log_file), "a+") as fp:
        fp.write("The time cost of hash local file creation is: " + str(time.time() - start) + "\n")

    start = time.time()
    local_hexdigest = contract.compute_local_hash(user, "Category1")
    with open(os.path.join(contract.directory, contract.log_file), "a+") as fp:
        fp.write("The time cost of local hash computation " + search_category + " is: " + str(time.time() - start) + "\n")

    start = time.time()
    online_hexdigest = contract.search_hash(user, "Category1")
    with open(os.path.join(contract.directory, contract.log_file), "a+") as fp:
        fp.write("The time cost of on-chain hash searching " + search_category + " is: " + str(time.time() - start) + "\n")
        
    print("The locally computed hash value is : " + local_hexdigest)
    print("The hash value recorded in app is : " + online_hexdigest)
    assert(local_hexdigest == online_hexdigest)
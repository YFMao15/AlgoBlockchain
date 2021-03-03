import os
import time
import random
from User import *
from Advertiser import *
from Contract import *
from collections import defaultdict

def send_money(sender, receiver, send_amount):
    def wait_for_confirmation(algodclient, txid):
        last_round = algodclient.status().get('last-round')
        txinfo = algodclient.pending_transaction_info(txid)
        while not (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0):
            last_round += 1
            algodclient.status_after_block(last_round)
            txinfo = algodclient.pending_transaction_info(txid)
        with open(os.path.join(os.path.dirname(__file__), "debug.log"), "a+") as fp:
            fp.write("Money transferring transaction {} confirmed in round {}.".format(txid, txinfo.get('confirmed-round')) + "\n")
        return True

    params = sender.algod_client.suggested_params()
    received = False
    while (not received):
        try:
            txn = transaction.PaymentTxn(sender.account_public_key, params, receiver.account_public_key, send_amount)
            signed_txn = txn.sign(sender.account_private_key)
            sender.algod_client.send_transactions([signed_txn])
            received = wait_for_confirmation(sender.algod_client, txid = signed_txn.transaction.get_txid())
        except:
            pass
    wait_for_confirmation(sender.algod_client, txid = signed_txn.transaction.get_txid())

def test_main(init, set_num, cate_num, adv_nums):
    API_key = "CdYVr07ErYa3VNessIks1aPcmlRYPjfZ34KYF7TF"
    algod_address = "https://testnet-algorand.api.purestake.io/ps2"
    index_address = "https://testnet-algorand.api.purestake.io/idx2"

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

    if init == True:
        print("Building contract app...\n")
        content_info = mnemonic.from_private_key(account.generate_account()[0])
        temp = Advertiser(API_key, algod_address, index_address, content_info)
        temp.login()
        send_money(banker, temp, 15000000)
        contract = Contract(API_key, algod_address, index_address, content_info)
        contract.create_code()
        contract.compile_code()
        contract.init_contract(cate_num)
        # distinguish the testing results of different params
        contract.log_file = "debug_adv_set_" + str(set_num) + "_cate_" + str(cate_num) + ".log"
        with open(os.path.join(os.path.dirname(__file__), "account_cate_" + str(cate_num) + "_set_" + str(set_num) + ".txt"), "w") as fp:
            fp.write(content_info)
        print("Contract application building complete\n")

        print("Adding advertisers...\n")
        adv_list = defaultdict(list)
        
        for idx in range(cate_num):
            for _ in range(adv_nums[idx]):
                info = account.generate_account()
                adv = Advertiser(API_key, algod_address, index_address, mnemonic.from_private_key(info[0]))
                adv.login()
                input_categories = ["Category" + str(idx + 1)]
                adv_list["Category" + str(idx + 1)].append(adv)
                adv.assign_category(input_categories)
                send_money(banker, adv, 11000000)
                contract.opt_in_app(adv) 
        print("Advertiser opting-in complete\n")
        time.sleep(5)

    elif init == False:
        print("Building contract app...\n")
        with open(os.path.join(os.path.dirname(__file__), "account_cate_" + str(cate_num) + "_set_" + str(set_num) + ".txt"), "r") as fp:
            content_info = fp.readline()
        contract = Contract(API_key, algod_address, index_address, content_info)
        contract.log_file = "debug_adv_set_" + str(set_num) + "_cate_" + str(cate_num) + ".log"
        contract.create_code()
        contract.compile_code()
        print("Contract application checking complete\n")

        for idx in range(cate_num): 
            input_categories = ["Category" + str(idx + 1)]
        info = account.generate_account()
        adv = Advertiser(API_key, algod_address, index_address, mnemonic.from_private_key(info[0]))
        adv.login()
        adv.assign_category(input_categories)
        send_money(banker, adv, 11000000)
        contract.opt_in_app(adv) 
        
        # search & online hash testing
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
        assert(local_hexdigest == online_hexdigest)

        # update testing
        print("Testing updating capability of smart contract...\n")
        start = time.time()
        contract.update_app(adv)
        with open(os.path.join(contract.directory, contract.log_file), "a+") as fp:
            fp.write("The time cost of updating one advertiser in " + search_category + " is: " + str(time.time() - start) + "\n")

        time.sleep(5)
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
        assert(local_hexdigest == online_hexdigest)

        # close out testing
        print("Testing closing out capability of smart contract...\n")
        start = time.time()
        contract.close_out_app(adv)
        with open(os.path.join(contract.directory, contract.log_file), "a+") as fp:
            fp.write("The time cost of closing out one advertiser in " + search_category + " is: " + str(time.time() - start) + "\n")

        time.sleep(5)
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
        assert(local_hexdigest == online_hexdigest)


if __name__ == "__main__":
    """
    CHANGE PARAMS HERE TO LAUNCH DIFFERENT MODE
    """
    init = True
    cate_num = 4
    adv_nums_set = [
        [1,2,4,3],
        [1,2,3,4]
    ]

    assert(type(init) is bool)
    assert(type(cate_num) is int)
    assert(type(adv_nums_set) is list)
    for set_num, adv_nums in enumerate(adv_nums_set):
        assert(type(adv_nums) is list)
        test_main(init, set_num, cate_num, adv_nums)

    for set_num, adv_nums in enumerate(adv_nums_set):
        test_main(False, set_num, cate_num, adv_nums)

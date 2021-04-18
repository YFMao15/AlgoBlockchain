import os
import time
import random
import argparse
from User import *
from Advertiser import *
from Contract import *

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
    txn = transaction.PaymentTxn(sender.account_public_key, params, receiver.account_public_key, send_amount)
    signed_txn = txn.sign(sender.account_private_key)
    sender.algod_client.send_transactions([signed_txn])
    wait_for_confirmation(sender.algod_client, txid = signed_txn.transaction.get_txid())

def test_main(cate_num, adv_nums, key):
    API_key = "CdYVr07ErYa3VNessIks1aPcmlRYPjfZ34KYF7TF"
    algod_address = "https://testnet-algorand.api.purestake.io/ps2"
    index_address = "https://testnet-algorand.api.purestake.io/idx2"

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

    print("Reading existed contract app...\n")
    with open(os.path.join(os.path.dirname(__file__), "account_adv_" + str(adv_nums) + "_cate_" + str(cate_num) + ".txt"), "r") as fp:
        content_info = fp.readline()
    contract = Contract(API_key, algod_address, index_address, content_info)
    contract.log_file = "test_imbalance_adv_" + str(adv_nums) + "_cate_" + str(cate_num) + ".log"
    contract.create_code()
    contract.compile_code()
    print("Contract application checking complete\n")
    # print("Contract mneumonic passphrase: ")
    # print(content_info)

    # opt-in testing
    print("Testing opting in advertiser...\n")
    info = account.generate_account()
    adv = Advertiser(API_key, algod_address, index_address, mnemonic.from_private_key(info[0]))
    adv.login()
    input_categories = []
    for count in range(1, 1 + cate_num):
        input_categories.append("Category" + str(count))
        adv.assign_category(input_categories)
    adv.content = bytes(''.join(random.choices(string.ascii_uppercase + string.digits, k=960)), 'utf-8')
    send_money(banker, adv, 11000000)
    start = time.time()
    contract.opt_in_app(adv) 
    with open(os.path.join(contract.directory, contract.log_file), "a+") as fp:
        fp.write("The time cost of opting in one advertiser is: " + str(time.time() - start) + "\n")
    time.sleep(5)

    # update testing
    print("Testing updating advertiser...\n")
    adv.content = bytes(''.join(random.choices(string.ascii_uppercase + string.digits, k=960)), 'utf-8')
    start = time.time()
    contract.update_app(adv)
    with open(os.path.join(contract.directory, contract.log_file), "a+") as fp:
        fp.write("The time cost of updating one advertiser in is: " + str(time.time() - start) + "\n")

    # close out testing
    print("Testing closing out advertiser...\n")
    start = time.time()
    contract.clear_app(adv)
    with open(os.path.join(contract.directory, contract.log_file), "a+") as fp:
        fp.write("The time cost of closing out one advertiser in is: " + str(time.time() - start) + "\n")

    # search & online hash testing
    time.sleep(5)
    print("Testing searching capability of smart contract of " + str(cate_num) + " categories...\n")
    full_serach_time = 0.
    local_hash_time = 0.

    for idx in range(1, cate_num + 1):
        search_category = "Category" + str(idx)
        start = time.time()
        contract.full_search(user, search_category)
        full_serach_time += (time.time() - start)
            
        time.sleep(3)
        contract.create_hash_local_file(user)
        
        start = time.time()
        local_hexdigest = contract.compute_local_hash(user, search_category)  
        local_hash_time += (time.time() - start)

    with open(os.path.join(contract.directory, contract.log_file), "a+") as fp:
        fp.write("The time cost of search " + str(cate_num) + " categories is: " + str(full_serach_time) + "\n")
        fp.write("The time cost of local hash computation of " + str(cate_num) + " categories is: " + str(local_hash_time) + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Running the imbalanced testing of blockchain in cmd mode.')
    parser.add_argument('-c', '--cate-num', type=int, 
        help='The number of categories of round building')
    parser.add_argument('-a', '--adv-nums', type=int, nargs='+',
        help='The number of advertisers inside one category')
    parser.add_argument('-k', '--key', type=int,
        help='The index of key selected')
    parser.add_argument('-r', '--round-num', type=int,
        help='The testing rounds of the same experiment')

    args = parser.parse_args(sys.argv[1:])
    cate_num = args.cate_num
    adv_nums = args.adv_nums
    key = args.key
    round_num = args.round_num

    assert(type(cate_num) is int)
    assert(type(adv_nums) is list)
    assert(len(adv_nums) == cate_num)
    assert(type(key) is int)
    assert((key >= 1) and (key <= 6))
    assert(type(round_num) is int)

    for _ in range(round_num):
        test_main(cate_num, adv_nums, key)
        time.sleep(5)
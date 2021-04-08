import os
import time
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

def test_main(cate_num, adv_num, key):
    if int(key) == 1:
        API_key = "afETOBfGPz3JfzIY3B1VG48kIGsMrlxO67VdEeOC"
    elif int(key) == 2:
        API_key = "7iNfo9pqXu4TbDwzzR6oB6yqcnxcpLwm36HdRHTu"
    elif int(key) == 3:
        API_key = "CdYVr07ErYa3VNessIks1aPcmlRYPjfZ34KYF7TF"
    elif int(key) == 4:
        API_key = "bm7hPLk9qh3E0paWuID732svReMjXUl7R2cUEAfb"
    elif int(key) == 5:
        API_key = "yyQ3OgPjfH8596UMflj213aSXUPeZU9N5Bhpa6OL"
    elif int(key) == 6:
        API_key = "3gy4jhdT5R3HT29Ok4YuXaRCocW3Y8HOaQbpvOJ4"

    algod_address = "https://testnet-algorand.api.purestake.io/ps2"
    index_address = "https://testnet-algorand.api.purestake.io/idx2"

    if os.path.exists(os.path.join(os.path.dirname(__file__), "debug.log")):
        os.remove(os.path.join(os.path.dirname(__file__), "debug.log"))
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

    full_serach_time = 0.
    local_hash_time = 0.
    hash_search_time = 0.
    print("Testing searching capability of smart contract of " + str(cate_num) + " categories...\n")
    for idx in range(1, cate_num + 1):
        print("Reading existed contract app...\n")
        with open(os.path.join(os.path.dirname(__file__), "account_adv_" + str(adv_num) + "_cate_1_" + str(idx) + ".txt"), "r") as fp:
            content_info = fp.readline()
        contract = Contract(API_key, algod_address, index_address, content_info)
        contract.log_file = "test_search_adv_" + str(adv_num) + "_cate_" + str(cate_num) + ".log"
        contract.create_code()
        contract.compile_code()
        print("Contract application checking complete\n")
        # print("Contract mneumonic passphrase: ")
        # print(content_info)

        # search & online hash testing
        search_category = "Category1"
        start = time.time()
        contract.full_search(user, search_category)
        full_serach_time += (time.time() - start)
            
        time.sleep(3)
        contract.create_hash_local_file(user)
        
        start = time.time()
        local_hexdigest = contract.compute_local_hash(user, search_category)  
        local_hash_time += (time.time() - start)

        start = time.time()
        online_hexdigest = contract.search_hash(user, search_category) 
        hash_search_time += (time.time() - start)
        assert(local_hexdigest == online_hexdigest)
        time.sleep(3)

    with open(os.path.join(contract.directory, contract.log_file), "a+") as fp:
        fp.write("The time cost of search " + str(cate_num) + " categories is: " + str(full_serach_time) + "\n")
        fp.write("The time cost of local hash computation of " + str(cate_num) + " categories is: " + str(local_hash_time) + "\n")
        fp.write("The time cost of on-chain hash searching of " + str(cate_num) + " categories is: " + str(hash_search_time) + "\n")   

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Running the round testing of blockchain in cmd mode.')
    parser.add_argument('-c', '--cate-num', type=int, 
        help='The number of categories of round test')
    parser.add_argument('-a', '--adv-num', type=int, 
        help='The number of advertisers inside one category')
    parser.add_argument('-k', '--key', type=int,
        help='The index of key selected')
    parser.add_argument('-r', '--round-num', type=int,
        help='The testing rounds of the same experiment')

    args = parser.parse_args(sys.argv[1:])
    adv_num = args.adv_num
    cate_num = args.cate_num
    key = args.key
    round_num = args.round_num

    assert(type(cate_num) is int)
    assert(type(adv_num) is int)
    assert(type(key) is int)
    assert((key >= 1) and (key <= 6))
    assert(type(round_num) is int)

    for _ in range(round_num):
        test_main(cate_num, adv_num, key)
        time.sleep(5)
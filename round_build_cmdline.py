import os
import time
import argparse
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
    txn = transaction.PaymentTxn(sender.account_public_key, params, receiver.account_public_key, send_amount)
    signed_txn = txn.sign(sender.account_private_key)
    sender.algod_client.send_transactions([signed_txn])
    wait_for_confirmation(sender.algod_client, txid = signed_txn.transaction.get_txid())

def build_main(init, cate_num, adv_num, key):
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

    print("Building contract app...\n")
    building_adv_nums = [adv_num for _ in range(cate_num)]

    if init is True:
        content_info = mnemonic.from_private_key(account.generate_account()[0])
        temp = Advertiser(API_key, algod_address, index_address, content_info)
        temp.login()
        send_money(banker, temp, 15000000)
        contract = Contract(API_key, algod_address, index_address, content_info)
        contract.create_code()
        contract.compile_code()
        contract.init_contract(cate_num)
        # distinguish the testing results of different params
        with open(os.path.join(os.path.dirname(__file__), "account_adv_" + str(adv_num) + "_cate_" + str(cate_num) + ".txt"), "w") as fp:
            fp.write(content_info)
        print("Contract application building complete\n")
    
    else: 
        with open(os.path.join(os.path.dirname(__file__), "account_adv_" + str(adv_num) + "_cate_" + str(cate_num) + ".txt"), "r") as fp:
            content_info = fp.readline()
        contract = Contract(API_key, algod_address, index_address, content_info)
        # Subtract existed advertisers
        for x in range(cate_num):
            building_adv_nums[x] -= contract.check_contract(cate_num, adv_num)
            assert(building_adv_nums[x] >= 0)
        contract.create_code()
        contract.compile_code()
        print("Contract application checking complete\n")
    # print("Contract mneumonic passphrase: ")
    # print(content_info)
    print("The advertisers needed opting-in are " + str(building_adv_nums) + "\n")

    print("Adding advertisers...\n")
    for count in range(len(building_adv_nums)):
        building_adv_num = building_adv_nums[count]
        for x in range(building_adv_num):
            info = account.generate_account()
            adv = Advertiser(API_key, algod_address, index_address, mnemonic.from_private_key(info[0]))
            adv.login()
            adv.assign_category(["Category" + str(count + 1)])
            send_money(banker, adv, 11000000)
            time.sleep(2)
            contract.opt_in_app(adv)
            time.sleep(2)
            send_money(adv, banker, 10000000)
            if (x + 1) % 5 == 0:
                print(str(x + 1) + " / " + str(building_adv_num) + " advertisers in category " + "Category" + str(count + 1) + " finished opting-in")
    print("Advertiser opting-in complete\n")

    time.sleep(5)
    # verifying opt-in results by comparing the hash value
    print("Verifying the contract opt-in process...\n")
    contract.create_hash_local_file(user)
    for count in range(cate_num):
        time.sleep(5)
        local_hexdigest = contract.compute_local_hash(user, "Category" + str(count + 1))
        online_hexdigest = contract.search_hash(user, "Category" + str(count + 1))
        assert(local_hexdigest == online_hexdigest)

if __name__ == "__main__":
    def str2bool(input_cmd):
        if isinstance(input_cmd, bool):
            return input_cmd
        if input_cmd.lower() in ('yes', 'true', 't', 'y', '1'):
            return True
        elif input_cmd.lower() in ('no', 'false', 'f', 'n', '0'):
            return False
        else:
            raise argparse.ArgumentTypeError('Boolean value expected.')

    parser = argparse.ArgumentParser(description='Running the round building of blockchain in cmd mode.')
    parser.add_argument('-i', '--init-mode', type=str2bool,
        help='The initialization of round building, init == True when contract account is not created, init == False when there already exists contract account')
    parser.add_argument('-c', '--cate-num', type=int, 
        help='The number of categories of round building')
    parser.add_argument('-a', '--adv-num', type=int, 
        help='The number of advertisers inside one category')
    parser.add_argument('-k', '--key', type=int,
        help='The index of key selected')

    args = parser.parse_args(sys.argv[1:])
    init = args.init_mode
    cate_num = args.cate_num
    adv_num = args.adv_num
    key = args.key

    assert(type(init) is bool)
    assert(type(cate_num) is int)
    assert(type(adv_num) is int)
    assert(type(key) is int)
    assert((key >= 1) and (key <= 6))
    build_main(init, cate_num, adv_num, key)
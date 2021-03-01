import os
import time
import random
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

def test_main(init, cate_nums, adv_nums, key, thrifty_mode):
    if int(key) == 1:
        API_key = "afETOBfGPz3JfzIY3B1VG48kIGsMrlxO67VdEeOC"
    elif int(key) == 2:
        API_key = "7iNfo9pqXu4TbDwzzR6oB6yqcnxcpLwm36HdRHTu"
    elif int(key) == 3:
        API_key = "CdYVr07ErYa3VNessIks1aPcmlRYPjfZ34KYF7TF"
    algod_address = "https://testnet-algorand.api.purestake.io/ps2"
    index_address = "https://testnet-algorand.api.purestake.io/idx2"

    for cate_num in cate_nums:
        for adv_num in adv_nums:
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
                send_money(banker, temp, 15000000)
                contract = Contract(API_key, algod_address, index_address, content_info)
                contract.create_code()
                contract.compile_code()
                contract.init_contract(cate_num)
                # distinguish the testing results of different params
                contract.log_file = "debug_adv_" + str(adv_num) + "_cate_" + str(cate_num) + ".log"
                with open(os.path.join(os.path.dirname(__file__), "account_cate_" + str(cate_num) + ".txt"), "w") as fp:
                    fp.write(content_info)
                print("Contract application building complete\n")
            else: 
                with open(os.path.join(os.path.dirname(__file__), "account_cate_" + str(cate_num) + ".txt"), "r") as fp:
                    content_info = fp.readline()
                contract = Contract(API_key, algod_address, index_address, content_info)
                contract.log_file = "debug_adv_" + str(adv_num) + "_cate_" + str(cate_num) + ".log"
                # Subtract existed advertisers
                adv_num -= contract.check_contract(cate_num, adv_num)
                contract.create_code()
                contract.compile_code()
                print("Contract application checking complete\n")
            # print("Contract mneumonic passphrase: ")
            # print(content_info)

            print("Adding advertisers...\n")
            adv_list = defaultdict(list)
            for x in range(adv_num):
                info = account.generate_account()
                adv = Advertiser(API_key, algod_address, index_address, mnemonic.from_private_key(info[0]))
                adv.login()
                input_categories = []
                for count in range(1, 1 + cate_num):
                    input_categories.append("Category" + str(count))
                    adv_list["Category" + str(count)].append(adv)
                adv.assign_category(input_categories)
                send_money(banker, adv, 11000000)
                if x == adv_num - 1:
                    start = time.time()
                contract.opt_in_app(adv) 
            with open(os.path.join(contract.directory, contract.log_file), "a+") as fp:
                fp.write("The time cost of opting in one advertiser at " + str(adv_num) + "th place in each category is: " + str(time.time() - start) + "\n")
            print("Advertiser opting-in complete\n")
            time.sleep(5)
        
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
            updated_adv = adv_list[search_category][adv_num // 3]
            contract.update_app(updated_adv)
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
            closed_out_adv = adv_list[search_category][adv_num // 9]
            contract.close_out_app(closed_out_adv)
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

            # Return money to banker account, saving the balance in our testing account
            if thrifty_mode is True:
                for category in adv_list:
                    for x in range(adv_num):
                        adv = adv_list[category][x]
                        send_money(adv, banker, 10900000)
                with open(os.path.join(contract.directory, contract.log_file), "a+") as fp:
                    fp.write("Money returned from advertisers to banker account for reusing \n")


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

    parser = argparse.ArgumentParser(description='Running the round testing of blockchain in cmd mode.')
    parser.add_argument('-i', '--init-mode', type=str2bool,
        help='The initial mode of round test')
    parser.add_argument('-c', '--cate-nums', type=int, nargs='+',
        help='The number of categories of round test')
    parser.add_argument('-a', '--adv-nums', type=int, nargs='+',
        help='The number of advertisers inside one category')
    parser.add_argument('-k', '--key', type=int,
        help='The index of key selected')
    parser.add_argument('-t', "--thrifty-mode", type=str2bool,
        help='The decision to transferring balance back to banker account for reuse')

    # args = parser.parse_args(["-i", "False", "-c", "1", "2", "3", "-a", "3", "5"])
    args = parser.parse_args(sys.argv[1:])
    input_adv_nums = args.adv_nums
    input_cate_nums = args.cate_nums
    input_init = args.init_mode
    key = args.key
    thrifty_mode = args.thrifty_mode

    for cate_num in input_cate_nums:
        init = input_init
        cate_nums = [int(cate_num)]
        adv_nums = [int(input_adv_nums[0])]

        assert(type(init) is bool)
        assert(type(cate_nums) is list)
        assert(type(adv_nums) is list)
        assert(int(key) <= 3)
        assert(int(key) >= 1)
        assert(type(thrifty_mode) is bool)

        test_main(init, cate_nums, adv_nums, key, thrifty_mode)
        
        for idx in range(len(input_adv_nums) - 1):
            init = False
            cate_nums = [int(cate_num)]
            adv_nums = [int(input_adv_nums[idx + 1])]

            assert(type(init) is bool)
            assert(type(cate_nums) is list)
            assert(type(adv_nums) is list)
            assert(int(key) <= 3)
            assert(int(key) >= 1)
            assert(type(thrifty_mode) is bool)

            test_main(init, cate_nums, adv_nums, key, thrifty_mode)
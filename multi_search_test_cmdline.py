import os
import time
import random
import argparse
from Utils import *
from User import *
from Advertiser import *
from Contract import *

def test_main(cate_num, adv_num, key, search_mode, start_time):
    API_key = "CdYVr07ErYa3VNessIks1aPcmlRYPjfZ34KYF7TF"
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
    timestamp_search_time = 0.
    opt_in_time = 0.
    update_time = 0.
    close_out_time = 0.
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

        if not search_mode:
            # opt-in testing
            print("Testing opting in advertiser...\n")
            info = account.generate_account()
            adv = Advertiser(API_key, algod_address, index_address, mnemonic.from_private_key(info[0]))
            adv.login()
            input_categories = []
            input_categories.append("Category1")
            adv.assign_category(input_categories)
            adv.content = bytes(''.join(random.choices(string.ascii_uppercase + string.digits, k=960)), 'utf-8')
            send_money(banker, adv, 11000000)
            time.sleep(3)
            start = time.time()
            contract.opt_in_app(adv) 
            opt_in_time += (time.time() - start)
            
            # update testing
            time.sleep(3)
            print("Testing updating advertiser...\n")
            adv.content = bytes(''.join(random.choices(string.ascii_uppercase + string.digits, k=960)), 'utf-8')
            start = time.time()
            contract.update_app(adv)
            update_time += (time.time() - start)

            # close out testing
            time.sleep(3)
            print("Testing closing out advertiser...\n")
            start = time.time()
            contract.clear_app(adv)
            close_out_time += (time.time() - start)
            
        print("Testing searching capability of smart contract of " + str(cate_num) + " categories...\n")
        # search & online hash testing
        search_category = "Category1"
        time.sleep(3)
        start = time.time()
        contract.full_search(user, search_category)
        full_serach_time += (time.time() - start)

        time.sleep(3)
        start = time.time()
        contract.search_by_time(user, search_category, start_time)
        timestamp_search_time += (time.time() - start)
            
    with open(os.path.join(contract.directory, contract.log_file), "a+") as fp:
        fp.write("The time cost of opting in one advertiser is: " + str(opt_in_time) + "\n")
        fp.write("The time cost of updating one advertiser is: " + str(update_time) + "\n")
        fp.write("The time cost of closing out one advertiser is: " + str(close_out_time) + "\n")
        fp.write("The time cost of search " + str(cate_num) + " categories is: " + str(full_serach_time) + "\n")
        fp.write("The time cost of search " + str(cate_num) + " categories under timestamp condition is: " + str(timestamp_search_time) + "\n")

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
    parser.add_argument('-s', '--search_mode', type=str2bool,
        help='Only the searching experiments will be conducted')
    parser.add_argument('-t', '--time-input', type=int, nargs='+',
        help='The timestamp for searching the smart contract under the condition of starting time, format YYYY MM DD hh mm ss')


    args = parser.parse_args(sys.argv[1:])
    adv_num = args.adv_num
    cate_num = args.cate_num
    key = args.key
    round_num = args.round_num
    search_mode = args.search_mode
    time_input = args.time_input

    assert(type(cate_num) is int)
    assert(type(adv_num) is int)
    assert(type(key) is int)
    assert((key >= 1) and (key <= 6))
    assert(type(round_num) is int)
    assert(type(search_mode) is bool)
    assert(len(time_input) == 6)
    start_time = datetime.datetime(time_input[0], time_input[1], time_input[2], time_input[3], time_input[4], time_input[5], 0, tzinfo=datetime.timezone.utc)
    assert(type(start_time) is datetime.datetime)

    for _ in range(round_num):
        test_main(cate_num, adv_num, key, search_mode, start_time)
        time.sleep(5)
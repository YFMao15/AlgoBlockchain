import os
import time
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

def build_main(init, cate_num, adv_nums):
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

    print("Building contract app...\n")
    building_adv_nums = adv_nums + []

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
        with open(os.path.join(os.path.dirname(__file__), "account_adv_" + str(adv_nums) + "_cate_" + str(cate_num) + ".txt"), "w") as fp:
            fp.write(content_info)
        print("Contract application building complete\n")
    
    else: 
        with open(os.path.join(os.path.dirname(__file__), "account_adv_" + str(adv_nums) + "_cate_" + str(cate_num) + ".txt"), "r") as fp:
            content_info = fp.readline()
        contract = Contract(API_key, algod_address, index_address, content_info)
        # Subtract existed advertisers
        for x in range(cate_num):
            cate = "Category" + str(x + 1)
            building_adv_nums[x] -= contract.check_contract(cate, adv_nums[x])
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
    """
    CHANGE PARAMS HERE TO LAUNCH DIFFERENT MODE
    """
    init = True
    cate_num = 2
    adv_nums = [1, 2]
    assert(type(init) is bool)
    assert(type(cate_num) is int)
    assert(type(adv_nums) is list)
    assert(len(adv_nums) == cate_num)
    build_main(init, cate_num, adv_nums)
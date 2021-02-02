import os
import time
import random
from User import *
from Advertiser import *
from IndexContract import *
from ContentContract import *
from MultiContract import *


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
    address = "https://testnet-algorand.api.purestake.io/ps2"

    """
    CHANGE PARAMS HERE TO LAUNCH DIFFERENT MODE
    """
    init = False
    app_accounts = 2
    cate_num = 5

    if init is True:
        if os.path.exists(os.path.join(os.path.dirname(__file__), "debug.log")):
            os.remove(os.path.join(os.path.dirname(__file__), "debug.log"))
        if os.path.exists(os.path.join(os.path.dirname(__file__), "verify.log")):
            os.remove(os.path.join(os.path.dirname(__file__), "verify.log"))
        if os.path.exists(os.path.join(os.path.dirname(__file__), "index")):
            index_files = os.listdir(os.path.join(os.path.dirname(__file__), "index"))
            for x in index_files:
                os.remove(os.path.join(os.path.dirname(__file__), "index", x))

    if os.path.exists(os.path.join(os.path.dirname(__file__), "search.log")):
        os.remove(os.path.join(os.path.dirname(__file__), "search.log"))

    temp_info = account.generate_account()
    user = User(API_key, address, mnemonic.from_private_key(temp_info[0]))
    user.login()

    banker = Advertiser(
        API_key = "afETOBfGPz3JfzIY3B1VG48kIGsMrlxO67VdEeOC",
        advertiser_address = "https://testnet-algorand.api.purestake.io/ps2",
        passphrase = "code thrive mouse code badge example pride stereo sell viable adjust planet text close erupt embrace nature upon february weekend humble surprise shrug absorb faint")
    banker.login()

    # index passphrase must be stored locally
    index_info = "meadow glare silk life neglect inject figure claw purity burden decide wonder cry clerk width case theme screen donor vault rice weasel host able peanut"
    # temp = Advertiser(API_key, address, index_info)
    # temp.login()
    # send_money(banker, temp)
    index = IndexContract(API_key, address, index_info)

    multi_contract = MultiContract(init)
    multi_contract.add_index_account(index)
    multi_contract.index_account.create_code()
    multi_contract.index_account.compile_code()
    multi_contract.index_account.init_index_contract()

    if init is True:
        for x in range(app_accounts):
            content_info = mnemonic.from_private_key(account.generate_account()[0])
            temp = Advertiser(API_key, address, content_info)
            temp.login()
            send_money(banker, temp)
            content = ContentContract(API_key, address, content_info)
            multi_contract.add_content_account(content)
        print("Contract accounts created")
    else:
        content_info = mnemonic.from_private_key(account.generate_account()[0])
        temp = Advertiser(API_key, address, content_info)
        temp.login()
        send_money(banker, temp)
        content = ContentContract(API_key, address, content_info)
        multi_contract.add_content_account(content)
    
    print("Adding advertisers")
    for x in range(cate_num):
        info = account.generate_account()
        adv = Advertiser(API_key, address, mnemonic.from_private_key(info[0]))
        adv.login()
        adv.assign_category("Category1")
        send_money(banker, adv)
        multi_contract.add_adv_into_content_apps(adv)
    print("Category1 opted-in")
        
    for x in range(cate_num):
        info = account.generate_account()
        adv = Advertiser(API_key, address, mnemonic.from_private_key(info[0]))
        adv.login()
        adv.assign_category("Category2")
        send_money(banker, adv)
        multi_contract.add_adv_into_content_apps(adv)
    print("Category2 opted-in")

    # for x in range(cate_num):
    #     info = account.generate_account()
    #     adv = Advertiser(API_key, address, mnemonic.from_private_key(info[0]))
    #     adv.login()
    #     adv.assign_category("Category3")
    #     send_money(banker, adv)
    #     multi_contract.add_adv_into_content_apps(adv)
    # print("Category3 opted-in")

    # for x in range(cate_num):
    #     info = account.generate_account()
    #     adv = Advertiser(API_key, address, mnemonic.from_private_key(info[0]))
    #     adv.login()
    #     adv.assign_category("Category4")
    #     send_money(banker, adv)
    #     multi_contract.add_adv_into_content_apps(adv)
    # print("Category4 opted-in")
        
    # for x in range(cate_num):
    #     info = account.generate_account()
    #     adv = Advertiser(API_key, address, mnemonic.from_private_key(info[0]))
    #     adv.login()
    #     adv.assign_category("Category5")
    #     send_money(banker, adv)
    #     multi_contract.add_adv_into_content_apps(adv)
    # print("Category5 opted-in")
        
    # for x in range(cate_num):
    #     info = account.generate_account()
    #     adv = Advertiser(API_key, address, mnemonic.from_private_key(info[0]))
    #     adv.login()
    #     adv.assign_category("Category6")
    #     send_money(banker, adv)
    #     multi_contract.add_adv_into_content_apps(adv)
    # print("Category6 opted-in")
        
    # for x in range(cate_num):
    #     info = account.generate_account()
    #     adv = Advertiser(API_key, address, mnemonic.from_private_key(info[0]))
    #     adv.login()
    #     adv.assign_category("Category7")
    #     send_money(banker, adv)
    #     multi_contract.add_adv_into_content_apps(adv)
    # print("Category7 opted-in")
        
    # for x in range(cate_num):
    #     info = account.generate_account()
    #     adv = Advertiser(API_key, address, mnemonic.from_private_key(info[0]))
    #     adv.login()
    #     adv.assign_category("Category8")
    #     send_money(banker, adv)
    #     multi_contract.add_adv_into_content_apps(adv)
    # print("Category8 opted-in")
        
    # for x in range(cate_num):
    #     info = account.generate_account()
    #     adv = Advertiser(API_key, address, mnemonic.from_private_key(info[0]))
    #     adv.login()
    #     adv.assign_category("Category9")
    #     send_money(banker, adv)
    #     multi_contract.add_adv_into_content_apps(adv)
    # print("Category9 opted-in")
        
    # for x in range(cate_num):
    #     info = account.generate_account()
    #     adv = Advertiser(API_key, address, mnemonic.from_private_key(info[0]))
    #     adv.login()
    #     adv.assign_category("Category10")
    #     send_money(banker, adv)
    #     multi_contract.add_adv_into_content_apps(adv)
    # print("Category10 opted-in")
    
    # search_category = "Category1"
    # start = time.time()
    # multi_contract.full_search(user, search_category)
    # with open(os.path.join(multi_contract.content_account.directory, multi_contract.content_account.search_file), "a+") as fp:
    #     fp.write("The time cost of search " + search_category + " is: " + str(time.time() - start))

    multi_contract.verify_hash(user, "Category1")
        
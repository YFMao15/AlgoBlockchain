from User import *
from Advertiser import *
from Contract import *
import time

def send_money(sender, receiver):
    def wait_for_confirmation(algodclient, txid):
        last_round = algodclient.status().get('last-round')
        txinfo = algodclient.pending_transaction_info(txid)
        while not (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0):
            print("Waiting for confirmation...")
            last_round += 1
            algodclient.status_after_block(last_round)
            txinfo = algodclient.pending_transaction_info(txid)
        print("Transaction {} confirmed in round {}.".format(txid, txinfo.get('confirmed-round')))

    params = sender.algod_client.suggested_params()
    # 100 algorands
    send_amount = 100000000

    txn = transaction.PaymentTxn(sender.account_public_key, params, receiver.account_public_key, send_amount)
    signed_txn = txn.sign(sender.account_private_key)
    sender.algod_client.send_transactions([signed_txn])
    wait_for_confirmation(sender.algod_client, txid = signed_txn.transaction.get_txid())

if __name__ == "__main__":
    # transfer money to testing account
    banker = Advertiser(
        API_key = "afETOBfGPz3JfzIY3B1VG48kIGsMrlxO67VdEeOC",
        advertiser_address = "https://testnet-algorand.api.purestake.io/ps2",
        passphrase = "code thrive mouse code badge example pride stereo sell viable adjust planet text close erupt embrace nature upon february weekend humble surprise shrug absorb faint")
    banker.login()

    # The algorand account name is the variable name
    adv1 = Advertiser(
        API_key = "afETOBfGPz3JfzIY3B1VG48kIGsMrlxO67VdEeOC",
        advertiser_address = "https://testnet-algorand.api.purestake.io/ps2",
        passphrase = "runway casual crisp couch never toy trap display surge wagon movie exercise lobster warm close casino vote crystal host wolf weird nephew must about merry")
    adv1.login()

    adv2 = Advertiser(
        API_key = "afETOBfGPz3JfzIY3B1VG48kIGsMrlxO67VdEeOC",
        advertiser_address = "https://testnet-algorand.api.purestake.io/ps2",
        passphrase = "garlic goose embark more inner course peasant fly join sister accident cause enhance fall tide thought alley pink index margin inject plastic aerobic able surge")
    adv2.login()

    adv3 = Advertiser(
        API_key = "afETOBfGPz3JfzIY3B1VG48kIGsMrlxO67VdEeOC",
        advertiser_address = "https://testnet-algorand.api.purestake.io/ps2",
        passphrase = "meadow glare silk life neglect inject figure claw purity burden decide wonder cry clerk width case theme screen donor vault rice weasel host able peanut")
    adv3.login()

    adv4 = Advertiser(
        API_key = "afETOBfGPz3JfzIY3B1VG48kIGsMrlxO67VdEeOC",
        advertiser_address = "https://testnet-algorand.api.purestake.io/ps2",
        passphrase = "cross high during drum shoot segment buffalo history earn word frame odor police talk engage boy about supply unique curve upgrade sauce exchange abstract penalty")
    adv4.login()

    adv5 = Advertiser(
        API_key = "afETOBfGPz3JfzIY3B1VG48kIGsMrlxO67VdEeOC",
        advertiser_address = "https://testnet-algorand.api.purestake.io/ps2",
        passphrase = "farm lake plate leader wet account police quiz captain attend major answer range blue pole state permit hero fringe magic quit margin impulse ability intact")
    adv5.login()

    adv6 = Advertiser(
        API_key = "afETOBfGPz3JfzIY3B1VG48kIGsMrlxO67VdEeOC",
        advertiser_address = "https://testnet-algorand.api.purestake.io/ps2",
        passphrase = "once blame leopard cargo air wrestle upset desert cloth beef movie leopard deny movie bronze ring portion erosion balance group walk airport airport ability resource")
    adv6.login()

    adv7 = Advertiser(
        API_key = "afETOBfGPz3JfzIY3B1VG48kIGsMrlxO67VdEeOC",
        advertiser_address = "https://testnet-algorand.api.purestake.io/ps2",
        passphrase = "inner cat switch entry garage unveil image lake endorse frown battle nose wink chapter describe cycle warrior finger usual twin blind risk remember ability poem")
    adv7.login()

    adv8 = Advertiser(
        API_key = "afETOBfGPz3JfzIY3B1VG48kIGsMrlxO67VdEeOC",
        advertiser_address = "https://testnet-algorand.api.purestake.io/ps2",
        passphrase = "burst idle drum hamster oval basket enrich fee hurt pioneer clerk team kick violin obtain segment solve sniff bleak baby tonight imitate paper ability figure")
    adv8.login()

    adv9 = Advertiser(
        API_key = "afETOBfGPz3JfzIY3B1VG48kIGsMrlxO67VdEeOC",
        advertiser_address = "https://testnet-algorand.api.purestake.io/ps2",
        passphrase = "offer frozen item tribe light curve fitness timber huge village earn tank peasant web obscure flower strike puzzle leader remain state disagree clump absent honey")
    adv9.login()

    adv10 = Advertiser(
        API_key = "afETOBfGPz3JfzIY3B1VG48kIGsMrlxO67VdEeOC",
        advertiser_address = "https://testnet-algorand.api.purestake.io/ps2",
        passphrase = "student easy outside heart mechanic prosper inside rent elite trade egg loud balcony leg gather entry scorpion want clock ethics wine list lemon ability impulse")
    adv10.login()

    adv11 = Advertiser(
        API_key = "afETOBfGPz3JfzIY3B1VG48kIGsMrlxO67VdEeOC",
        advertiser_address = "https://testnet-algorand.api.purestake.io/ps2",
        passphrase = "humor salmon fuel smart matrix piano train nest first cargo alarm toilet easily asset visual position image alarm ticket citizen muscle clutch attract above slide")
    adv11.login()

    adv12 = Advertiser(
        API_key = "afETOBfGPz3JfzIY3B1VG48kIGsMrlxO67VdEeOC",
        advertiser_address = "https://testnet-algorand.api.purestake.io/ps2",
        passphrase = "nation raccoon regular credit father slow column describe awake tired ostrich elder what guitar follow output service brisk permit base enforce brother muscle about run")
    adv12.login()

    temp = Advertiser(
        API_key = "afETOBfGPz3JfzIY3B1VG48kIGsMrlxO67VdEeOC",
        advertiser_address = "https://testnet-algorand.api.purestake.io/ps2",
        passphrase = "account impact timber wall weapon coil flat alert park sting west easy alter amateur lucky rose enhance mass script brain crop hint unusual abstract job")
    temp.login()

    contract_client = Contract(
        API_key = "afETOBfGPz3JfzIY3B1VG48kIGsMrlxO67VdEeOC",
        contract_address = "https://testnet-algorand.api.purestake.io/ps2",
        passphrase = "account impact timber wall weapon coil flat alert park sting west easy alter amateur lucky rose enhance mass script brain crop hint unusual abstract job")

    user = User(
        API_key = "afETOBfGPz3JfzIY3B1VG48kIGsMrlxO67VdEeOC",
        user_address = "https://testnet-algorand.api.purestake.io/ps2",
        passphrase = "test run vintage dune funny forget either tape work indicate enrich peace isolate crew pipe prepare someone ahead walk dignity hint peasant call absent debate")
    user.login()
    # send_money(banker,adv1)
    # send_money(banker,adv2)
    # send_money(banker,adv3)
    # send_money(banker,adv4)
    # send_money(banker,adv5)
    # send_money(banker,adv6)
    # send_money(banker,adv7)
    # send_money(banker,adv8)
    # send_money(banker,adv9)
    # send_money(banker,adv10)
    # send_money(banker,adv11)
    # send_money(banker,adv12)
    # send_money(banker,temp)
    # send_money(banker, user)

    contract_client.read_head_app_id()
    contract_client.create_code()
    contract_client.compile_code()

    adv_count = 12
    add_in_times = 30
    category_count = 12
    # for x in range(add_in_times):
    #     time.sleep(3)
    #     if x % adv_count == 0:
    #         print("\n")
    #         adv1.assign_category("Category"+ str(x % category_count+1))
    #         contract_client.add_adv_into_app(adv1)

    #     elif x % adv_count == 1:
    #         print("\n")
    #         adv2.assign_category("Category" + str(x % category_count+1))
    #         contract_client.add_adv_into_app(adv2)

    #     elif x % adv_count == 2:
    #         print("\n")
    #         adv3.assign_category("Category" + str(x % category_count+1))
    #         contract_client.add_adv_into_app(adv3)

    #     elif x % adv_count == 3:
    #         print("\n")
    #         adv4.assign_category("Category" + str(x % category_count+1))
    #         contract_client.add_adv_into_app(adv4)
        
    #     elif x % adv_count == 4:
    #         print("\n")
    #         adv5.assign_category("Category"+ str(x % category_count+1))
    #         contract_client.add_adv_into_app(adv5)

    #     elif x % adv_count == 5:
    #         print("\n")
    #         adv6.assign_category("Category" + str(x % category_count+1))
    #         contract_client.add_adv_into_app(adv6)

    #     elif x % adv_count == 6:
    #         print("\n")
    #         adv7.assign_category("Category" + str(x % category_count+1))
    #         contract_client.add_adv_into_app(adv7)

    #     elif x % adv_count == 7:
    #         print("\n")
    #         adv8.assign_category("Category" + str(x % category_count+1))
    #         contract_client.add_adv_into_app(adv8)
        
    #     elif x % adv_count == 8:
    #         print("\n")
    #         adv9.assign_category("Category"+ str(x % category_count+1))
    #         contract_client.add_adv_into_app(adv9)

    #     elif x % adv_count == 9:
    #         print("\n")
    #         adv10.assign_category("Category" + str(x % category_count+1))
    #         contract_client.add_adv_into_app(adv10)

    #     elif x % adv_count == 10:
    #         print("\n")
    #         adv11.assign_category("Category" + str(x % category_count+1))
    #         contract_client.add_adv_into_app(adv11)

    #     elif x % adv_count == 11:
    #         print("\n")
    #         adv12.assign_category("Category" + str(x % category_count+1))
    #         contract_client.add_adv_into_app(adv12)

    start = time.time()
    contract_client.external_search(user, "Category1")
    print("\nThe searching time cost of " + str(add_in_times) + " add-ins is " + str(time.time() - start))
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
    # 10 algorands
    send_amount = 10000000

    txn = transaction.PaymentTxn(sender.account_public_key, params, receiver.account_public_key, send_amount)
    signed_txn = txn.sign(sender.account_private_key)
    sender.algod_client.send_transactions([signed_txn])
    wait_for_confirmation(sender.algod_client, txid = signed_txn.transaction.get_txid())


if __name__ == "__main__":
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

    contract_client = Contract(
        API_key = "afETOBfGPz3JfzIY3B1VG48kIGsMrlxO67VdEeOC",
        contract_address = "https://testnet-algorand.api.purestake.io/ps2",
        passphrase = "account impact timber wall weapon coil flat alert park sting west easy alter amateur lucky rose enhance mass script brain crop hint unusual abstract job")
    contract_client.read_head_app_id()
    contract_client.create_code()
    contract_client.compile_code()

    adv_count = 1000
    for x in range(adv_count):
        time.sleep(3)
        if x % 4 == 0:
            print("\n")
            contract_client.create_contract_app()
            adv1.assign_category("Category"+ str(x%8+1))
            contract_client.opt_in_app(adv1)
            contract_client.chain_app(adv1)

        elif x % 4 == 1:
            print("\n")
            contract_client.create_contract_app()
            adv2.assign_category("Category" + str(x%8+1))
            contract_client.opt_in_app(adv2)
            contract_client.chain_app(adv2)

        elif x % 4 == 2:
            print("\n")
            contract_client.create_contract_app()
            adv3.assign_category("Category" + str(x%8+1))
            contract_client.opt_in_app(adv3)
            contract_client.chain_app(adv3)

        elif x % 4 == 3:
            print("\n")
            contract_client.create_contract_app()
            adv4.assign_category("Category" + str(x%8+1))
            contract_client.opt_in_app(adv4)
            contract_client.chain_app(adv4)

    start = time.time()
    contract_client.search_category("Category2")
    print("\nThe searching time cost of " + str(adv_count) + " advertisers is " + str(time.time() - start))
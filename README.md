**This is the repo to build & test smart contract for Algorand.**

**WARNING:**

This is an academic proof-of-concept prototype, and in particular has not received careful code review. 
This implementation is NOT ready for production use.

**Code structure:**

Contract.py, Advertiser.py, User.py, Utils.py -> main code designing smart contract app

xxxx_build_debug.py -> code to build the smart contract on blockchain using integrated envs
xxxx_test_debug.py -> code to test the functionality of the smart contract using integrated envs

xxxx_build_cmdline.py -> code to build the smart contract on blockchain using terminal
xxxx_test_cmdline.py -> code to test the functionality of the smart contract using terminal

**Building & testing scenarios:**

round -> single or multiple contracts with same number of accounts opted-in
imbalance -> multiple contracts with different number of acconts opted-in
multi_search -> multiple contracts accounts integrated for one test
change_by_ratio -> single or multiple contracts testing with different percentage of accounts whose local storage changed

**Command line arguments:**

xxxx_build_cmdline:
-i: true or false. If true then creating a new account, if false then continue building the account earlier.
-c: int. The number of contracts created in smart contract app account.
-a: int. The number of accounts waiting to be opted-in.
-k: int, 1 <= k <= 6. The index of purestake api keys used for building.

xxxx_test_cmdline.py:
-s: true or false. If true then only testing indexer functionality, if false then testing opt-in, update, delete and indexing.
-c: int. The number of contracts in smart contract app account for testing.
-a: int, or list of ints. The number of accounts in each smart contract app to be tested.
-k: int, 1 <= k <= 6. The index of purestake api keys used for testing.
-r: int. The rounds of repeated testing.
-p: float, 0<= p <= 1. The percentage of accounts with local storage changed.
-t: time stamp like strings. E.g. 2021 5 7 12 0 0. The time stamp which marks the starting time of returning results.

**Outputs:**

account_xxxx.txt: The private key of smart contract accounts.
debug.log: The log of minor processes.
test_xxxx.log: The output of testing process.

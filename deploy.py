import json
from solcx import compile_standard, install_solc
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

# compile Our solidity
print("Installing...")
install_solc("0.6.0")

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"simpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.6.0",
)
# print(compiled_sol)
with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# get bytecode
bytecode = compiled_sol["contracts"]["simpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]
#get abi
abi = json.loads(
    compiled_sol["contracts"]["simpleStorage.sol"]["SimpleStorage"]["metadata"]
)["output"]["abi"]

# print(abi)

# #for connecting to ganache
# w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:8545"))
# chain_id= 1337
# my_address = "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1"
# private_key = os.getenv("PRIVATE_KEY")
# # print(private_key)
#for connecting to Sepolia
w3 = Web3(Web3.HTTPProvider("https://sepolia.infura.io/v3/e90e1b2d0eeb424a91722de60226dfeb"))
chain_id= 11155111
my_address = "0x32E41F3789d9924216FaD199Fd74Df5496288CE1"
#remember use source .env to update private_key
#also remember to leave 0x in the front of .env private_key
private_key = os.getenv("PRIVATE_KEY")

#
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

#
nonce = w3.eth.get_transaction_count(my_address)
# print(nonce)

transaction = SimpleStorage.constructor().build_transaction(
    {"chainId": chain_id, "from": my_address, "nonce":nonce}
)
# print(transaction)

signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
# print(signed_txn)
print("Deploying contract...")
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Deployed")
#We need Contract ABI & Address to work with Contract
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
print(simple_storage.functions.retrieve().call())
print("Updating Contract...")
# create a transaction
store_transaction = simple_storage.functions.store(15).build_transaction(
    {"chainId": chain_id, "from": my_address, "nonce": nonce + 1}
)
# signed the transaction
signed_store_txn = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)
# send the transaction
send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)
print("Updated!")
print(simple_storage.functions.retrieve().call())
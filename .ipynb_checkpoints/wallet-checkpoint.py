from constants import *
import os
import subprocess 
import json
from dotenv import load_dotenv
from bit import Key, PrivateKey, PrivateKeyTestnet
from bit.network import NetworkAPI
from bit import *
from bit import wif_to_key
from web3 import Web3
from eth_account import Account 
from web3.middleware import geth_poa_middleware

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
w3.middleware_onion.inject(geth_poa_middleware, layer =0)


load_dotenv()

mnemonic = os.getenv('MNEMONIC', 'child drastic demand audit engine exotic knife jealous crime private sample ankle crazy first cushion')
print(mnemonic)

def derive_wallets (mnemonic, coin, numderive):
    
    command = f'./derive -g --mnemonic="{mnemonic}" --coin="{coin}" --numderive="{numderive}" --cols=index,path,address,privkey,pubkey,pubkeyhash,xprv,xpub --format=json'

    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    
    keys = json.loads(output)
    
    return keys

derive_wallets(mnemonic, BTCTEST, 3)
derive_wallets(mnemonic, ETH, 3)

coins={'btc-test':derive_wallets (mnemonic, BTCTEST, 3),'eth':derive_wallets (mnemonic, ETH, 3)}
print(json.dumps(coins, indent=4, sort_keys=True))

eth_PrivateKey = coins[ETH][0]['privkey']
btc_PrivateKey = coins[BTCTEST][0]['privkey']


def priv_key_to_account (coin, priv_key):
    if coin == ETH:
        return Account.privateKeyToAccount(priv_key)
    elif coin == BTCTEST:
        return PrivateKeyTestnet(priv_key)


btc_account = priv_key_to_account(BTCTEST,btc_PrivateKey)
eth_account = priv_key_to_account(ETH,eth_PrivateKey)

def create_raw_tx(coin, account, recipient, amount):
    
    if coin == ETH:
        gasEstimate = w3.eth.estimateGas(
        {"from": account.address, "to": recipient, "value": amount}
        )
    return {
        "from": account.address,
        "to": recipient,
        "value": amount,
        "gasPrice": w3.eth.gasPrice, #jason round(w3.eth.gasPrice *1.55)
        "gas": gasEstimate,
        "nonce": w3.eth.getTransactionCount(account.address),
        "chainID": w3.eth.chainId
    }

    if coin == BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(account.address, [(recipient, amount, BTC)])

def send_tx(coin,account, recipient, amount):
    
    raw_tx = create_raw_tx(coin,account,recipient,amount)
    signed_tx = account.sign_transaction(raw_tx)
    
    if coin == ETH:
        result = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        return result.hex()
    elif coin == BTCTEST:
        return NetworkAPI.broadcast_tx_testnet(signed_tx)

btc_tx = create_raw_tx(BTCTEST, btc_account, 'mke3YHzqNhDSaZ1qVNSPyLB2TVdYzojYSm', 0.000001 )
btc_tx
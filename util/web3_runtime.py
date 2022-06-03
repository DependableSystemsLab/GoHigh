from web3 import Web3
import os
import solcx
from solcx import compile_source


GETH_PATH = os.getenv('GETH_PATH')
ACCOUNT = os.getenv('GETH_ACCOUNT')
PRIVATE_KEY = os.getenv('GETH_ACCOUNT_PRIVATE_KEY')
PASSWORD = os.getenv('GETH_ACCOUNT_PASSWORD')

SCRIPT_TO_START_GETH_NODE = f'''
geth --datadir "~/ethereum/peer1" --networkid 24601 --port 12341 --http --http.port 9001 --http.corsdomain "*" --http.addr "0.0.0.0" --http.api web3,eth,debug,personal,net --ipcpath {GETH_PATH}  --allow-insecure-unlock console
'''

def initialize_web3_env():
    w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:9001'))
    w3.isConnected()
    w3.eth.get_block('latest') # test connection
    defaultAccount = w3.toChecksumAddress(ACCOUNT)
    w3.eth.default_account = defaultAccount
    w3.eth.get_balance(defaultAccount)
    w3.geth.personal.unlock_account(defaultAccount, PASSWORD, 0)

    return w3

def initialize_solcx_env(df):
    for ver in df['compiler_version'].unique():
        try:
            solcx.install_solc(f'{ver}')
        except:
            continue

def deploy_contract(w3, contract_code, solc_version):
    compiled_sol = compile_source(contract_code, solc_version=solc_version)
    contract_id, contract_interface = compiled_sol.popitem()

    contract_ = w3.eth.contract(
        abi=contract_interface['abi'],
        bytecode=contract_interface['bin'])
    """
    construct_txn = contract_.constructor().buildTransaction({
        'from': defaultAccount,
        'nonce': w3.eth.getTransactionCount(defaultAccount),
        'gas': 1728712,
        'gasPrice': w3.toWei('21', 'gwei')
    })
    signed = defaultAccount.signTransaction(construct_txn)
    txn_hash = w3.eth.sendRawTransaction(signed.rawTransaction)
    """
    txn_hash = contract_.constructor().transact()
    return txn_hash

def get_contract_address(w3, txn_hash):
    return w3.eth.wait_for_transaction_receipt(txn_hash)['contractAddress']

def deploy_contract_batch(w3, dataset_df, src_dir_path):
    deploy_txns = []
    error_logs = {'address': [], 'msg': []}
    
    for _, r in dataset_df.iterrows():    
        addr = r["code_hash"][:8]
        ver = r['compiler_version']
        fn = f'{src_dir_path}/{addr}.sol'
        with open(fn) as f:
            code = f.read()
        try:
            x = deploy_contract(w3, code, ver)
            deploy_txns.append(x)
        except BaseException as err:
            error_logs['msg'].append(f"Unexpected {err=}, {type(err)=}")
            error_logs['address'].append(addr)
            
    return deploy_txns, error_logs
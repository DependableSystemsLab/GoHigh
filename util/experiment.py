import os
import subprocess

from util.web3_runtime import initialize_web3_env, initialize_solcx_env, deploy_contract_batch


def compile_contract(df):
    install_solc_version(df)
    compile_send(df, 'contract/send', 'contract/send_out')
    compile_send(df, 'contract/send_replace', 'contract/send_replace_out')
    compile_call(df, 'contract/call', 'contract/call_out')
    compile_call(df, 'contract/call_replace', 'contract/call_replace_out')

def compare_waring(df):
    unchange_send, add_send, remove_send = compare_warning_send(df, 'contract/send_out', 'contract/send_replace_out')
    print(f"Unchanged (DS): {unchange_send / sum([unchange_send, add_send, remove_send])}")
    print(f"Add (DS): {add_send / sum([unchange_send, add_send, remove_send])}")
    print(f"Remove (DS): {remove_send / sum([unchange_send, add_send, remove_send])}")
    unchange_call, add_call, remove_call = compare_warning_call(df, 'contract/call_out', 'contract/call_replace_out')
    print(f"Unchanged (CSLC): {unchange_call / sum([unchange_call, add_call, remove_call])}")
    print(f"Add (CSLC): {add_call / sum([unchange_call, add_call, remove_call])}")
    print(f"Remove (CSLC): {remove_call / sum([unchange_call, add_call, remove_call])}")

def replay_transaction(df):
    initialize_solcx_env(df)
    w3 = initialize_web3_env()
    send, call, send_replaced, call_replaced = redeploy_contract(w3, df)
    print(f"Gas cost (before): {get_average_gas_cost(w3, send)}")
    print(f"Gas cost (after): {get_average_gas_cost(w3, send_replaced)}")

def redeploy_contract(w3, df):
    send_df = df[df['type'].str.contains('SE')]
    call_df = df[df['type'].str.contains('CS')]
    deploy_txns_send, _ = deploy_contract_batch(w3, send_df, 'contract/send')
    deploy_txns_call, _ = deploy_contract_batch(w3, call_df, 'contract/call')
    deploy_txns_send_replaced, _ = deploy_contract_batch(w3, send_df, 'contract/send_replaced')
    deploy_txns_call_replaced, _ = deploy_contract_batch(w3, call_df, 'contract/call_replaced')
    return deploy_txns_send, deploy_txns_call, deploy_txns_send_replaced, deploy_txns_call_replaced

def get_average_gas_cost(w3, txns):
    gas_list = []
    for txn in txns:
        gas_list.append(w3.eth.get_transaction(txn)['gas'])
    return sum(gas_list) / len(gas_list)

def install_solc_version(df):
    with open('install_solc_version.sh', 'w') as f:
        f.write(f'#!/bin/sh\n')
        for version in df['compiler_version'].unique():
            f.write(f'solc-select install {version} > /dev/null\n')
    subprocess.call(['chmod', '+x', f'./install_solc_version.sh'])
    subprocess.call([f'./install_solc_version.sh'])
    
def compile_send(df, dir_path, dest_dir_path):
    if not os.path.isdir(dest_dir_path):
        os.mkdir(dest_dir_path)
    send_df = df[df['type'].str.contains('SE')]

    with open(f'compile_{dest_dir_path.split("/")[-1]}.sh', 'w') as f:
        f.write(f'#!/bin/sh\n')
        for _, contract in send_df.iterrows():
            f.write(f'solc-select use {contract["compiler_version"]}\n')
            f.write(f'solc {dir_path}/{contract["address"]}.sol > /dev/null 2> {dest_dir_path}/{contract["address"]}.sol.err\n')
    
    subprocess.call(['chmod', '+x', f'compile_{dest_dir_path.split("/")[-1]}.sh'])
    subprocess.call([f'./compile_{dest_dir_path.split("/")[-1]}.sh'])

def compile_call(df, dir_path, dest_dir_path):
    if not os.path.isdir(dest_dir_path):
        os.mkdir(dest_dir_path)
    call_df = df[df['type'].str.contains('CS')]

    with open(f'compile_{dest_dir_path.split("/")[-1]}.sh', 'w') as f:
        f.write(f'#!/bin/sh\n')
        for _, contract in call_df.iterrows():
            f.write(f'solc-select use {contract["compiler_version"]}\n')
            f.write(f'solc {dir_path}/{contract["address"]}.sol > /dev/null 2> {dest_dir_path}/{contract["address"]}.sol.err\n')
    
    subprocess.call(['chmod', '+x', f'compile_{dest_dir_path.split("/")[-1]}.sh'])
    subprocess.call([f'./compile_{dest_dir_path.split("/")[-1]}.sh'])

def compare_warning_send(df, original_dir_path, replaced_dir_path):
    unchange, add, remove = 0, 0, 0
    send_df = df[df['type'].str.contains('SE')]
    for _, row in send_df.iterrows():
        name = f'{row["address"]}.sol.err'

        with open(os.path.join(original_dir_path, name)) as f:
            warning = f.read()
            warning_count = warning.count("Warning")

        with open(os.path.join(replaced_dir_path, name)) as f:
            replaced_warning = f.read()
            replaced_warning_count = replaced_warning.count("Warning")

        if replaced_warning_count > warning_count:
            add += 1
        elif replaced_warning_count == warning_count:
            unchange += 1
        else:
            remove += 1

    return unchange, add, remove

def compare_warning_call(df, original_dir_path, replaced_dir_path):
    unchange, add, remove = 0, 0, 0
    call_df = df[df['type'].str.contains('CS')]
    for _, row in call_df.iterrows():
        name = f'{row["address"]}.sol.err'

        with open(os.path.join(original_dir_path, name)) as f:
            warning = f.read()
            warning_count = warning.count("Warning")

        with open(os.path.join(replaced_dir_path, name)) as f:
            replaced_warning = f.read()
            replaced_warning_count = replaced_warning.count("Warning")

        if replaced_warning_count > warning_count:
            add += 1
        elif replaced_warning_count == warning_count:
            unchange += 1
        else:
            remove += 1

    return unchange, add, remove
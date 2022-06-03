from collections import Counter

def report_stats(df):
    print(f'Total Contract: {df.shape[0]}')
    print(f'Unique Contract: {df.code_hash.unique().shape}')

    contract_types = df.code.apply(get_type)
    count = Counter(contract_types)
    contract_number = df.shape[0]
    llf_contract_number = contract_number - count[""]

    print(f'Low-level Function: {llf_contract_number / contract_number}')
    print(f'Deprecated Send: {count["SE"] / llf_contract_number}')
    print(f'Constant String Low-level Call: {count["CS"] / llf_contract_number}')
    print(f'Arbitrary Low-level Call: {count["AB"] / llf_contract_number}')
    print(f'Inline Assembly Call: {count["IA"] / llf_contract_number}')

    unique_df = df.drop_duplicates(subset=['code_hash'])
    contract_types = unique_df.code.apply(get_type)
    count = Counter(contract_types)
    contract_number = unique_df.shape[0]
    llf_contract_number = contract_number - count[""]

    print(f'Low-level Function (unique): {llf_contract_number / contract_number}')
    print(f'Deprecated Send (unique): {count["SE"] / llf_contract_number}')
    print(f'Constant String Low-level Call (unique): {count["CS"] / llf_contract_number}')
    print(f'Arbitrary Low-level Call (unique): {count["AB"] / llf_contract_number}')
    print(f'Inline Assembly Call (unique): {count["IA"] / llf_contract_number}')

def get_type(code):
    pattern = ''
    if '.send(' in code:
        pattern += 'SE'
    if '.call(' in code:
        if '.call(bytes4(' in code or '.call(abi.encode' in code:
            pattern += 'CS'
        else:
            pattern += 'AB'
    if ':= call(' in code:
        pattern += 'IA'
    return pattern
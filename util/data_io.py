import pandas as pd
import os

def read_csv(fn):
    
    if not os.path.isdir('contract'):
        os.mkdir('contract')
    if not os.path.isdir('contract/send'):
        os.mkdir('contract/send')
    if not os.path.isdir('contract/call'):
        os.mkdir('contract/call')
    
    df = pd.read_csv(fn)
    for _, row in df.iterrows():
        addr = row['address']
        code = row['code']
        typ = row['type']
        if 'SE' in typ:
            with open(f'contract/send/{addr}.sol', 'w', encoding="utf-8") as f:
                f.write(code)
        if 'CS' in typ:
            with open(f'contract/call/{addr}.sol', 'w', encoding="utf-8") as f:
                f.write(code)

    return df


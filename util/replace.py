import re
from string import ascii_lowercase
import os

def replace_contract(df):
    replace_send(df, 'contract/send', 'contract/send_replaced')
    replace_call(df, 'contract/call', 'contract/call_replaced')

def replace_send(df, dir_path, dest_dir_path):
    if not os.path.isdir(dest_dir_path):
        os.mkdir(dest_dir_path)
    send_df = df[df['type'].str.contains('SE')]
    for _, row in send_df.iterrows():
        code = row['code']
        addr = row['address']
        newlines = []
        func_decls = []

        for line in code.split('\n'):
            func_decl = None
            if re.search('\.send *\(', line):
                line, func_decl = process_line(line)
            newlines.append(line)
            #if func_decl:
            #    func_decls.append(func_decl)
            
        with open(f'{dest_dir_path}/{addr}.sol', 'w', encoding="utf-8") as f:
            f.write('\n'.join(newlines))

def replace_call(df, dirpath, dest_dir_path):
    if not os.path.isdir(dest_dir_path):
        os.mkdir(dest_dir_path)
    call_df = df[df['type'].str.contains('CS')]
    for _, row in call_df.iterrows():
        code = row['code']
        addr = row['address']
        newlines = []
        func_decls = []

        for line in code.split('\n'):
            func_decl = None
            if re.search('\.call *\(', line):
                line, func_decl = process_line(line)
            newlines.append(line)
            if func_decl:
                func_decls.append(func_decl)
            
        with open(f'{dest_dir_path}/{addr}.sol', 'w', encoding="utf-8") as f:
            f.write('\n'.join(newlines))
            f.write('\ncontract test {\n\t')
            f.write('\n\t'.join([x for x in func_decls]))
            f.write('\n}')


def rreplace(string, ori, new, times):
    return new.join(string.rsplit(ori, times))

def process_line(line):
    #         if (!owner.send(amount)) revert();
    pattern_count = [0, 0, 0, 0, 0] # if, ifnot, return, require, bare
    
    if re.search('if *\(!*.*\.send *\(.*\).*\) *revert\(\);', line):
        string_before = re.search('if *\(!*.*\.send *\(.*\).*\) *revert\(\);', line).group()
        string_after = string_before.replace('if', '').replace('!', '').replace('.send(', '.transfer(').replace('.send (', '.transfer(')
        string_after = string_after.replace('revert();', '')
        if '==' in string_after:
            string_after = string_after.split('==')[0]
        string_after = string_after.strip('() ') + ');'

        line = line.replace(string_before, string_after)
        pattern_count[1] += 1

    # if (!addr.send(some_ether)) {
    elif re.search('if *\(![a-zA-Z_\.\(\)_\[\]]*\.send *\(.*\) *{*', line):
        string_before = re.search('if *\(![a-zA-Z_\.\(\)_\[\]]*\.send *\(.*\) *{*', line).group()
        string_after = string_before.replace('if', '').replace('!', '').replace('.send(', '.transfer(').replace('.send (', '.transfer(')
        if '{' in string_after:
            #string_after = string_after.strip('(){ ') + ');'
            string_after = string_after.replace('(', '', 1).replace('{', '', 1)
            string_after = rreplace(string_after, ')', '', 1) + ';'
            string_after += '\nif(false)\n{'
        else:
            string_after = string_after.strip('() ') + ');'
            string_after += '\nif(false)'

        line = line.replace(string_before, string_after)
        pattern_count[0] += 1

    # if (addr.send(some_ether)) {
    elif re.search('if *\([a-zA-Z_\.\(\)_\[\]]*\.send *\(.*\) *{*', line):
        string_before = re.search('if *\([a-zA-Z_\.\(\)_\[\]]*\.send *\(.*\) *{*', line).group()
        string_after = string_before.replace('if', '').replace('.send(', '.transfer(').replace('.send (', '.transfer(')
        if '==' in string_after:
            if '{' in string_after:
                string_after = string_after.split('==')[0] + ') {'
                string_after = string_after.replace('(', '', 1).replace('{', '', 1)
                string_after = rreplace(string_after, ')', '', 1) + ';'
                string_after += '\nif(true)\n{'
            else:
                string_after = string_after.strip('() ') + ');'
                string_after += '\nif(true)'
        else:
            if '{' in string_after:
                string_after = string_after.replace('(', '', 1).replace('{', '', 1)
                string_after = rreplace(string_after, ')', '', 1) + ';'
                string_after += '\nif(true)\n{'
            else:
                string_after = string_after.strip('() ') + ');'
                string_after += '\nif(true)'
        line = line.replace(string_before, string_after)
        pattern_count[1] += 1

    # return msg.sender.send(
    elif re.search('return .*\.send *\(', line):
        string_before = re.search('return .*\.send *\(', line).group()
        string_after = string_before.replace('return', '').replace('.send(', '.transfer(').replace('.send (', '.transfer(')
        line = line.replace(string_before, string_after)
        pattern_count[2] += 1

    # require(any.send(some_ether), 'message');
    elif re.search('require *\([^!,]*\.send\([^\,]*\), *[\d\w_ \"\'\.]*\);', line):
        string_before = re.search('require *\([^!,]*\.send\([^\,]*\), *[\d\w_ \"\'\.]*\);', line).group()
        string_after = string_before.replace('require(', '').replace('require (', '').replace('.send(', '.transfer(').replace('.send (', '.transfer(')
        if string_after.find(',') != -1:
            string_after = string_after[:string_after.find(',')]
            string_after += ';'
        else:
            string_after = rreplace(string_after, ')', '', 1)
        line = line.replace(string_before, string_after)
        pattern_count[3] += 1

    # require(any.send(some_ether));
    elif re.search('require *\([^!,]*\.send\([^\,]*\)\);', line):
        string_before = re.search('require *\([^!,]*\.send\([^\,]*\)\);', line).group()
        string_after = string_before.replace('require(', '').replace('require (', '').replace('.send(', '.transfer(').replace('.send (', '.transfer(')
        if string_after.find(',') != -1:
            string_after = string_after[:string_after.find(',')]
            string_after += ';'
        else:
            string_after = rreplace(string_after, ')', '', 1)
        line = line.replace(string_before, string_after)
        pattern_count[3] += 1

    # assert(any.send(some_ether));
    elif re.search('assert\([^!,]*\.send\(.*\)\);', line):
        string_before = re.search('assert\([^!,]*\.send\(.*\)\);', line).group()
        string_after = string_before.replace('assert(', '').replace('.send(', '.transfer(').replace('.send (', '.transfer(')
        if string_after.find(',') != -1:
            string_after = string_after[:string_after.find(',')]
            string_after += ';'
        else:
            string_after = rreplace(string_after, ')', '', 1)
        line = line.replace(string_before, string_after)
        pattern_count[3] += 1

    #bool re_s = address(this).send(any_ether);
    elif re.search(' *= *[a-zA-Z_\.\(\)_\[\]]*\.send\([a-zA-Z_.\(\)]*\);', line):
        string_before = re.search(' *= *[a-zA-Z_\.\(\)_\[\]]*\.send\([a-zA-Z_.\(\)]*\);', line).group()
        string_after = string_before.replace('=', '= true;\n').replace('.send(', '.transfer(').replace('.send (', '.transfer(')

        line = line.replace(string_before, string_after)
        pattern_count[4] += 1
    
    # any.send(Any) No any.send(Any, b, c)
    elif re.search('\.send *\([^\,\n]*\)', line):
        string_before = re.search('\.send *\([^\,\n]*\)', line).group()
        string_after = string_before.replace('.send(', '.transfer(').replace('.send (', '.transfer(')
        line = line.replace(string_before, string_after)
        pattern_count[4] += 1

    return line, pattern_count

def process_line(line):
    
    pattern_sha3 = '[\w\d_\(\)]+\.call\(bytes4\((bytes32\()*(sha3|keccak256)\("[\w\d_]+\([\w\d_,]*\)"\)+(, [\w\d_,. \[\]]*\)+)*'
    pattern_abi = '[\w\d_\(\)]+\.call\(abi\.encodeWithSignature\("[\w\d_]+\([\w\d_,]*\)"\)*(, [\w\d_,. ]*\)+)*'
    func_decl = None
    
    if re.search(pattern_sha3, line):
        func_call = reconstruct_function_call(extract_string(pattern_sha3, line))
        func_decl = reconstruct_function_declaration(extract_string(pattern_sha3, line))
        line = line.replace(line, func_call)

    elif re.search(pattern_abi, line):
        func_call = reconstruct_function_call(extract_string(pattern_abi, line))
        func_decl = reconstruct_function_declaration(extract_string(pattern_abi, line))
        line = line.replace(line, func_call)

    return line, func_decl

def extract_string(pattern, string):
    return re.search(pattern, string).group()

def extract_dest_address(string):
    dest_addr = string.split('.')[0]
    return ''.join(dest_addr.split('require('))

def extract_function_name(string):
    return string.split('"')[1]

def extract_parameter_list(string):
    return string.split('"')[2].strip('(), ')

def reconstruct_function_call(string):
    da = extract_dest_address(string)
    fn = extract_function_name(string).split('(')[0]
    pl = extract_parameter_list(string)
    return f'test({da}).{fn}({pl});\n'

def reconstruct_function_declaration(string):
    fn = extract_function_name(string)
    pl = fn.strip(')').split('(')[-1]
    alphabet = list(ascii_lowercase)
    pl_add_var_name = ', '.join([a + ' ' + b for (a,b) in zip(pl.split(','), alphabet)]) if pl else ''
    fn_add_var_name = fn.split('(')[0] + '(' + pl_add_var_name + ')'
    return f'function {fn_add_var_name};'
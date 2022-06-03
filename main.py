#! /usr/bin/python3

import argparse
from util.data_io import read_csv
from util.stats import report_stats
from util.replace import replace_contract
from util.experiment import compile_contract, compare_waring, replay_transaction

parser = argparse.ArgumentParser(description='Replace Low-level Functions in Solidity Using GoHigh.')

parser.add_argument('-m', '--mode', choices=['replace', 'stats', 'experiment', 'deploy'],
                    default='stats',
                    help='Replace contracts/Get stats of dataset/run validation experiment')

parser.add_argument('-s', '--source',
                    default='data/gohigh-base-dataset-v2.csv',
                    help='Replace contracts')
parser.add_argument('-d', '--destation',
                    default='output/',
                    help='Replace contracts')
parser.add_argument('-v', '--verbose', default=False,
                    help='Run silently, default=False')



def main():
    args = parser.parse_args()
    mode = args.mode
    input_file_path = args.source
    dataset = read_csv(input_file_path)

    if mode == 'replace':
        replace_contract(dataset)
    elif mode == 'stats':
        report_stats(dataset)
    elif mode == 'experiment':
        compile_contract(dataset)
        compare_waring(dataset)
    elif mode == 'deploy':
        replay_transaction(dataset)

if __name__ == "__main__":
    main()
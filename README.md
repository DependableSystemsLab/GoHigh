# GoHigh

> There are >40% Solidity smart contracts are still using not-recommended features. And >90% of them are avoidable.

GoHigh is a fully automated tool that replace low-level functions in Solidity smart contracts into their high-level alternatives.

SANER'22 paper: https://blogs.ubc.ca/dependablesystemslab/2021/12/18/when-they-go-low-automated-replacement-of-low-level-functions-in-ethereum-smart-contracts/

## How to use

### Replace
Do the replacement job.
```
python3 main.py -s [path to dataset csv file] -m replace
```
### Stats
See how many low-level functions are used in the dataset.
```
python3 main.py -s [path to dataset csv file] -m stats
```
### Compile
See how many warning are eliminated after the replacement.
```
python3 main.py -s [path to dataset csv file] -m experiment
```
> Windows not yet supports the official solc compiler. Please run this on Unix-like system (tested on Ubuntu 20.04 LTS).

### Deploy
Re-deploy the original contract and the replaced contract. See how many gas is saved after the replacement and see whether the replaced contract has identical behaviors as the original one.
```
python3 main.py -s [path to dataset csv file] -m deploy
```

Before re-deployment, make sure you correctly configure the following environment variables:
```
GETH_PATH: the path to a valid geth node. Refer to [Installing Geth official document](https://geth.ethereum.org/docs/install-and-build/installing-geth).
ACCOUNT: the default account that deploy the contracts/issue the transactions. Refer to [Step 1: Generating accounts](https://geth.ethereum.org/docs/getting-started).
PASSWORD: the password to unlock your ACCOUNT
```

Then, start mining in your local geth node to earn some initial Ether (we need them to pay for transaction fee), and to pack the incoming transactions. After all the experiments are done, stop mining.
```
miner.start(3)
miner.stop()
```

### Citation
```
@inproceedings{rui2022when,
  title        = {When They Go Low: Automated Replacement of Low-level Functions in Ethereum Smart Contracts},
  author       = {Xi, Rui and Pattabiraman, Karthik},
  booktitle    = {2022 IEEE International Conference on Software Analysis, Evolution and Reengineering (SANER)},
  year         = {2022},
  organization = {IEEE}
}
```
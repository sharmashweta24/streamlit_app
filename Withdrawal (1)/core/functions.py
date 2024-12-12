from os.path import abspath, join, dirname
from sys import path, exc_info

base_dir = abspath(join(dirname(__file__), "../"))
path.append(base_dir)

from pymongo import MongoClient
from web3 import Web3
from sys import path, exc_info
from datetime import datetime
import time
import pandas as pd
from uuid import uuid4
import requests
from decimal import Decimal
from datetime import timedelta
from hashlib import sha512
from core.db import *

# client = MongoClient("mongodb+srv://doadmin:0ZeKg6Q321x79G4t@db-mongodb-fra1-25085-01-421631d0.mongo.ondigitalocean.com/?authSource=admin")
# db = client['OdecenstTestClone'] 
# client = MongoClient("mongodb+srv://doadmin:E2963A08R7TCep5Z@db-mongodb-fra1-94403-0fe401bc.mongo.ondigitalocean.com/?authSource=admin")
# db = client['Odecent_B'] 
# col1 = db['Withdrawal_Request']
# col2 = db['User_Wallet']
# col3 = db['Withdrawal_Transactions']
# col4 = db['Admin']

BSC_MAINNET_URL = "https://bsc-dataseed.binance.org/"
BSC_TESTNET_URL = "https://data-seed-prebsc-1-s1.binance.org:8545/"
USDT_CONTRACT_ADDRESS = "0x55d398326f99059ff775485246999027b3197955" 
USDT_ABI = '[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"}]'


API_KEY_BSC = 'NK53INX25EUDS7X6W8ZB63DN7B11VWFRTE'
BASE_URL_BSC = 'https://api.bscscan.com/api/'



def trans_id():
    try:
        return 'ODC' + uuid4().hex[:18].upper()
    except Exception as err:
        exc_type, exc_obj, exc_tb = exc_info()
        print(f"Error: {err}")

def get_wallet_balances_bep20(wallet_address:str):
    try:
        # print(f'Fetching wallet balances for {wallet_address}...')
        # st.write(f'Fetching wallet balances.....')
        bscscan_api_key = f'{API_KEY_BSC}'
        rpc_endpoint = "https://bsc-dataseed1.binance.org"
        tokens = {
            "BNB": ("0x0000000000000000000000000000000000000000", 18),
            "USDT": ("0x55d398326f99059ff775485246999027b3197955", 18),
        }
        all_balances = {}
        for token_name, (token_address, decimals) in tokens.items():
            if token_name == 'BNB':
                response = requests.get(f"{BASE_URL_BSC}?module=account&action=balance&address={wallet_address}&tag=latest&apikey={bscscan_api_key}")
                if response.status_code == 200:
                    data = response.json()
                    if data['status'] == '1':
                        balance_wei = int(data['result'])
                        balance_bnb = Decimal(balance_wei) / Decimal("1000000000000000000")
                        all_balances['BNB'] = float(balance_bnb)
                    else:
                        return {'Error': data['message']}
                else:
                    return {'Error': response.status_code}
            else:
                response = requests.post(rpc_endpoint, json={
                    "jsonrpc": "2.0",
                    "method": "eth_call",
                    "params": [{
                        "to": token_address,
                        "data": f"0x70a08231000000000000000000000000{wallet_address.lower()[2:]}"
                    }, "latest"],
                    "id": 1
                })
                data = response.json()
                if "result" in data:
                    balance = int(data["result"], 16)
                    balance_in_decimal = balance / (10 ** decimals)
                    all_balances[token_name] = balance_in_decimal
                else:
                    return {'Error': f"Error getting balance for {token_name}"}
        return all_balances
    except Exception as e:
        exc_type, exc_obj, exc_tb = exc_info()
        print(f"Error: {e}, {exc_tb.tb_lineno}")
        return {'Error': str(e)}

def transfer_usdt_bep20(SENDER_ADDRESS, SENDER_PRIVATE_KEY, RECIPIENT_ADDRESS,amount, mainnet=True):
    try:
        # print(f"Transferring {amount} USDT to {RECIPIENT_ADDRESS}")
        w3 = Web3(Web3.HTTPProvider(BSC_MAINNET_URL if mainnet else BSC_TESTNET_URL))
        if not w3.is_connected():
            return {'Error':"Failed to connect to the network"}
        SENDER_ADDRESS = w3.to_checksum_address(SENDER_ADDRESS)
        RECIPIENT_ADDRESS = w3.to_checksum_address(RECIPIENT_ADDRESS)
        usdt_contract = w3.eth.contract(address=w3.to_checksum_address(USDT_CONTRACT_ADDRESS), abi=USDT_ABI)
        amount_in_smallest_unit = w3.to_wei(amount, 'ether')
        nonce = (w3.eth.get_transaction_count(SENDER_ADDRESS))
        gas_price = w3.eth.gas_price
        txn = usdt_contract.functions.transfer(RECIPIENT_ADDRESS, amount_in_smallest_unit).build_transaction({
            'chainId': 56 if mainnet else 97,  # 56 for mainnet, 97 for testnet
            'gas': 200000,
            'gasPrice': gas_price,
            'nonce': nonce,
        })
        signed_txn = w3.eth.account.sign_transaction(txn, private_key=SENDER_PRIVATE_KEY)
        txn_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
        gas_used = txn_receipt['gasUsed']
        gas_price = w3.eth.gas_price
        txn_fee = gas_used * gas_price
        txn_details = {
            'blockHash': txn_receipt.blockHash.hex(),
            'blockNumber': txn_receipt.blockNumber,
            'contractAddress': txn_receipt.contractAddress,
            'cumulativeGasUsed': txn_receipt.cumulativeGasUsed,
            'from': txn_receipt['from'],
            'gasUsed': txn_receipt.gasUsed,
            'logs': txn_receipt.logs,
            'logsBloom': txn_receipt.logsBloom.hex(),
            'status': txn_receipt.status,
            'to': txn_receipt['to'],
            'transactionHash': txn_receipt.transactionHash.hex(),
            'transactionIndex': txn_receipt.transactionIndex,
            'transactionFee': float(w3.from_wei(txn_fee, 'ether'))
        }
        return {'Success': txn_details}
    except ValueError as err:
        exc_type, exc_obj, exc_tb = exc_info()
        print(f"Error: {err}")
        print(f"Line: {exc_tb.tb_lineno}")
        print(f"Type: {exc_type}")
        return {'Error': err}
    except Exception as err:
        print(f"Error: {err}")
        return {'Error': err}

def calculate(transactions):
    # print('Calculating Transaction Amount...')
    user = col1.find({'TransID': {'$in': transactions} , 'Network': 'BEP.20'}, {'_id': 0,'Amount':1})
    amount = sum([i['Amount'] for i in user])
    return amount

def muliple_withdrawal(st,sender_address, private_key, transactions):
    try:
        final_data = []
        invalid_transactions_id = []
        for transaction in transactions:
            data = {}
            ff = col1.find_one({'TransID': transaction,'Network':'BEP.20','Status':'PENDING'}, {'_id': 0})
            if not ff:
                # print(f"Transaction ID {transaction} not found or Not PENDING or Network is not BEP.20")
                invalid_transactions_id.append(transaction)
                continue
            st.write(f"Transferring {ff['Amount']} USDT to {ff['Wallet_Address']}")
            data['TransID'] = ff['TransID']
            data['Username'] = ff['Username']
            data['Network'] = ff['Network']
            data['Requested_Amount'] = ff['Requested_Amount']
            data['Transfer_Amount'] = ff['Amount']
            data['Fees'] = ff['Fees']
            data['Wallet_Address'] = ff['Wallet_Address']
            trans = transfer_usdt_bep20(sender_address, private_key, ff['Wallet_Address'], ff['Amount'])
            if 'Error' in trans:
                # print(f"Transaction Failed: {trans['Error']} Transaction ID: {ff['TransID']} Username: {ff['Username']} Amount: {ff['Amount']} ")
                continue
            if trans['Success']:
                # print(f"Transaction Successful: {trans['Success']['transactionHash']} Transaction ID: {ff['TransID']} Username: {ff['Username']} Amount: {ff['Amount']} ")
                st.write(f"Transaction Successful: {trans['Success']['transactionHash']} Transaction ID: {ff['TransID']} Username: {ff['Username']} Amount: {ff['Amount']}")
                data['Status'] = 'Success'
                data['TxnHash'] = trans['Success']['transactionHash']
                data['TxnFee'] = trans['Success']['transactionFee']
                data['From'] = trans['Success']['from']
                data['To'] = trans['Success']['to']
                data['Reason'] ='NA'
                final_data.append(data)
                insert_withdrawal_data = {
                    'TransID': trans_id(),
                    'DateTime': datetime.now(),
                    'Username': ff['Username'],
                    'Total_Amount': ff['Requested_Amount'],
                    'Paid': ff['Amount'],
                    'Fees':ff['Fees'],
                    'Executed_By': 'Admin',
                    'Adminname': 'admin',
                    'Transaction_Hash': trans['Success']['transactionHash'],
                    'W_TransID': ff['TransID'],
                    'Status': True
                }
                # print('Updating Database...')
                st.write('Updating Database...')
                col1.update_one(
                    {'TransID': transaction},
                    {
                        '$set': {
                            'Status': 'APPROVED',
                            'Transaction_Hash': trans['Success']['transactionHash'],
                            'Transfer_Amount': ff['Amount'],
                            'Approved_DateTime': datetime.now()
                        }
                    }
                )
                col2.update_one({
                    'Username': ff['Username']
                },
                {
                    '$inc': {
                        'Total_Withdrawal': ff['Requested_Amount']
                    }
                })
                col3.insert_one(insert_withdrawal_data)
            else:
                # print(f"Transaction Failed: {trans['Error']} Transaction ID: {ff['TransID']} Username: {ff['Username']} Amount: {ff['Amount']} ")
                data['Status'] = 'Failed'
                data['TxnHash'] = 'NA'
                data['TxnFee'] = 'NA'
                data['From'] = 'NA'
                data['To'] = 'NA'
                data['Reason'] = trans['Error']
                final_data.append(data)
            time.sleep(5)
        if final_data:
            df = pd.DataFrame(final_data)
            date = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
            df.to_csv(date+'withdrawal_transactions.csv', index=False)
            # print('Generated CSV file: withdrawal_transactions.csv')
        if invalid_transactions_id:
            df1 = pd.DataFrame(invalid_transactions_id)
            df1.to_csv('invalid_transactions_id.csv', index=False)
            # print('Generated CSV file: invalid_transactions_id.csv')
        return True
    except Exception as err:
        exc_type, exc_obj, exc_tb = exc_info()
        print(f"Error: {err}")
        print(f"Line: {exc_tb.tb_lineno}")
        print(f"Type: {exc_type}")

def get_transactions(days=7,status='PENDING',network='BEP.20',enable=False,onhold=False):
    try:
        pipeline = [{'$sort': {'DateTime': -1}}]
        filt = {}
        if days:
            filt['DateTime'] = {'$gte': datetime.now() - timedelta(days=days)}
        if status:
            filt['Status'] = status
        if network:
            filt['Network'] = network
        filt['On_Hold'] = onhold
        filt['Withdrawal_Enabled'] = enable
        pipeline.append({'$match': filt})
        pipeline.append({
            '$project': {
                '_id': 0,
                'DateTime': {'$dateToString': {'format': '%Y-%m-%d %H:%M:%S', 'date': '$DateTime'}},
                'TransID': 1,
                'Username': 1,
                'Network': 1,
                'Requested_Amount': 1,
                'Transfer_Amount': 1,
                'Fees': 1,
                'Amount': 1,
                'Wallet_Address': 1,
                'Status': 1,
                'Created_On': 1,
                'Transaction_Hash': 1
            }
        })
        transactions = list(col1.aggregate(pipeline))
        return transactions
    except Exception as err:
        exc_type, exc_obj, exc_tb = exc_info()
        print(f"Error: {err}")
        print(f"Line: {exc_tb.tb_lineno}")
        print(f"Type: {exc_type}")

def login(st,input1,input2):
    try:
        st.title("Login")
        username = st.text_input(input1)
        password = st.text_input(input2, type="password")
        password_hash = sha512(bytes(password,'utf-8')).hexdigest()
        if st.button("Login"):
            if username == '':
                st.error("Please enter username")
                return
            if password == '':
                st.error("Please enter password")
                return
            search = col4.find_one({'Adminname':username,'Password':password_hash},{'_id':0,'Adminname':1})
            if search:
                st.session_state.logged_in = True
                st.success("Successfully logged in")
                st.rerun()
            else:
                st.error("Invalid username or password")
                return
    except Exception as err:
        pass

def logout(st):
    st.session_state.logged_in = False
    st.rerun()



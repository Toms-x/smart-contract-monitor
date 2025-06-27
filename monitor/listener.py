#!/usr/bin/env python3

import sys
import os
import time
import requests
from datetime import datetime
from web3 import Web3
from dotenv import load_dotenv

# --- FIX FOR ModuleNotFoundError ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# -----------------------------------

from utils.db import init_db, save_event
from utils.notifier import send_slack_alert

# Load environment variables
load_dotenv()

INFURA_URL = os.getenv("INFURA_URL")
CONTRACT_ADDRESS = Web3.to_checksum_address(os.getenv("CONTRACT_ADDRESS"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# --- Configuration ---
TOKEN_SYMBOL_MONITORED = "USDC"
TOKEN_DECIMALS = 6

def handle_event(event, w3_instance):
    """
    This function is called for each new event.
    It now extracts specific data fields, fetches the block timestamp,
    and saves a structured dictionary to the database.
    """
    print(f"Event detected in block {event.blockNumber}: {event.transactionHash.hex()}")

    tx_hash = event.transactionHash.hex()
    block_number = event.blockNumber
    from_address = event.args['from']
    to_address = event.args['to']
    raw_value = event.args['value']
    value_adjusted = raw_value / (10**TOKEN_DECIMALS)

    try:
        block_info = w3_instance.eth.get_block(block_number)
        timestamp = datetime.fromtimestamp(block_info.timestamp).strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        print(f"Error fetching block info for block {block_number}: {e}")
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    structured_event_data = {
        "tx_hash": tx_hash,
        "blockNumber": block_number,
        "timestamp": timestamp,
        "from_address": from_address,
        "to_address": to_address,
        "value": value_adjusted,
        "tokenSymbol": TOKEN_SYMBOL_MONITORED
    }

    save_event(structured_event_data)
    print(f"Successfully saved event {tx_hash} to database.")
    send_slack_alert(f"🚨 New Transfer!\nTx: {tx_hash}\nValue: {value_adjusted} {TOKEN_SYMBOL_MONITORED}")

def main():
    """
    The main runner function, now structured to be resilient to connection drops.
    """
    print("Initializing database...")
    init_db()
    print(f"Monitoring contract: {CONTRACT_ADDRESS}")

    while True:
        try:
            # --- 1. Establish Connection and Create Filter ---
            # This is now inside the loop, so it reconnects if something goes wrong.
            print("Connecting to Ethereum node...")
            w3 = Web3(Web3.HTTPProvider(INFURA_URL))
            if not w3.is_connected():
                raise ConnectionError("Failed to connect to the Ethereum node.")
            
            print("Connection successful. Creating new event filter...")
            contract_abi = [{"anonymous":False,"inputs":[{"indexed":True,"name":"from","type":"address"},{"indexed":True,"name":"to","type":"address"},{"indexed":False,"name":"value","type":"uint256"}],"name":"Transfer","type":"event"}]
            contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi)
            event_filter = contract.events.Transfer.create_filter(from_block='latest')
            print("Event listener started. Polling for new events...")

            # --- 2. Poll for Events in a nested loop ---
            while True:
                for event in event_filter.get_new_entries():
                    handle_event(event, w3)
                time.sleep(5) # poll every 5 seconds

        except Exception as e:
            # --- 3. Handle Errors and Restart the Loop ---
            # This block will catch the "filter not found" error and any other connection issue.
            print(f"An error occurred: {e}")
            print("Restarting listener in 15 seconds...")
            time.sleep(15) # Wait before trying to reconnect

if __name__ == "__main__":
    main()

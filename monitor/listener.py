#!/usr/bin/env python3

import os
import time
import json
import requests
from web3 import Web3
from dotenv import load_dotenv
from hexbytes import HexBytes
from collections.abc import Mapping
from utils.db import init_db, save_event
from utils.notifier import send_slack_alert

# Load environment variables
load_dotenv()

INFURA_URL = os.getenv("INFURA_URL")
CONTRACT_ADDRESS = Web3.to_checksum_address(os.getenv("CONTRACT_ADDRESS"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Initialize Web3
w3 = Web3(Web3.HTTPProvider(INFURA_URL))

# Define the ABI for the event you're listening to
contract_abi = [
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "from", "type": "address"},
            {"indexed": True, "name": "to", "type": "address"},
            {"indexed": False, "name": "value", "type": "uint256"}
        ],
        "name": "Transfer",
        "type": "event"
    }
]

# Connect to the contract
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi)

# Deep conversion to make sure JSON serialization works
def convert(obj):
    if isinstance(obj, Mapping):
        return {k: convert(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert(i) for i in obj]
    elif isinstance(obj, HexBytes):
        return obj.hex()
    elif hasattr(obj, '__dict__'):
        return convert(vars(obj))
    else:
        return obj

# Handle the event
def handle_event(event):
    print("Event detected:", event)
    cleaned_event = convert(event)
    response = requests.post(WEBHOOK_URL, json=cleaned_event)
    print("Webhook response status:", response.status_code)

    # New Slack alert
    tx_hash = cleaned_event.get('transactionHash')
    value = cleaned_event['args'].get('value')
    send_slack_alert(f"🚨 New Transfer!\nTx: {tx_hash}\nValue: {value}")

# Save event to database
    save_event(cleaned_event)

    response = requests.post(WEBHOOK_URL, json=cleaned_event)
    print("Webhook response status:", response.status_code)

# Poll for new events
def log_loop(event_filter, poll_interval):
    while True:
        for event in event_filter.get_new_entries():
            handle_event(event)
        time.sleep(poll_interval)

# Main runner
def main():
    print("Starting event listener...")

# Initialize DB once before listening for events
    init_db()
    
    event_filter = contract.events.Transfer.create_filter(from_block='latest')
    log_loop(event_filter, 2)

if __name__ == "__main__":
    main()
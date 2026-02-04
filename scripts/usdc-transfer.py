#!/usr/bin/env python3
"""
Transfer USDC on testnet.

Supports sending by name, ENS, or raw address:
  --to Alice              (contact book lookup)
  --to vitalik.eth        (ENS resolution)
  --to 0x742d35Cc...      (raw address)
"""
import argparse
import sys
import json
import os
from pathlib import Path
from web3 import Web3
from eth_account import Account
from decimal import Decimal
import time

# Allow importing contacts-manager from the same directory
sys.path.insert(0, str(Path(__file__).resolve().parent))
from importlib import import_module
contacts_mod = import_module("contacts-manager")

# Network configurations
NETWORKS = {
    'base-sepolia': {
        'rpc': 'https://sepolia.base.org',
        'usdc': '0x036CbD53842c5426634e7929541eC2318f3dCF7e',
        'explorer': 'https://sepolia.basescan.org',
        'chain_id': 84532
    },
    'eth-sepolia': {
        'rpc': 'https://ethereum-sepolia-rpc.publicnode.com',
        'usdc': '0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238',
        'explorer': 'https://sepolia.etherscan.io',
        'chain_id': 11155111
    }
}

# ERC-20 ABI
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_to", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    }
]

def load_wallet(key_file: str = None, private_key: str = None) -> Account:
    """Load wallet from file or private key"""
    if private_key:
        return Account.from_key(private_key)
    
    if key_file:
        try:
            with open(key_file, 'r') as f:
                data = json.load(f)
                if 'private_key' in data:
                    return Account.from_key(data['private_key'])
                else:
                    raise ValueError("key_file must contain 'private_key' field")
        except FileNotFoundError:
            raise FileNotFoundError(f"Key file not found: {key_file}")
    
    raise ValueError("Must provide either --key-file or --private-key")

def resolve_recipient(recipient: str) -> tuple[str, str | None]:
    """
    Resolve a recipient to a checksum address.
    Returns (address, display_name_or_None).
    """
    result = contacts_mod.resolve_name(recipient)
    if not result["success"]:
        raise ValueError(result.get("error", f"Cannot resolve recipient: {recipient}"))
    display = result["name"] if result["source"] in ("contacts", "ens", "fuzzy") else None
    return result["address"], display


def transfer_usdc(to_raw: str, amount: float, network: str,
                  key_file: str = None, private_key: str = None,
                  gas_price_gwei: float = None) -> dict:
    """Transfer USDC to another address (accepts name, ENS, or 0x address)"""
    try:
        if network not in NETWORKS:
            raise ValueError(f"Unknown network: {network}")

        # ── resolve recipient ───────────────────────────────────
        to_address, display_name = resolve_recipient(to_raw)

        config = NETWORKS[network]
        w3 = Web3(Web3.HTTPProvider(config['rpc']))
        
        if not w3.is_connected():
            raise ConnectionError(f"Failed to connect to {network}")
        
        # Load wallet
        account = load_wallet(key_file, private_key)
        from_address = account.address
        
        to_address = Web3.to_checksum_address(to_address)
        
        # Get USDC contract
        usdc_contract = w3.eth.contract(
            address=Web3.to_checksum_address(config['usdc']),
            abi=ERC20_ABI
        )
        
        # Get decimals and convert amount
        decimals = usdc_contract.functions.decimals().call()
        amount_wei = int(Decimal(str(amount)) * Decimal(10 ** decimals))
        
        # Check balance
        balance_wei = usdc_contract.functions.balanceOf(from_address).call()
        if balance_wei < amount_wei:
            balance = Decimal(balance_wei) / Decimal(10 ** decimals)
            raise ValueError(f"Insufficient USDC balance. Have: {balance}, Need: {amount}")
        
        # Check ETH balance for gas
        eth_balance = w3.eth.get_balance(from_address)
        if eth_balance == 0:
            raise ValueError("Insufficient ETH for gas fees")
        
        # Build transaction
        nonce = w3.eth.get_transaction_count(from_address)
        
        # Estimate gas
        gas_estimate = usdc_contract.functions.transfer(
            to_address, amount_wei
        ).estimate_gas({'from': from_address})
        
        # Get gas price
        if gas_price_gwei:
            gas_price = w3.to_wei(gas_price_gwei, 'gwei')
        else:
            gas_price = w3.eth.gas_price
        
        # Build transaction
        transaction = usdc_contract.functions.transfer(
            to_address, amount_wei
        ).build_transaction({
            'chainId': config['chain_id'],
            'gas': int(gas_estimate * 1.2),  # Add 20% buffer
            'gasPrice': gas_price,
            'nonce': nonce,
        })
        
        # Sign transaction
        signed_txn = w3.eth.account.sign_transaction(transaction, account.key)
        
        # Send transaction
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        tx_hash_hex = tx_hash.hex()
        
        print(f"Transaction sent: {tx_hash_hex}")
        print(f"Waiting for confirmation...")
        
        # Wait for receipt (with timeout)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
        
        result = {
            'success': True,
            'tx_hash': tx_hash_hex,
            'from': from_address,
            'to': to_address,
            'amount': amount,
            'network': network,
            'block': receipt['blockNumber'],
            'gas_used': receipt['gasUsed'],
            'status': 'confirmed' if receipt['status'] == 1 else 'failed',
            'explorer': f"{config['explorer']}/tx/{tx_hash_hex}"
        }
        if display_name:
            result['recipient_name'] = display_name
        return result
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'network': network
        }

def main():
    parser = argparse.ArgumentParser(description='Transfer USDC on testnet')
    parser.add_argument('--to', required=True, help='Recipient: name, ENS (alice.eth), or 0x address')
    parser.add_argument('--amount', required=True, type=float, help='Amount of USDC to send')
    parser.add_argument('--network', default='base-sepolia',
                       choices=list(NETWORKS.keys()),
                       help='Network to use (default: base-sepolia)')
    parser.add_argument('--key-file', help='Path to JSON file with private_key')
    parser.add_argument('--private-key', help='Private key (use key-file instead for security)')
    parser.add_argument('--gas-price', type=float, help='Gas price in gwei (optional)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    if not args.key_file and not args.private_key:
        print("Error: Must provide either --key-file or --private-key", file=sys.stderr)
        sys.exit(1)
    
    result = transfer_usdc(
        args.to,
        args.amount,
        args.network,
        args.key_file,
        args.private_key,
        args.gas_price
    )
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result['success']:
            to_display = result.get('recipient_name', result['to'])
            if result.get('recipient_name'):
                to_display = f"{result['recipient_name']} ({result['to']})"
            print(f"\n✓ Transfer successful!")
            print(f"From: {result['from']}")
            print(f"To: {to_display}")
            print(f"Amount: {result['amount']} USDC")
            print(f"Tx Hash: {result['tx_hash']}")
            print(f"Block: {result['block']}")
            print(f"Gas Used: {result['gas_used']}")
            print(f"Explorer: {result['explorer']}")
        else:
            print(f"✗ Transfer failed: {result['error']}", file=sys.stderr)
            sys.exit(1)

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Get USDC transaction history for an address
"""
import argparse
import sys
import json
from web3 import Web3
from decimal import Decimal
import requests
import time

# Network configurations
NETWORKS = {
    'base-sepolia': {
        'rpc': 'https://sepolia.base.org',
        'usdc': '0x036CbD53842c5426634e7929541eC2318f3dCF7e',
        'explorer': 'https://sepolia.basescan.org',
        'api': 'https://api-sepolia.basescan.org/api'
    },
    'eth-sepolia': {
        'rpc': 'https://ethereum-sepolia-rpc.publicnode.com',
        'usdc': '0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238',
        'explorer': 'https://sepolia.etherscan.io',
        'api': 'https://api-sepolia.etherscan.io/api'
    }
}

# ERC-20 Transfer event signature
TRANSFER_EVENT_SIGNATURE = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'

def get_history_via_rpc(address: str, network: str, limit: int = 10) -> dict:
    """Get transaction history using RPC (fallback method)"""
    try:
        config = NETWORKS[network]
        w3 = Web3(Web3.HTTPProvider(config['rpc']))
        
        if not w3.is_connected():
            raise ConnectionError(f"Failed to connect to {network}")
        
        address = Web3.to_checksum_address(address)
        usdc_address = Web3.to_checksum_address(config['usdc'])
        
        # Get recent blocks (last ~1000 blocks)
        current_block = w3.eth.block_number
        from_block = max(0, current_block - 1000)
        
        # Get Transfer event topic hash (keep as HexBytes for web3 compatibility)
        transfer_topic = Web3.keccak(text='Transfer(address,address,uint256)')
        
        # Address as topic (padded to 32 bytes, must have 0x prefix)
        address_hex = address[2:].lower().zfill(64)
        address_topic = '0x' + address_hex
        
        # Get transfers FROM this address
        logs_from = w3.eth.get_logs({
            'fromBlock': from_block,
            'toBlock': 'latest',
            'address': usdc_address,
            'topics': [transfer_topic, address_topic]
        })
        
        # Get transfers TO this address
        logs_to = w3.eth.get_logs({
            'fromBlock': from_block,
            'toBlock': 'latest',
            'address': usdc_address,
            'topics': [transfer_topic, None, address_topic]
        })
        
        # Combine and parse logs
        all_logs = logs_from + logs_to
        transactions = []
        
        for log in all_logs[:limit]:
            from_addr = '0x' + log['topics'][1].hex()[-40:]
            to_addr = '0x' + log['topics'][2].hex()[-40:]
            
            # log['data'] is HexBytes in web3.py v6+
            raw_data = log['data']
            if isinstance(raw_data, bytes):
                value = int.from_bytes(raw_data, 'big')
            else:
                value = int(raw_data, 16)
            
            # Get block info
            block = w3.eth.get_block(log['blockNumber'])
            
            direction = 'in' if to_addr.lower() == address.lower() else 'out'
            counterparty = from_addr if direction == 'in' else to_addr
            
            transactions.append({
                'hash': log['transactionHash'].hex(),
                'block': log['blockNumber'],
                'timestamp': block['timestamp'],
                'from': Web3.to_checksum_address(from_addr),
                'to': Web3.to_checksum_address(to_addr),
                'value': value / (10 ** 6),  # USDC has 6 decimals
                'direction': direction,
                'counterparty': Web3.to_checksum_address(counterparty)
            })
        
        # Sort by block number (newest first)
        transactions.sort(key=lambda x: x['block'], reverse=True)
        
        return {
            'success': True,
            'address': address,
            'network': network,
            'transactions': transactions[:limit],
            'method': 'rpc',
            'blocks_scanned': f"{from_block}-{current_block}"
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'address': address,
            'network': network
        }

def get_history(address: str, network: str, limit: int = 10) -> dict:
    """Get USDC transaction history"""
    # For now, use RPC method (API requires key)
    # In production, you could add API key support for better performance
    return get_history_via_rpc(address, network, limit)

def main():
    parser = argparse.ArgumentParser(description='Get USDC transaction history')
    parser.add_argument('--address', required=True, help='Ethereum address')
    parser.add_argument('--network', default='base-sepolia',
                       choices=list(NETWORKS.keys()),
                       help='Network to use (default: base-sepolia)')
    parser.add_argument('--limit', type=int, default=10, help='Number of transactions to fetch')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    result = get_history(args.address, args.network, args.limit)
    
    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        if result['success']:
            print(f"USDC Transaction History")
            print(f"Address: {result['address']}")
            print(f"Network: {result['network']}")
            print(f"Blocks Scanned: {result.get('blocks_scanned', 'N/A')}")
            print(f"\nFound {len(result['transactions'])} transactions:\n")
            
            for tx in result['transactions']:
                direction_symbol = '←' if tx['direction'] == 'in' else '→'
                print(f"{direction_symbol} {tx['value']:.6f} USDC")
                print(f"  {tx['direction'].upper()}: {tx['counterparty']}")
                print(f"  Block: {tx['block']} | Tx: {tx['hash'][:16]}...")
                print(f"  Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(tx['timestamp']))}")
                print()
        else:
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)

if __name__ == '__main__':
    main()

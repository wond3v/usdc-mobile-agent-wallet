#!/usr/bin/env python3
"""
Monitor for incoming USDC transactions
"""
import argparse
import sys
import json
import time
from web3 import Web3
from decimal import Decimal

# Network configurations
NETWORKS = {
    'base-sepolia': {
        'rpc': 'https://sepolia.base.org',
        'usdc': '0x036CbD53842c5426634e7929541eC2318f3dCF7e',
        'explorer': 'https://sepolia.basescan.org'
    },
    'eth-sepolia': {
        'rpc': 'https://ethereum-sepolia-rpc.publicnode.com',
        'usdc': '0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238',
        'explorer': 'https://sepolia.etherscan.io'
    }
}

def monitor_incoming(address: str, network: str, interval: int = 15, 
                     webhook: str = None, output_file: str = None) -> None:
    """Monitor for incoming USDC transactions"""
    try:
        if network not in NETWORKS:
            raise ValueError(f"Unknown network: {network}")
        
        config = NETWORKS[network]
        w3 = Web3(Web3.HTTPProvider(config['rpc']))
        
        if not w3.is_connected():
            raise ConnectionError(f"Failed to connect to {network}")
        
        address = Web3.to_checksum_address(address)
        usdc_address = Web3.to_checksum_address(config['usdc'])
        
        print(f"Monitoring USDC transfers to: {address}")
        print(f"Network: {network}")
        print(f"Check interval: {interval}s")
        print(f"Press Ctrl+C to stop\n")
        
        # Track last seen block
        last_block = w3.eth.block_number
        seen_txs = set()
        
        while True:
            try:
                current_block = w3.eth.block_number
                
                if current_block > last_block:
                    # Get Transfer events to our address
                    transfer_topic = Web3.keccak(text='Transfer(address,address,uint256)').hex()
                    address_topic = '0x' + address[2:].zfill(64).lower()
                    
                    logs = w3.eth.get_logs({
                        'fromBlock': last_block + 1,
                        'toBlock': current_block,
                        'address': usdc_address,
                        'topics': [transfer_topic, None, address_topic]  # Transfers TO our address
                    })
                    
                    for log in logs:
                        tx_hash = log['transactionHash'].hex()
                        
                        # Skip if we've already seen this
                        if tx_hash in seen_txs:
                            continue
                        
                        seen_txs.add(tx_hash)
                        
                        # Parse transfer
                        from_addr = '0x' + log['topics'][1].hex()[-40:]
                        value = int(log['data'], 16) / (10 ** 6)  # USDC has 6 decimals
                        
                        # Get block timestamp
                        block = w3.eth.get_block(log['blockNumber'])
                        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(block['timestamp']))
                        
                        incoming = {
                            'timestamp': timestamp,
                            'block': log['blockNumber'],
                            'tx_hash': tx_hash,
                            'from': Web3.to_checksum_address(from_addr),
                            'to': address,
                            'amount': value,
                            'explorer': f"{config['explorer']}/tx/{tx_hash}"
                        }
                        
                        # Output
                        print(f"\n🔔 Incoming USDC!")
                        print(f"Amount: {value:.6f} USDC")
                        print(f"From: {incoming['from']}")
                        print(f"Tx: {tx_hash}")
                        print(f"Block: {log['blockNumber']}")
                        print(f"Time: {timestamp}")
                        print(f"Explorer: {incoming['explorer']}\n")
                        
                        # Write to file if specified
                        if output_file:
                            with open(output_file, 'a') as f:
                                f.write(json.dumps(incoming) + '\n')
                        
                        # Webhook notification (placeholder for OpenClaw integration)
                        if webhook:
                            print(f"[Webhook trigger: {webhook}]")
                    
                    last_block = current_block
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                print("\n\nMonitoring stopped.")
                break
            except Exception as e:
                print(f"Error during monitoring: {e}", file=sys.stderr)
                time.sleep(interval)
                
    except Exception as e:
        print(f"Failed to start monitoring: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Monitor for incoming USDC transactions')
    parser.add_argument('--address', required=True, help='Address to monitor')
    parser.add_argument('--network', default='base-sepolia',
                       choices=list(NETWORKS.keys()),
                       help='Network to use (default: base-sepolia)')
    parser.add_argument('--interval', type=int, default=15, 
                       help='Check interval in seconds (default: 15)')
    parser.add_argument('--output', help='Write transactions to file (JSON lines)')
    parser.add_argument('--webhook', help='Webhook URL for notifications (future use)')
    
    args = parser.parse_args()
    monitor_incoming(args.address, args.network, args.interval, args.webhook, args.output)

if __name__ == '__main__':
    main()

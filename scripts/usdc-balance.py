#!/usr/bin/env python3
"""
Check USDC balance for an address on testnet
"""
import argparse
import sys
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

# ERC-20 ABI (minimal - just what we need)
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
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function"
    }
]

def check_balance(address: str, network: str) -> dict:
    """Check USDC balance for an address"""
    try:
        if network not in NETWORKS:
            raise ValueError(f"Unknown network: {network}. Choose from: {', '.join(NETWORKS.keys())}")
        
        config = NETWORKS[network]
        w3 = Web3(Web3.HTTPProvider(config['rpc']))
        
        if not w3.is_connected():
            raise ConnectionError(f"Failed to connect to {network}")
        
        # Validate address
        if not Web3.is_address(address):
            raise ValueError(f"Invalid Ethereum address: {address}")
        
        address = Web3.to_checksum_address(address)
        
        # Get USDC contract
        usdc_contract = w3.eth.contract(
            address=Web3.to_checksum_address(config['usdc']),
            abi=ERC20_ABI
        )
        
        # Get balance
        balance_wei = usdc_contract.functions.balanceOf(address).call()
        decimals = usdc_contract.functions.decimals().call()
        symbol = usdc_contract.functions.symbol().call()
        
        # Convert to human-readable format
        balance = Decimal(balance_wei) / Decimal(10 ** decimals)
        
        # Get ETH balance for gas
        eth_balance_wei = w3.eth.get_balance(address)
        eth_balance = Decimal(eth_balance_wei) / Decimal(10 ** 18)
        
        return {
            'success': True,
            'address': address,
            'network': network,
            'usdc_balance': float(balance),
            'eth_balance': float(eth_balance),
            'symbol': symbol,
            'decimals': decimals,
            'explorer': f"{config['explorer']}/address/{address}"
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'address': address,
            'network': network
        }

def main():
    parser = argparse.ArgumentParser(description='Check USDC balance on testnet')
    parser.add_argument('--address', required=True, help='Ethereum address to check')
    parser.add_argument('--network', default='base-sepolia', 
                       choices=list(NETWORKS.keys()),
                       help='Network to use (default: base-sepolia)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    result = check_balance(args.address, args.network)
    
    if args.json:
        import json
        print(json.dumps(result, indent=2))
    else:
        if result['success']:
            print(f"Address: {result['address']}")
            print(f"Network: {result['network']}")
            print(f"USDC Balance: {result['usdc_balance']:.6f} {result['symbol']}")
            print(f"ETH Balance: {result['eth_balance']:.6f} ETH (for gas)")
            print(f"Explorer: {result['explorer']}")
        else:
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)

if __name__ == '__main__':
    main()

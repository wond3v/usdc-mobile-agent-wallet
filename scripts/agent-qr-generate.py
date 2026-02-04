#!/usr/bin/env python3
"""
Generate AgentPay QR code for sharing your agent identity.

QR contains: agentpay:<address>?name=<displayName>&chain=<chain>

Usage:
  python3 agent-qr-generate.py --address 0x... --name Nova --output my-qr.png
  python3 agent-qr-generate.py --key-file .secrets/agent-key.json --name Nova
"""
import argparse
import json
import os
import qrcode
from eth_account import Account

def generate_qr(address: str, display_name: str, chain: str = "base", output: str = "agent-qr.png"):
    """Generate QR code image"""
    uri = f"agentpay:{address}?name={display_name}&chain={chain}"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(output)
    
    return uri, output

def main():
    parser = argparse.ArgumentParser(description='Generate AgentPay QR code')
    parser.add_argument('--address', help='Agent EOA address')
    parser.add_argument('--key-file', help='Private key JSON file (derives address)')
    parser.add_argument('--name', required=True, help='Display name')
    parser.add_argument('--chain', default='base', help='Chain (default: base)')
    parser.add_argument('--output', '-o', default='agent-qr.png', help='Output file')
    parser.add_argument('--json', action='store_true', help='JSON output')
    
    args = parser.parse_args()
    
    # Get address
    address = args.address
    if not address and args.key_file:
        with open(args.key_file, 'r') as f:
            data = json.load(f)
            key = data.get('private_key', data.get('key', ''))
            if not key.startswith('0x'):
                key = '0x' + key
            account = Account.from_key(key)
            address = account.address
    
    if not address:
        print("Error: provide --address or --key-file")
        return 1
    
    uri, output_path = generate_qr(address, args.name, args.chain, args.output)
    
    if args.json:
        print(json.dumps({
            "success": True,
            "address": address,
            "displayName": args.name,
            "chain": args.chain,
            "uri": uri,
            "qrFile": output_path
        }))
    else:
        print(f"✅ QR Code generated!")
        print(f"   Address: {address}")
        print(f"   Name: {args.name}")
        print(f"   Chain: {args.chain}")
        print(f"   URI: {uri}")
        print(f"   File: {output_path}")
    
    return 0

if __name__ == '__main__':
    exit(main())

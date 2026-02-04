#!/usr/bin/env python3
"""
Read an AgentPay QR code and add contact to phone book.

Supports:
  - QR code image files (PNG/JPG)
  - Direct URI string input
  - URI format: agentpay:<address>?name=<displayName>&chain=<chain>

Usage:
  python3 agent-qr-read.py --image alice-qr.png
  python3 agent-qr-read.py --uri "agentpay:0x123...?name=Alice&chain=base"
"""
import argparse
import json
import os
import re
from urllib.parse import urlparse, parse_qs
from web3 import Web3

PHONEBOOK_FILE = "data/phonebook.json"

def parse_agentpay_uri(uri: str) -> dict:
    """Parse agentpay URI → {address, name, chain}"""
    # agentpay:0xABC...?name=Alice&chain=base
    match = re.match(r'^agentpay:(0x[a-fA-F0-9]{40})\??(.*)$', uri)
    if not match:
        raise ValueError(f"Invalid AgentPay URI: {uri}")
    
    address = Web3.to_checksum_address(match.group(1))
    params_str = match.group(2)
    
    # Parse query params
    params = {}
    if params_str:
        for pair in params_str.split('&'):
            if '=' in pair:
                k, v = pair.split('=', 1)
                params[k] = v
    
    return {
        "address": address,
        "name": params.get("name", "Unknown"),
        "chain": params.get("chain", "base")
    }

def read_qr_from_image(image_path: str) -> str:
    """Extract QR code data from image"""
    try:
        from pyzbar.pyzbar import decode
        from PIL import Image
        
        img = Image.open(image_path)
        codes = decode(img)
        
        if not codes:
            raise ValueError("No QR code found in image")
        
        return codes[0].data.decode('utf-8')
    
    except ImportError:
        # Fallback: try with qrcode reader
        # If pyzbar not available, try opencv
        try:
            import cv2
            detector = cv2.QRCodeDetector()
            data, _, _ = detector.detectAndDecode(cv2.imread(image_path))
            if data:
                return data
        except ImportError:
            pass
        
        # Last resort: try reading with qreader
        raise ImportError(
            "QR reading requires pyzbar or opencv.\n"
            "Install: pip install pyzbar Pillow\n"
            "Or: pip install opencv-python\n"
            "Or use --uri flag with the URI string directly."
        )

def load_phonebook() -> dict:
    """Load local phone book"""
    if os.path.exists(PHONEBOOK_FILE):
        with open(PHONEBOOK_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_phonebook(phonebook: dict):
    """Save phone book"""
    os.makedirs(os.path.dirname(PHONEBOOK_FILE) or '.', exist_ok=True)
    with open(PHONEBOOK_FILE, 'w', encoding='utf-8') as f:
        json.dump(phonebook, f, indent=2, ensure_ascii=False)

def add_contact(name: str, address: str, chain: str = "base") -> dict:
    """Add contact to phone book"""
    phonebook = load_phonebook()
    
    import datetime
    phonebook[name] = {
        "address": address,
        "chain": chain,
        "addedAt": datetime.datetime.utcnow().isoformat(),
        "addedVia": "qr"
    }
    
    save_phonebook(phonebook)
    return phonebook[name]

def main():
    parser = argparse.ArgumentParser(description='Read AgentPay QR code')
    parser.add_argument('--image', '-i', help='QR code image file')
    parser.add_argument('--uri', '-u', help='AgentPay URI string directly')
    parser.add_argument('--no-save', action='store_true', help="Don't save to phone book")
    parser.add_argument('--json', action='store_true', help='JSON output')
    
    args = parser.parse_args()
    
    if not args.image and not args.uri:
        print("Error: provide --image or --uri")
        return 1
    
    try:
        # Get URI
        if args.uri:
            uri = args.uri
        else:
            uri = read_qr_from_image(args.image)
        
        # Parse
        info = parse_agentpay_uri(uri)
        
        # Save to phone book
        if not args.no_save:
            add_contact(info["name"], info["address"], info["chain"])
        
        if args.json:
            print(json.dumps({
                "success": True,
                "uri": uri,
                **info,
                "saved": not args.no_save
            }))
        else:
            print(f"✅ Contact added!")
            print(f"   Name: {info['name']}")
            print(f"   Address: {info['address']}")
            print(f"   Chain: {info['chain']}")
            if not args.no_save:
                print(f"   Saved to: {PHONEBOOK_FILE}")
        
        return 0
    
    except Exception as e:
        if args.json:
            print(json.dumps({"success": False, "error": str(e)}))
        else:
            print(f"❌ Error: {e}")
        return 1

if __name__ == '__main__':
    exit(main())

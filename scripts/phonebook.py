#!/usr/bin/env python3
"""
Local phone book — maps names to agent addresses.
This is what makes "pay Alice" work without remembering addresses.

Usage:
  python3 phonebook.py list
  python3 phonebook.py add --name Alice --address 0x...
  python3 phonebook.py get --name Alice
  python3 phonebook.py remove --name Alice
  python3 phonebook.py search --query coffee
"""
import argparse
import json
import os
import datetime
from web3 import Web3

PHONEBOOK_FILE = "data/phonebook.json"

class PhoneBook:
    def __init__(self, filepath=PHONEBOOK_FILE):
        self.filepath = filepath
        self.contacts = self._load()
    
    def _load(self) -> dict:
        if os.path.exists(self.filepath):
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save(self):
        os.makedirs(os.path.dirname(self.filepath) or '.', exist_ok=True)
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(self.contacts, f, indent=2, ensure_ascii=False)
    
    def add(self, name: str, address: str, chain: str = "base", via: str = "manual"):
        if not Web3.is_address(address):
            raise ValueError(f"Invalid address: {address}")
        address = Web3.to_checksum_address(address)
        
        self.contacts[name] = {
            "address": address,
            "chain": chain,
            "addedAt": datetime.datetime.utcnow().isoformat(),
            "addedVia": via
        }
        self._save()
        return address
    
    def get(self, name: str) -> str:
        """Get address by name. Also accepts raw addresses."""
        if name in self.contacts:
            return self.contacts[name]["address"]
        if Web3.is_address(name):
            return Web3.to_checksum_address(name)
        raise KeyError(f"Contact not found: {name}")
    
    def remove(self, name: str) -> bool:
        if name in self.contacts:
            del self.contacts[name]
            self._save()
            return True
        return False
    
    def list_all(self) -> dict:
        return self.contacts
    
    def search(self, query: str) -> dict:
        q = query.lower()
        return {k: v for k, v in self.contacts.items() if q in k.lower()}

def main():
    parser = argparse.ArgumentParser(description='AgentPay Phone Book')
    parser.add_argument('action', choices=['list', 'add', 'get', 'remove', 'search'])
    parser.add_argument('--name', '-n', help='Contact name')
    parser.add_argument('--address', '-a', help='Agent address')
    parser.add_argument('--query', '-q', help='Search query')
    parser.add_argument('--json', action='store_true')
    
    args = parser.parse_args()
    pb = PhoneBook()
    
    try:
        if args.action == 'add':
            addr = pb.add(args.name, args.address)
            if args.json:
                print(json.dumps({"success": True, "name": args.name, "address": addr}))
            else:
                print(f"✅ {args.name} → {addr}")
        
        elif args.action == 'get':
            addr = pb.get(args.name)
            if args.json:
                print(json.dumps({"success": True, "name": args.name, "address": addr}))
            else:
                print(f"{args.name}: {addr}")
        
        elif args.action == 'remove':
            ok = pb.remove(args.name)
            if args.json:
                print(json.dumps({"success": ok}))
            else:
                print(f"✅ Removed {args.name}" if ok else f"❌ Not found: {args.name}")
        
        elif args.action == 'list':
            contacts = pb.list_all()
            if args.json:
                print(json.dumps({"success": True, "contacts": contacts, "count": len(contacts)}))
            else:
                print(f"📇 Contacts ({len(contacts)}):\n")
                for name, info in contacts.items():
                    print(f"  {name}: {info['address']} ({info.get('chain', 'base')})")
        
        elif args.action == 'search':
            results = pb.search(args.query)
            if args.json:
                print(json.dumps({"success": True, "results": results, "count": len(results)}))
            else:
                print(f"🔍 '{args.query}' ({len(results)} found):\n")
                for name, info in results.items():
                    print(f"  {name}: {info['address']}")
    
    except Exception as e:
        if args.json:
            print(json.dumps({"success": False, "error": str(e)}))
        else:
            print(f"❌ {e}")
        return 1

if __name__ == '__main__':
    exit(main())

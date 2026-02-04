#!/usr/bin/env python3
"""
USDC Wallet Contacts Manager
Solve the problem: "How do you know someone's address?"
"""
import json
import os
import argparse
from pathlib import Path
from web3 import Web3

CONTACTS_FILE = "data/contacts.json"

class ContactsManager:
    def __init__(self, contacts_file=CONTACTS_FILE):
        self.contacts_file = contacts_file
        self.contacts = self._load_contacts()
    
    def _load_contacts(self) -> dict:
        """Load contacts from JSON file"""
        if os.path.exists(self.contacts_file):
            with open(self.contacts_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_contacts(self):
        """Save contacts to JSON file"""
        os.makedirs(os.path.dirname(self.contacts_file) or '.', exist_ok=True)
        with open(self.contacts_file, 'w', encoding='utf-8') as f:
            json.dump(self.contacts, f, indent=2, ensure_ascii=False)
    
    def add(self, name: str, address: str) -> bool:
        """Add a new contact"""
        # Validate Ethereum address
        if not Web3.is_address(address):
            raise ValueError(f"Invalid Ethereum address: {address}")
        
        # Checksum address
        address = Web3.to_checksum_address(address)
        
        self.contacts[name] = address
        self._save_contacts()
        return True
    
    def get(self, name: str) -> str:
        """Get address by name"""
        if name in self.contacts:
            return self.contacts[name]
        
        # Check if input is already an address
        if Web3.is_address(name):
            return Web3.to_checksum_address(name)
        
        # TODO: Try ENS resolution
        # if name.endswith('.eth'):
        #     return resolve_ens(name)
        
        raise KeyError(f"Contact '{name}' not found")
    
    def remove(self, name: str) -> bool:
        """Remove a contact"""
        if name in self.contacts:
            del self.contacts[name]
            self._save_contacts()
            return True
        return False
    
    def list(self) -> dict:
        """List all contacts"""
        return self.contacts
    
    def search(self, query: str) -> dict:
        """Search contacts by name (case-insensitive)"""
        query = query.lower()
        return {
            name: addr 
            for name, addr in self.contacts.items() 
            if query in name.lower()
        }

def main():
    parser = argparse.ArgumentParser(description='Manage USDC wallet contacts')
    parser.add_argument('action', choices=['add', 'get', 'remove', 'list', 'search'],
                       help='Action to perform')
    parser.add_argument('--name', help='Contact name')
    parser.add_argument('--address', help='Ethereum address')
    parser.add_argument('--query', help='Search query')
    parser.add_argument('--json', action='store_true', help='Output JSON')
    
    args = parser.parse_args()
    manager = ContactsManager()
    
    try:
        if args.action == 'add':
            if not args.name or not args.address:
                print("Error: --name and --address required for add")
                return 1
            
            manager.add(args.name, args.address)
            
            if args.json:
                print(json.dumps({"success": True, "name": args.name, "address": args.address}))
            else:
                print(f"✅ Added contact: {args.name} → {args.address}")
        
        elif args.action == 'get':
            if not args.name:
                print("Error: --name required for get")
                return 1
            
            address = manager.get(args.name)
            
            if args.json:
                print(json.dumps({"success": True, "name": args.name, "address": address}))
            else:
                print(f"{args.name}: {address}")
        
        elif args.action == 'remove':
            if not args.name:
                print("Error: --name required for remove")
                return 1
            
            success = manager.remove(args.name)
            
            if args.json:
                print(json.dumps({"success": success}))
            else:
                if success:
                    print(f"✅ Removed contact: {args.name}")
                else:
                    print(f"❌ Contact not found: {args.name}")
        
        elif args.action == 'list':
            contacts = manager.list()
            
            if args.json:
                print(json.dumps({"success": True, "contacts": contacts, "count": len(contacts)}))
            else:
                print(f"📇 Contacts ({len(contacts)}):\\n")
                for name, address in contacts.items():
                    print(f"  {name}: {address}")
        
        elif args.action == 'search':
            if not args.query:
                print("Error: --query required for search")
                return 1
            
            results = manager.search(args.query)
            
            if args.json:
                print(json.dumps({"success": True, "results": results, "count": len(results)}))
            else:
                print(f"🔍 Search results for '{args.query}' ({len(results)}):\\n")
                for name, address in results.items():
                    print(f"  {name}: {address}")
        
        return 0
    
    except Exception as e:
        if args.json:
            print(json.dumps({"success": False, "error": str(e)}))
        else:
            print(f"❌ Error: {e}")
        return 1

if __name__ == '__main__':
    exit(main())

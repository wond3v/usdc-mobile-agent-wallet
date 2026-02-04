#!/usr/bin/env python3
"""
Example: How to integrate USDC wallet scripts with an AI agent
"""
import subprocess
import json
import re

class USDCWalletAgent:
    """Example agent integration for USDC operations"""
    
    def __init__(self, default_network='base-sepolia', wallet_file='.secrets/wallet.json'):
        self.default_network = default_network
        self.wallet_file = wallet_file
        
    def parse_command(self, user_input: str) -> dict:
        """Parse natural language commands"""
        user_input = user_input.lower()
        
        # Check balance
        if 'balance' in user_input or 'how much' in user_input:
            # Extract address if present
            addr_match = re.search(r'0x[a-fA-F0-9]{40}', user_input)
            return {
                'action': 'balance',
                'address': addr_match.group(0) if addr_match else None
            }
        
        # Send USDC
        if 'send' in user_input or 'transfer' in user_input or 'pay' in user_input:
            # Extract amount
            amount_match = re.search(r'(\d+\.?\d*)\s*usdc', user_input)
            # Extract address
            addr_match = re.search(r'0x[a-fA-F0-9]{40}', user_input)
            
            return {
                'action': 'transfer',
                'amount': float(amount_match.group(1)) if amount_match else None,
                'to': addr_match.group(0) if addr_match else None
            }
        
        # Transaction history
        if 'history' in user_input or 'transactions' in user_input or 'recent' in user_input:
            return {'action': 'history'}
        
        # Monitor
        if 'watch' in user_input or 'monitor' in user_input or 'alert' in user_input:
            return {'action': 'monitor'}
        
        return {'action': 'unknown'}
    
    def check_balance(self, address: str) -> dict:
        """Check USDC balance"""
        result = subprocess.run([
            'python3', 'scripts/usdc-balance.py',
            '--address', address,
            '--network', self.default_network,
            '--json'
        ], capture_output=True, text=True)
        
        return json.loads(result.stdout)
    
    def transfer_usdc(self, to: str, amount: float) -> dict:
        """Transfer USDC"""
        result = subprocess.run([
            'python3', 'scripts/usdc-transfer.py',
            '--to', to,
            '--amount', str(amount),
            '--network', self.default_network,
            '--key-file', self.wallet_file,
            '--json'
        ], capture_output=True, text=True)
        
        return json.loads(result.stdout)
    
    def get_history(self, address: str, limit: int = 10) -> dict:
        """Get transaction history"""
        result = subprocess.run([
            'python3', 'scripts/usdc-history.py',
            '--address', address,
            '--network', self.default_network,
            '--limit', str(limit),
            '--json'
        ], capture_output=True, text=True)
        
        return json.loads(result.stdout)
    
    def respond(self, user_input: str, user_address: str = None) -> str:
        """Generate response to user input"""
        parsed = self.parse_command(user_input)
        
        if parsed['action'] == 'balance':
            address = parsed['address'] or user_address
            if not address:
                return "Please provide your address to check balance."
            
            result = self.check_balance(address)
            if result['success']:
                return f"Your USDC balance: {result['usdc_balance']:.6f} USDC\n" \
                       f"ETH for gas: {result['eth_balance']:.6f} ETH"
            else:
                return f"Error checking balance: {result['error']}"
        
        elif parsed['action'] == 'transfer':
            if not parsed['amount'] or not parsed['to']:
                return "Please specify amount and recipient address.\n" \
                       "Example: 'Send 10 USDC to 0x742d35...'"
            
            # Confirm with user (in real implementation)
            confirmation = f"Confirm transfer:\n" \
                          f"  Amount: {parsed['amount']} USDC\n" \
                          f"  To: {parsed['to']}\n" \
                          f"  Network: {self.default_network}\n" \
                          f"Proceed? (This is a simulation)"
            
            # In real implementation, wait for user confirmation
            # then execute: self.transfer_usdc(parsed['to'], parsed['amount'])
            
            return confirmation
        
        elif parsed['action'] == 'history':
            if not user_address:
                return "Please provide your address to view history."
            
            result = self.get_history(user_address, limit=5)
            if result['success']:
                response = f"Recent transactions ({len(result['transactions'])}):\n\n"
                for tx in result['transactions']:
                    direction = '←' if tx['direction'] == 'in' else '→'
                    response += f"{direction} {tx['value']:.6f} USDC\n"
                    response += f"   {tx['direction'].upper()}: {tx['counterparty'][:10]}...\n"
                    response += f"   Block: {tx['block']}\n\n"
                return response
            else:
                return f"Error fetching history: {result['error']}"
        
        elif parsed['action'] == 'monitor':
            return "To monitor for incoming USDC, run:\n" \
                   f"python3 scripts/usdc-monitor.py --address <your_address> --network {self.default_network}"
        
        else:
            return "I can help you with:\n" \
                   "• Check balance: 'What's my USDC balance?'\n" \
                   "• Send USDC: 'Send 10 USDC to 0x...'\n" \
                   "• View history: 'Show my transactions'\n" \
                   "• Monitor: 'Watch my wallet'"


def demo():
    """Demo the agent integration"""
    agent = USDCWalletAgent()
    
    # Example address (replace with real address for testing)
    user_address = "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
    
    print("🤖 USDC Wallet Agent Demo\n")
    
    # Example conversations
    examples = [
        "What's my USDC balance?",
        "Send 10 USDC to 0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
        "Show my recent transactions",
        "Watch my wallet for incoming payments"
    ]
    
    for user_input in examples:
        print(f"👤 User: {user_input}")
        response = agent.respond(user_input, user_address)
        print(f"🤖 Agent: {response}\n")
        print("-" * 60 + "\n")


if __name__ == '__main__':
    demo()

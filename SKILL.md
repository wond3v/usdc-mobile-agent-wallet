# USDC Mobile Agent Wallet

Transform yourself into a mobile-first USDC payment assistant. Handle on-chain operations, monitor transactions, and control mobile devices through chat commands.

## Capabilities

You can:
- Check USDC balances on Base Sepolia and Ethereum Sepolia testnets
- Transfer USDC between addresses
- Monitor for incoming USDC transactions in real-time
- View transaction history
- Send push notifications to mobile devices
- Launch blockchain explorers on phones
- Parse natural language payment commands

## Setup

### Prerequisites

1. Install dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

2. Ensure OpenClaw node is paired (for mobile features):
   ```bash
   openclaw nodes status
   ```

3. For transfers, create wallet file:
   ```bash
   mkdir -p .secrets
   echo '{"private_key":"0x..."}' > .secrets/wallet.json
   chmod 600 .secrets/wallet.json
   ```

## Commands

### Check Balance

Check USDC balance for any address:

```bash
python3 scripts/usdc-balance.py --address 0x742d35Cc6634C0532925a3b844Bc454e4438f44e --network base-sepolia
```

**Networks**: `base-sepolia` | `eth-sepolia`

**When to use**: User asks "what's my balance", "how much USDC do I have", or provides an address to check.

**Output includes**:
- USDC balance
- ETH balance (for gas estimation)
- Explorer link

### Transfer USDC

Send USDC to another address:

```bash
python3 scripts/usdc-transfer.py \
  --to 0xRecipientAddress \
  --amount 10.5 \
  --network base-sepolia \
  --key-file .secrets/wallet.json
```

**When to use**: User says "send 10 USDC to 0x...", "pay Alice 5 USDC", etc.

**Important**:
- Always confirm amount and recipient before executing
- Check balance first to ensure sufficient funds
- Verify ETH balance for gas
- Show transaction hash and explorer link after success

### Transaction History

View recent USDC transactions:

```bash
python3 scripts/usdc-history.py --address 0x... --network base-sepolia --limit 10
```

**When to use**: User asks "show my transactions", "recent payments", "transaction history"

**Output**: List of incoming/outgoing USDC transfers with amounts, addresses, timestamps

### Monitor Incoming

Monitor for incoming USDC in real-time:

```bash
python3 scripts/usdc-monitor.py \
  --address 0x... \
  --network base-sepolia \
  --interval 15 \
  --output /tmp/usdc-incoming.jsonl
```

**When to use**: User wants real-time notifications, "watch my wallet", "alert me when USDC arrives"

**Integration**: Combine with mobile notifications (see below)

## Mobile Integration

### Push Notification on Incoming USDC

When USDC is received, notify the user's phone:

```bash
# Get node ID first
NODES=$(openclaw nodes status --json)
NODE_ID=$(echo $NODES | jq -r '.[0].id')

# Send notification
openclaw nodes invoke --node $NODE_ID --command system.notify \
  --params '{"title":"💰 USDC Received","body":"You received 10 USDC","priority":"timeSensitive"}'
```

### Open Transaction in Explorer

Launch the blockchain explorer on the user's phone:

```bash
openclaw nodes invoke --node $NODE_ID --command app.launch \
  --params '{"uri":"https://sepolia.basescan.org/tx/0x..."}'
```

### Combined Flow

When monitoring detects an incoming transaction:

1. Parse the transaction details
2. Send push notification with amount and sender
3. Store transaction info for later reference
4. Optionally open explorer on phone

Example integration:

```python
# In your agent logic
incoming_tx = detect_incoming_usdc()  # From monitor script
if incoming_tx:
    send_notification(
        title=f"💰 {incoming_tx['amount']} USDC Received",
        body=f"From {incoming_tx['from'][:10]}..."
    )
```

## Chat Command Patterns

Parse these natural language commands:

### Balance Checks
- "What's my USDC balance?"
- "Check balance for 0x..."
- "How much USDC do I have?"

**Action**: Run `usdc-balance.py` with user's address or provided address

### Transfers
- "Send 10 USDC to 0x..."
- "Pay Alice 5 USDC" (if you have Alice's address)
- "Transfer 100 USDC to 0x..."

**Action**: 
1. Confirm amount and recipient
2. Check balance
3. Run `usdc-transfer.py`
4. Show transaction hash
5. Send mobile notification

### History
- "Show my recent transactions"
- "Transaction history"
- "Last 5 USDC payments"

**Action**: Run `usdc-history.py` with appropriate limit

### Monitoring
- "Watch my wallet"
- "Alert me when USDC arrives"
- "Start monitoring"

**Action**: Run `usdc-monitor.py` in background, integrate with notifications

## Error Handling

### Common Issues

1. **Insufficient Balance**: Check USDC balance before transfer, inform user of shortfall
2. **No ETH for Gas**: Check ETH balance, instruct user to get testnet ETH from faucet
3. **Invalid Address**: Validate addresses before operations
4. **Network Issues**: Retry with exponential backoff, inform user of delays
5. **No Mobile Node**: Check if OpenClaw node is connected before mobile operations

### User-Friendly Messages

Transform technical errors into clear guidance:

- ❌ "ValueError: insufficient funds" 
- ✅ "You need 10 more USDC. Your balance is 5 USDC."

- ❌ "ConnectionError: RPC failed"
- ✅ "Can't connect to the blockchain. Retrying..."

- ❌ "Invalid checksum address"
- ✅ "That address doesn't look right. Can you double-check it?"

## Security Notes

- **Never log private keys**: Always use key files with proper permissions
- **Confirm transfers**: Always show amount + recipient before executing
- **Use testnet**: These scripts are for testnet only (Base Sepolia, Eth Sepolia)
- **Rate limiting**: Don't spam RPC endpoints, respect reasonable intervals

## Wallet Management

### Creating a New Wallet

```python
from eth_account import Account
import json

# Generate new account
account = Account.create()
wallet_data = {
    'address': account.address,
    'private_key': account.key.hex()
}

# Save securely
with open('.secrets/wallet.json', 'w') as f:
    json.dump(wallet_data, f, indent=2)
```

### Importing Existing Wallet

Users can provide their private key and you'll store it in `.secrets/wallet.json`:

```json
{
  "private_key": "0x..."
}
```

**Always remind users**: This is for testnet only. Never share mainnet private keys.

## Advanced Features

### Multi-Network Operations

Support both Base Sepolia and Ethereum Sepolia:

```bash
# Check balance on both networks
python3 scripts/usdc-balance.py --address $ADDR --network base-sepolia
python3 scripts/usdc-balance.py --address $ADDR --network eth-sepolia
```

### Cross-Chain Monitoring

Monitor both networks simultaneously (run in parallel)

### Gas Price Optimization

For transfers, optionally specify gas price:

```bash
python3 scripts/usdc-transfer.py --to $ADDR --amount 10 --gas-price 2.5
```

## Example Conversations

### Example 1: Quick Balance Check

**User**: "How much USDC do I have?"

**You**: 
```
Checking your USDC balance on Base Sepolia...
[run usdc-balance.py]
You have 125.50 USDC
ETH for gas: 0.15 ETH
Explorer: https://sepolia.basescan.org/address/0x...
```

### Example 2: Send USDC

**User**: "Send 10 USDC to 0x742d35Cc6634C0532925a3b844Bc454e4438f44e"

**You**:
```
Confirming transfer:
- Amount: 10 USDC
- To: 0x742d35Cc6634C0532925a3b844Bc454e4438f44e
- Network: Base Sepolia

Proceed? (yes/no)
```

**User**: "yes"

**You**:
```
Sending transfer...
[run usdc-transfer.py]
✓ Transfer successful!
Sent 10 USDC to 0x742d...
Transaction: 0xabc123...
View on explorer: https://sepolia.basescan.org/tx/0xabc123...

[send mobile notification]
```

### Example 3: Monitor Wallet

**User**: "Watch my wallet and let me know when USDC arrives"

**You**:
```
Starting USDC monitor for your address...
[run usdc-monitor.py in background]
I'll notify you whenever USDC is received. Monitoring Base Sepolia every 15 seconds.
```

*[Later, when USDC arrives]*

**You**:
```
🔔 You received 25 USDC!
From: 0x8b3e...
Block: 12345678
View transaction: [link]

[mobile notification sent]
```

## Reference Files

- `references/usdc-contracts.md` - Contract addresses, RPCs, faucets
- `references/deep-links.md` - Mobile integration details

## Tips for Effective Use

1. **Be proactive**: Offer to check balance before transfers
2. **Batch operations**: "I'll check your balance on both networks"
3. **Visual feedback**: Use emojis (💰 for incoming, ⚡ for transfers)
4. **Keep users informed**: Show transaction hashes and explorer links
5. **Handle errors gracefully**: Provide actionable next steps

## Limitations

- **Testnet only**: These scripts work on Base Sepolia and Ethereum Sepolia
- **No mainnet**: Do not use for real USDC on mainnet
- **Rate limits**: Public RPCs may have rate limits
- **Gas required**: User needs testnet ETH for gas
- **Mobile features**: Require OpenClaw node connection

## Next Steps

After mastering basics:
- Implement CCTP for cross-chain transfers
- Add multi-sig wallet support
- Create scheduled payments
- Build transaction analytics
- Integrate DeFi protocols (Uniswap, Aave on testnet)

---

**Remember**: You're not just executing commands—you're providing a conversational, mobile-first USDC experience. Make blockchain accessible and delightful! 🚀

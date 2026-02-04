# Mobile Deep Links Reference

## OpenClaw Node Commands

### Push Notifications

Send a push notification to the mobile device:

```bash
openclaw nodes invoke --node <node-id> --command system.notify \
  --params '{"title":"USDC Received","body":"You received 10 USDC from 0x123...","priority":"timeSensitive"}'
```

**Parameters:**
- `title`: Notification title
- `body`: Notification message
- `priority`: `passive` | `active` | `timeSensitive`
- `sound`: (optional) notification sound

### App Launch / Deep Links

Launch an app or URL on the mobile device:

```bash
openclaw nodes invoke --node <node-id> --command app.launch \
  --params '{"uri":"https://sepolia.basescan.org/tx/0x..."}'
```

**Common URIs:**
- `https://sepolia.basescan.org/tx/<tx_hash>` - View transaction
- `https://sepolia.basescan.org/address/<address>` - View address
- `https://app.uniswap.org` - Open Uniswap
- Custom app schemes (if supported)

## Blockchain Explorer Deep Links

### Base Sepolia (basescan.org)
- **Transaction**: `https://sepolia.basescan.org/tx/{tx_hash}`
- **Address**: `https://sepolia.basescan.org/address/{address}`
- **Token**: `https://sepolia.basescan.org/token/{token_address}`
- **Block**: `https://sepolia.basescan.org/block/{block_number}`

### Ethereum Sepolia (etherscan.io)
- **Transaction**: `https://sepolia.etherscan.io/tx/{tx_hash}`
- **Address**: `https://sepolia.etherscan.io/address/{address}`
- **Token**: `https://sepolia.etherscan.io/token/{token_address}`
- **Block**: `https://sepolia.etherscan.io/block/{block_number}`

## Wallet Deep Links

### MetaMask
- **Send**: `https://metamask.app.link/send/{address}@{chain_id}?value={amount}`
- **Add Token**: `https://metamask.app.link/add-token?address={token_address}`

### Coinbase Wallet
- **Open**: `cbwallet://`
- **Deeplink**: `https://go.cb-w.com/`

### Rainbow
- **Send**: `https://rainbow.me/send?address={address}&amount={amount}`

## Usage Examples

### Notify on Incoming USDC

```python
import subprocess
import json

def notify_incoming_usdc(node_id, amount, from_address, tx_hash):
    params = {
        "title": "💰 USDC Received",
        "body": f"You received {amount} USDC from {from_address[:8]}...",
        "priority": "timeSensitive",
        "sound": "default"
    }
    
    subprocess.run([
        'openclaw', 'nodes', 'invoke',
        '--node', node_id,
        '--command', 'system.notify',
        '--params', json.dumps(params)
    ])
```

### Open Transaction in Explorer

```python
def open_tx_explorer(node_id, tx_hash, network='base-sepolia'):
    explorers = {
        'base-sepolia': 'https://sepolia.basescan.org',
        'eth-sepolia': 'https://sepolia.etherscan.io'
    }
    
    uri = f"{explorers[network]}/tx/{tx_hash}"
    params = {"uri": uri}
    
    subprocess.run([
        'openclaw', 'nodes', 'invoke',
        '--node', node_id,
        '--command', 'app.launch',
        '--params', json.dumps(params)
    ])
```

## Combined Flow Example

When USDC is received:
1. Monitor detects incoming transaction
2. Send push notification with amount and sender
3. When user taps notification, open transaction in explorer
4. Optional: Store notification action to trigger explorer launch

```python
# Monitor script integration
def on_usdc_received(tx_data, node_id):
    # 1. Send notification
    notify_incoming_usdc(
        node_id,
        tx_data['amount'],
        tx_data['from'],
        tx_data['tx_hash']
    )
    
    # 2. (Optional) Auto-open explorer after delay
    time.sleep(2)
    open_tx_explorer(node_id, tx_data['tx_hash'])
```

## Testing

Use OpenClaw node status to verify connection:

```bash
openclaw nodes status
```

List available nodes:

```bash
openclaw nodes list
```

Test notification:

```bash
openclaw nodes invoke --node <id> --command system.notify \
  --params '{"title":"Test","body":"OpenClaw is connected!"}'
```

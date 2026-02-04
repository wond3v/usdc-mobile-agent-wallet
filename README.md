# 🤖💰 USDC Mobile Agent Wallet

**An AI agent that manages your USDC wallet through chat, with mobile-first notifications and controls.**

> Turn any AI assistant into a powerful, conversational USDC payment system that lives in your pocket.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## 🎯 What Is This?

USDC Mobile Agent Wallet bridges three powerful technologies:

1. **🧠 AI Agents** (via OpenClaw) - Natural language interface
2. **⛓️ On-Chain Operations** (Base & Ethereum) - Real USDC transactions
3. **📱 Mobile Control** (via ClawBot nodes) - Push notifications & deep links

The result? **Chat with your AI, control your crypto wallet, get real-time mobile alerts.**

## ✨ Key Features

### 💬 Conversational Payments
- "Send 10 USDC to Alice" → Agent executes transfer
- "What's my balance?" → Instant on-chain check
- "Show recent transactions" → Complete history

### 📲 Mobile-First Experience
- Push notifications when USDC arrives
- Tap notification → Open blockchain explorer
- Control wallet from any chat platform (WhatsApp, Telegram, Discord)

### ⛓️ Multi-Chain Support
- Base Sepolia (Layer 2, low fees)
- Ethereum Sepolia (Testnet)
- Ready for CCTP cross-chain transfers

### 🔒 Secure & Transparent
- Non-custodial (you control your keys)
- All transactions on-chain
- Open-source and auditable

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
│                   (WhatsApp / Telegram / CLI)                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      OpenClaw AI Agent                          │
│                  (Natural Language Processing)                  │
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │  Parse Commands  │  │  Execute Scripts │  │ Error Handler│ │
│  └──────────────────┘  └──────────────────┘  └──────────────┘ │
└────────────┬────────────────────────┬────────────────┬─────────┘
             │                        │                │
             ▼                        ▼                ▼
┌─────────────────────┐  ┌──────────────────────┐  ┌──────────────┐
│  Python Scripts     │  │   Web3.py Library    │  │  ClawBot Node│
│                     │  │                      │  │   (Mobile)   │
│  • Balance Check    │  │  • Smart Contracts   │  │              │
│  • Transfer         │  │  • Event Listening   │  │ • Notify     │
│  • History          │  │  • Transaction Sign  │  │ • Launch App │
│  • Monitor          │  │                      │  │ • Vibrate    │
└─────────────────────┘  └──────────┬───────────┘  └──────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │     Blockchain Networks       │
                    │                               │
                    │  ┌─────────────────────────┐  │
                    │  │   Base Sepolia (L2)     │  │
                    │  │   USDC: 0x036CbD...     │  │
                    │  └─────────────────────────┘  │
                    │                               │
                    │  ┌─────────────────────────┐  │
                    │  │  Ethereum Sepolia       │  │
                    │  │  USDC: 0x1c7D4B1...     │  │
                    │  └─────────────────────────┘  │
                    └───────────────────────────────┘
```

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/wond3v/usdc-mobile-agent-wallet.git
cd usdc-mobile-agent-wallet

# Install dependencies
pip3 install -r requirements.txt

# Verify installation
python3 scripts/usdc-balance.py --help
```

### Setup Wallet

```bash
# Create secrets directory
mkdir -p .secrets

# Generate new wallet or import existing
echo '{"private_key":"0xYOUR_PRIVATE_KEY_HERE"}' > .secrets/wallet.json
chmod 600 .secrets/wallet.json
```

**⚠️ Important**: This is for testnet only. Never use mainnet keys.

### Get Testnet Tokens

You'll need:
1. **Testnet ETH** (for gas):
   - Base Sepolia: https://www.coinbase.com/faucets/base-ethereum-goerli-faucet
   - Ethereum Sepolia: https://sepoliafaucet.com

2. **Testnet USDC**:
   - Use Circle's testnet faucet or swap testnet ETH on testnet DEXs

### First Transaction

```bash
# Check your balance
python3 scripts/usdc-balance.py \
  --address 0xYourAddress \
  --network base-sepolia

# Send USDC
python3 scripts/usdc-transfer.py \
  --to 0xRecipientAddress \
  --amount 10 \
  --network base-sepolia \
  --key-file .secrets/wallet.json

# View transaction history
python3 scripts/usdc-history.py \
  --address 0xYourAddress \
  --network base-sepolia
```

## 📱 Mobile Integration

### Connect OpenClaw Node

```bash
# Check node status
openclaw nodes status

# Pair new device
openclaw nodes pairing
```

### Enable Notifications

In your OpenClaw agent configuration, this skill automatically handles:
- 📬 Push notifications on incoming USDC
- 🔗 Deep links to blockchain explorers
- 📊 Balance updates

## 💡 Usage Examples

### Example 1: Natural Language Transfer

**Chat Interface:**
```
You: Send 25 USDC to 0x742d35Cc6634C0532925a3b844Bc454e4438f44e

Agent: I'll send 25 USDC on Base Sepolia.
       Recipient: 0x742d35...
       Your balance: 100 USDC
       Estimated gas: ~0.001 ETH
       
       Confirm? (yes/no)

You: yes

Agent: ✓ Transfer complete!
       Tx: 0xabc123def456...
       Block: 12345678
       🔗 View on explorer

[Mobile notification sent to your phone]
```

### Example 2: Real-Time Monitoring

**Setup:**
```bash
# Start monitoring in background
python3 scripts/usdc-monitor.py \
  --address 0xYourAddress \
  --network base-sepolia \
  --interval 15
```

**When USDC arrives:**
```
🔔 [Mobile Notification]
   💰 USDC Received
   You received 50 USDC from 0x8b3e4f2a...
   
   [Tap to view transaction]
```

### Example 3: Multi-Chain Balance

**Chat Interface:**
```
You: What's my balance on all networks?

Agent: Checking Base Sepolia and Ethereum Sepolia...

       Base Sepolia:
       • USDC: 125.50
       • ETH: 0.15 (gas)
       
       Ethereum Sepolia:
       • USDC: 75.00
       • ETH: 0.08 (gas)
       
       Total: 200.50 USDC across both networks
```

## 🎬 Demo Scenarios

### Scenario 1: Split Dinner Bill
**Context**: You had dinner with 3 friends. Total was $120, your share is $30.

```
You: Send 30 USDC to Alice for dinner

Agent: Sending 30 USDC to Alice (0x742d...)
       ✓ Done! Transaction: 0xabc...
       
       [Alice's phone buzzes with notification]
```

### Scenario 2: Freelance Payment
**Context**: Client wants to pay you for completed work.

```
You: Watch my wallet for incoming payments

Agent: Monitoring enabled. I'll notify you when USDC arrives.

[10 minutes later]
Agent: 💰 Payment received!
       Your client sent 500 USDC
       New balance: 625.50 USDC
       
       [Mobile notification with transaction link]
```

### Scenario 3: Quick Balance Check
**Context**: At checkout, need to verify you have enough USDC.

```
You: Do I have enough to pay 45 USDC?

Agent: Checking...
       Your balance: 75.50 USDC
       ✓ Yes! You have 75.50 USDC available.
       You'll have 30.50 left after payment.
```

## 🔧 Scripts Reference

### `usdc-balance.py`
Check USDC and ETH balance for any address.

```bash
python3 scripts/usdc-balance.py \
  --address 0x... \
  --network base-sepolia \
  [--json]
```

### `usdc-transfer.py`
Send USDC to another address.

```bash
python3 scripts/usdc-transfer.py \
  --to 0x... \
  --amount 10.5 \
  --network base-sepolia \
  --key-file .secrets/wallet.json \
  [--gas-price 2.5]
```

### `usdc-history.py`
View recent USDC transactions.

```bash
python3 scripts/usdc-history.py \
  --address 0x... \
  --network base-sepolia \
  [--limit 20] \
  [--json]
```

### `usdc-monitor.py`
Monitor for incoming USDC in real-time.

```bash
python3 scripts/usdc-monitor.py \
  --address 0x... \
  --network base-sepolia \
  [--interval 15] \
  [--output transactions.jsonl]
```

## 🌟 What Makes This Different?

### Traditional Crypto Wallets
- 😕 Complex interfaces with technical jargon
- 📱 Need to open app and navigate multiple screens
- 🔔 Limited or no notifications
- 🤖 No AI assistance

### USDC Mobile Agent Wallet
- ✅ Natural language: "Send 10 USDC to Alice"
- ✅ Works from any chat app you already use
- ✅ Real-time mobile notifications with deep links
- ✅ AI agent handles complexity for you
- ✅ Conversational, intelligent, mobile-first

**It's like having a personal blockchain assistant in your pocket.** 🚀

## 🛣️ Roadmap

### Phase 1: Foundation ✅
- [x] Basic USDC operations (balance, transfer, history)
- [x] Multi-network support (Base, Ethereum)
- [x] Mobile notifications via OpenClaw nodes
- [x] Natural language parsing

### Phase 2: Enhanced Features 🚧
- [ ] CCTP cross-chain transfers
- [ ] Scheduled payments
- [ ] Multi-signature wallet support
- [ ] Transaction analytics dashboard
- [ ] Voice commands

### Phase 3: DeFi Integration 🔮
- [ ] Uniswap integration (swap USDC)
- [ ] Aave integration (earn interest)
- [ ] Gas optimization strategies
- [ ] Batch transactions
- [ ] Portfolio tracking

### Phase 4: Production Ready 🎯
- [ ] Mainnet support (with extensive safety features)
- [ ] Hardware wallet integration
- [ ] Biometric authentication
- [ ] Multi-language support
- [ ] White-label SDK for other agents

## 📚 Documentation

- **[SKILL.md](SKILL.md)** - Complete agent instructions and examples
- **[references/usdc-contracts.md](references/usdc-contracts.md)** - Contract addresses and network info
- **[references/deep-links.md](references/deep-links.md)** - Mobile integration guide

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

```bash
# Install dev dependencies
pip3 install -r requirements.txt

# Run tests (coming soon)
# python3 -m pytest tests/

# Check code style
# black scripts/
# flake8 scripts/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Circle** - For USDC and CCTP documentation
- **Base** - For excellent Layer 2 infrastructure
- **OpenClaw** - For the AI agent framework
- **web3.py** - For Python Ethereum integration

## 📞 Contact & Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/wond3v/usdc-mobile-agent-wallet/issues)
- **Hackathon**: Built for USDC Hackathon 2026

## ⚠️ Disclaimer

This is experimental software built for educational and hackathon purposes. Currently configured for testnet only. Use mainnet functionality (when available) at your own risk. Always verify transactions before signing.

---

**Built with ❤️ for the USDC Hackathon** | Made possible by Circle, Base, and OpenClaw


#!/bin/bash
# Demo workflow showing all major features

set -e

echo "🤖 USDC Mobile Agent Wallet - Demo Workflow"
echo "==========================================="
echo ""

# Configuration
NETWORK="base-sepolia"
TEST_ADDRESS="0x742d35Cc6634C0532925a3b844Bc454e4438f44e"

echo "📍 Using Network: $NETWORK"
echo "📍 Test Address: $TEST_ADDRESS"
echo ""

# Check balance
echo "1️⃣  Checking USDC balance..."
python3 scripts/usdc-balance.py --address $TEST_ADDRESS --network $NETWORK
echo ""

# View transaction history
echo "2️⃣  Fetching transaction history (last 5)..."
python3 scripts/usdc-history.py --address $TEST_ADDRESS --network $NETWORK --limit 5
echo ""

# Example transfer (commented out - requires private key)
echo "3️⃣  Transfer example (requires wallet setup):"
echo "   python3 scripts/usdc-transfer.py \\"
echo "     --to 0xRecipientAddress \\"
echo "     --amount 10 \\"
echo "     --network $NETWORK \\"
echo "     --key-file .secrets/wallet.json"
echo ""

# Monitor example
echo "4️⃣  To monitor for incoming USDC:"
echo "   python3 scripts/usdc-monitor.py \\"
echo "     --address $TEST_ADDRESS \\"
echo "     --network $NETWORK \\"
echo "     --interval 15"
echo ""

echo "✅ Demo complete!"
echo ""
echo "📚 Next steps:"
echo "  • Set up your wallet in .secrets/wallet.json"
echo "  • Get testnet tokens from faucets (see README.md)"
echo "  • Connect OpenClaw node for mobile notifications"
echo "  • Try natural language commands through your AI agent"

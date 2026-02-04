# USDC Contract Addresses

## Testnet Addresses

### Base Sepolia
- **USDC Contract**: `0x036CbD53842c5426634e7929541eC2318f3dCF7e`
- **Chain ID**: 84532
- **RPC**: `https://sepolia.base.org`
- **Explorer**: https://sepolia.basescan.org
- **Faucet**: https://www.coinbase.com/faucets/base-ethereum-goerli-faucet

### Ethereum Sepolia
- **USDC Contract**: `0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238`
- **Chain ID**: 11155111
- **RPC**: `https://ethereum-sepolia-rpc.publicnode.com`
- **Alternative RPC**: `https://rpc.sepolia.org`
- **Explorer**: https://sepolia.etherscan.io
- **Faucet**: https://sepoliafaucet.com

## Getting Testnet Tokens

### ETH (for gas)
1. **Alchemy Faucet**: https://sepoliafaucet.com (Sepolia)
2. **Coinbase Faucet**: https://www.coinbase.com/faucets (Base Sepolia)
3. **QuickNode**: https://faucet.quicknode.com/ethereum/sepolia

### USDC (testnet)
Since USDC is an ERC-20 token, you'll need to:
1. Get testnet ETH first (for gas)
2. Use Circle's testnet faucet or bridge
3. Or swap testnet ETH for testnet USDC on testnet DEXs

**Note**: For hackathon purposes, you can also deploy a mock USDC contract or use existing testnet USDC from Circle's Cross-Chain Transfer Protocol (CCTP) sandbox.

## ERC-20 Standard Functions

USDC implements the standard ERC-20 interface:

```solidity
function balanceOf(address account) external view returns (uint256);
function transfer(address to, uint256 amount) external returns (bool);
function allowance(address owner, address spender) external view returns (uint256);
function approve(address spender, uint256 amount) external returns (bool);
function transferFrom(address from, address to, uint256 amount) external returns (bool);
function decimals() external view returns (uint8);  // USDC = 6 decimals
function symbol() external view returns (string);   // USDC
```

## Circle's CCTP (Cross-Chain Transfer Protocol)

For cross-chain USDC transfers, see:
- **Docs**: https://developers.circle.com/stablecoins/docs/cctp-getting-started
- **Testnet**: Available on Base Sepolia and Ethereum Sepolia
- **Token Messenger**: Contract that handles cross-chain burns/mints

## Additional Resources

- **Circle Developer Docs**: https://developers.circle.com
- **Base Documentation**: https://docs.base.org
- **Ethereum Sepolia Info**: https://ethereum.org/en/developers/docs/networks/

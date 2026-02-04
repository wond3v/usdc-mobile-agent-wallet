// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./AgentWallet.sol";
import "./AgentRegistry.sol";

/**
 * @title AgentWalletFactory
 * @notice CREATE2 factory — agent address → deterministic wallet
 *
 * Flow:
 *   1. Agent calls deployAndRegister() with its own EOA
 *   2. Factory deploys wallet via CREATE2 (salt = agent address)
 *   3. Factory registers agent in AgentRegistry
 *   4. Wallet address is deterministic — can be computed before deployment
 *
 * Why CREATE2?
 *   - Anyone can compute an agent's wallet address from just their EOA address
 *   - Wallet doesn't need to exist yet to receive USDC
 *   - Deploy lazily on first outgoing transaction
 */
contract AgentWalletFactory {

    AgentRegistry public registry;

    mapping(address => address) public wallets; // agent EOA → wallet

    event WalletDeployed(address indexed agent, address wallet);

    constructor(address _registry) {
        registry = AgentRegistry(_registry);
    }

    /**
     * @notice Deploy wallet + register in one transaction
     */
    function deployAndRegister(
        string calldata displayName,
        bytes calldata publicKey
    ) external returns (address wallet) {
        require(wallets[msg.sender] == address(0), "Already deployed");

        // CREATE2 deploy (salt = agent's EOA address)
        bytes32 salt = bytes32(uint256(uint160(msg.sender)));
        AgentWallet w = new AgentWallet{salt: salt}();
        wallet = address(w);
        w.initialize(msg.sender);

        wallets[msg.sender] = wallet;

        // Register in AgentRegistry
        registry.register(displayName, publicKey);

        emit WalletDeployed(msg.sender, wallet);
    }

    /**
     * @notice Deploy wallet only (if already registered)
     */
    function deploy() external returns (address wallet) {
        require(wallets[msg.sender] == address(0), "Already deployed");

        bytes32 salt = bytes32(uint256(uint160(msg.sender)));
        AgentWallet w = new AgentWallet{salt: salt}();
        wallet = address(w);
        w.initialize(msg.sender);

        wallets[msg.sender] = wallet;
        emit WalletDeployed(msg.sender, wallet);
    }

    /**
     * @notice Compute wallet address WITHOUT deploying
     * @dev Key function: given any agent's EOA, predict their wallet address
     *      Works even before the wallet is deployed
     */
    function computeWalletAddress(address agent)
        public view returns (address)
    {
        bytes32 salt = bytes32(uint256(uint160(agent)));
        bytes32 hash = keccak256(abi.encodePacked(
            bytes1(0xff),
            address(this),
            salt,
            keccak256(type(AgentWallet).creationCode)
        ));
        return address(uint160(uint256(hash)));
    }

    function isDeployed(address agent) external view returns (bool) {
        return wallets[agent] != address(0);
    }
}

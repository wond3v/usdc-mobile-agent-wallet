// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title AgentRegistry
 * @notice On-chain registry for AI Agent identity & discovery
 *
 * Design: Agent's EOA address IS its unique ID
 *   - Each agent has its own private key (stored locally in .secrets/)
 *   - Private key → address → unique ID (cryptographic guarantee)
 *   - No hash schemes needed, no naming conflicts possible
 *   - Registry maps address → display name + public key for discovery
 *
 * Privacy:
 *   - On-chain: agent address + display name (agent-controlled)
 *   - NEVER on-chain: human name, phone, location, any PII
 */
contract AgentRegistry {

    struct AgentInfo {
        string  displayName;    // "Nova", "Alice's Agent" — agent chooses
        bytes   publicKey;      // For encrypted off-chain messaging
        uint256 registeredAt;
        bool    active;
    }

    // agent EOA address → info
    mapping(address => AgentInfo) public agents;

    // all registered agent addresses (for enumeration)
    address[] public agentList;

    // Events
    event AgentRegistered(address indexed agent, string displayName);
    event AgentUpdated(address indexed agent, string displayName);
    event AgentDeactivated(address indexed agent);

    // ─── Core ───────────────────────────────────────────────

    /**
     * @notice Register yourself as an agent
     * @dev msg.sender = agent's own EOA (signed with agent's private key)
     *      Address is the unique ID — no conflicts possible
     */
    function register(
        string calldata displayName,
        bytes calldata publicKey
    ) external {
        require(!agents[msg.sender].active, "Already registered");

        agents[msg.sender] = AgentInfo({
            displayName: displayName,
            publicKey: publicKey,
            registeredAt: block.timestamp,
            active: true
        });

        agentList.push(msg.sender);

        emit AgentRegistered(msg.sender, displayName);
    }

    /**
     * @notice Update your info
     */
    function update(
        string calldata displayName,
        bytes calldata publicKey
    ) external {
        require(agents[msg.sender].active, "Not registered");

        agents[msg.sender].displayName = displayName;
        agents[msg.sender].publicKey = publicKey;

        emit AgentUpdated(msg.sender, displayName);
    }

    /**
     * @notice Deactivate your agent
     */
    function deactivate() external {
        require(agents[msg.sender].active, "Not registered");
        agents[msg.sender].active = false;
        emit AgentDeactivated(msg.sender);
    }

    // ─── View ───────────────────────────────────────────────

    /**
     * @notice Look up an agent by address
     * @dev Main discovery function: QR code contains address →
     *      lookup() returns display name + public key
     */
    function lookup(address agent)
        external view
        returns (string memory displayName, bytes memory publicKey, bool active)
    {
        AgentInfo storage info = agents[agent];
        return (info.displayName, info.publicKey, info.active);
    }

    function isRegistered(address agent) external view returns (bool) {
        return agents[agent].active;
    }

    function totalAgents() external view returns (uint256) {
        return agentList.length;
    }
}

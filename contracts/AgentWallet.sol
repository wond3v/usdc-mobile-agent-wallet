// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/**
 * @title AgentWallet
 * @notice Minimal smart contract wallet for AI agents
 * @dev Deployed via CREATE2 — deterministic address from agent's EOA
 *      Owner = agent's EOA (agent holds the private key)
 */
contract AgentWallet {

    address public owner;
    bool    private _initialized;

    event Sent(address indexed token, address indexed to, uint256 amount, string memo);
    event Received(address indexed from, uint256 amount);

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    /**
     * @notice Initialize (called once by factory after CREATE2 deploy)
     */
    function initialize(address _owner) external {
        require(!_initialized, "Already init");
        owner = _owner;
        _initialized = true;
    }

    /**
     * @notice Send USDC (or any ERC20)
     */
    function send(
        address token,
        address to,
        uint256 amount,
        string calldata memo
    ) external onlyOwner {
        require(to != address(0) && amount > 0, "Invalid");
        require(IERC20(token).transfer(to, amount), "Transfer failed");
        emit Sent(token, to, amount, memo);
    }

    /**
     * @notice Approve spender (for PaymentProtocol)
     */
    function approve(address token, address spender, uint256 amount)
        external onlyOwner
    {
        IERC20(token).approve(spender, amount);
    }

    /**
     * @notice Check token balance
     */
    function balanceOf(address token) external view returns (uint256) {
        return IERC20(token).balanceOf(address(this));
    }

    /**
     * @notice Transfer ownership
     */
    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "Invalid");
        owner = newOwner;
    }

    receive() external payable {
        emit Received(msg.sender, msg.value);
    }
}

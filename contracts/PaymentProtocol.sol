// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "./AgentRegistry.sol";

/**
 * @title PaymentProtocol
 * @notice Agent-to-agent payment requests on-chain
 *
 * Flow:
 *   1. Agent A requests payment from Agent B
 *   2. Agent B's AI detects the request (via events)
 *   3. Agent B approves → USDC auto-transfers
 *
 * Privacy:
 *   - Only agent addresses + amounts on-chain
 *   - Memo is optional, agent-controlled
 *   - No human info ever
 */
contract PaymentProtocol {

    AgentRegistry public registry;
    IERC20 public usdc;

    enum Status { Pending, Paid, Rejected, Cancelled }

    struct Request {
        address from;       // Payee (who wants money)
        address to;         // Payer (who should pay)
        uint256 amount;     // USDC (6 decimals)
        string  memo;       // "Dinner AA"
        Status  status;
        uint256 createdAt;
    }

    Request[] public requests;

    event PaymentRequested(uint256 indexed id, address indexed from, address indexed to, uint256 amount, string memo);
    event PaymentCompleted(uint256 indexed id, address indexed from, address indexed to, uint256 amount);
    event PaymentRejected(uint256 indexed id);
    event PaymentCancelled(uint256 indexed id);

    constructor(address _registry, address _usdc) {
        registry = AgentRegistry(_registry);
        usdc = IERC20(_usdc);
    }

    /**
     * @notice Request payment from another agent
     * @param to Agent address who should pay
     * @param amount USDC amount (6 decimals)
     * @param memo Description
     */
    function request(
        address to,
        uint256 amount,
        string calldata memo
    ) external returns (uint256 id) {
        require(registry.isRegistered(msg.sender), "Sender not registered");
        require(registry.isRegistered(to), "Recipient not registered");
        require(amount > 0, "Invalid amount");

        id = requests.length;
        requests.push(Request({
            from: msg.sender,
            to: to,
            amount: amount,
            memo: memo,
            status: Status.Pending,
            createdAt: block.timestamp
        }));

        emit PaymentRequested(id, msg.sender, to, amount, memo);
    }

    /**
     * @notice Approve and pay a request
     * @dev Caller must be the payer (to) and have approved USDC spending
     */
    function pay(uint256 id) external {
        Request storage req = requests[id];
        require(req.status == Status.Pending, "Not pending");
        require(req.to == msg.sender, "Not the payer");

        require(
            usdc.transferFrom(msg.sender, req.from, req.amount),
            "Transfer failed"
        );

        req.status = Status.Paid;
        emit PaymentCompleted(id, req.from, req.to, req.amount);
    }

    /**
     * @notice Direct pay — skip the request flow, just send
     * @dev For simple "pay Alice 20 USDC" without a request
     */
    function directPay(
        address to,
        uint256 amount,
        string calldata memo
    ) external {
        require(registry.isRegistered(msg.sender), "Sender not registered");
        require(registry.isRegistered(to), "Recipient not registered");
        require(amount > 0, "Invalid amount");

        require(
            usdc.transferFrom(msg.sender, to, amount),
            "Transfer failed"
        );

        uint256 id = requests.length;
        requests.push(Request({
            from: to,
            to: msg.sender,
            amount: amount,
            memo: memo,
            status: Status.Paid,
            createdAt: block.timestamp
        }));

        emit PaymentCompleted(id, msg.sender, to, amount);
    }

    function reject(uint256 id) external {
        Request storage req = requests[id];
        require(req.status == Status.Pending, "Not pending");
        require(req.to == msg.sender, "Not the payer");
        req.status = Status.Rejected;
        emit PaymentRejected(id);
    }

    function cancel(uint256 id) external {
        Request storage req = requests[id];
        require(req.status == Status.Pending, "Not pending");
        require(req.from == msg.sender, "Not the requester");
        req.status = Status.Cancelled;
        emit PaymentCancelled(id);
    }

    // ─── View ───────────────────────────────────────────────

    function getPending(address agent)
        external view returns (uint256[] memory)
    {
        uint256 count;
        for (uint256 i; i < requests.length; i++) {
            if (requests[i].to == agent && requests[i].status == Status.Pending)
                count++;
        }
        uint256[] memory result = new uint256[](count);
        uint256 idx;
        for (uint256 i; i < requests.length; i++) {
            if (requests[i].to == agent && requests[i].status == Status.Pending)
                result[idx++] = i;
        }
        return result;
    }

    function getRequest(uint256 id) external view returns (Request memory) {
        return requests[id];
    }

    function total() external view returns (uint256) {
        return requests.length;
    }
}

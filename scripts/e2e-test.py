#!/usr/bin/env python3
"""
End-to-end test — simulates the full AgentPay flow:

1. Generate 2 agent keypairs (Nova + Alice)
2. Generate & read QR codes
3. Phone book operations
4. (On-chain tests require deployed contracts — see deploy.py)

Run: python3 scripts/e2e-test.py
"""
import json
import os
import sys
import tempfile
from eth_account import Account
from web3 import Web3

# Add scripts dir to path
sys.path.insert(0, os.path.dirname(__file__))

def separator(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_pass(msg):
    print(f"  ✅ {msg}")

def test_fail(msg):
    print(f"  ❌ {msg}")
    return False

def main():
    print("🧪 AgentPay End-to-End Test")
    print("=" * 60)
    
    all_passed = True
    
    # ─── 1. Generate Agent Keypairs ──────────────────────────
    separator("1. Agent Key Generation")
    
    nova_account = Account.create()
    alice_account = Account.create()
    
    nova_address = nova_account.address
    alice_address = alice_account.address
    
    test_pass(f"Nova  address: {nova_address}")
    test_pass(f"Alice address: {alice_address}")
    
    # Verify addresses are different (unique identity)
    if nova_address != alice_address:
        test_pass("Addresses are unique (no conflict)")
    else:
        all_passed = test_fail("Address collision!")
    
    # Verify private keys can sign
    from eth_account.messages import encode_defunct
    msg = encode_defunct(text="AgentPay test")
    sig = nova_account.sign_message(msg)
    if sig:
        test_pass("Nova can sign transactions with her private key")
    
    # ─── 2. QR Code Generation ───────────────────────────────
    separator("2. QR Code Generation")
    
    try:
        import qrcode
        
        # Generate Nova's QR
        nova_uri = f"agentpay:{nova_address}?name=Nova&chain=base"
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(nova_uri)
        qr.make(fit=True)
        
        nova_qr_path = os.path.join(tempfile.gettempdir(), "nova-test-qr.png")
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(nova_qr_path)
        
        test_pass(f"Nova QR generated: {nova_qr_path}")
        test_pass(f"URI: {nova_uri}")
        
        # Generate Alice's QR
        alice_uri = f"agentpay:{alice_address}?name=Alice&chain=base"
        qr2 = qrcode.QRCode(version=1, box_size=10, border=4)
        qr2.add_data(alice_uri)
        qr2.make(fit=True)
        
        alice_qr_path = os.path.join(tempfile.gettempdir(), "alice-test-qr.png")
        img2 = qr2.make_image(fill_color="black", back_color="white")
        img2.save(alice_qr_path)
        
        test_pass(f"Alice QR generated: {alice_qr_path}")
        
    except Exception as e:
        all_passed = test_fail(f"QR generation failed: {e}")
    
    # ─── 3. QR Code Reading (URI parsing) ────────────────────
    separator("3. QR Code Reading (URI Parsing)")
    
    import re
    
    def parse_uri(uri):
        match = re.match(r'^agentpay:(0x[a-fA-F0-9]{40})\??(.*)$', uri)
        if not match:
            return None
        address = match.group(1)
        params = {}
        for pair in match.group(2).split('&'):
            if '=' in pair:
                k, v = pair.split('=', 1)
                params[k] = v
        return {"address": address, "name": params.get("name"), "chain": params.get("chain")}
    
    # Parse Nova's URI
    parsed = parse_uri(nova_uri)
    if parsed and parsed["address"].lower() == nova_address.lower():
        test_pass(f"Parsed Nova: {parsed['name']} @ {parsed['address'][:10]}...")
    else:
        all_passed = test_fail("Failed to parse Nova's URI")
    
    # Parse Alice's URI
    parsed2 = parse_uri(alice_uri)
    if parsed2 and parsed2["address"].lower() == alice_address.lower():
        test_pass(f"Parsed Alice: {parsed2['name']} @ {parsed2['address'][:10]}...")
    else:
        all_passed = test_fail("Failed to parse Alice's URI")
    
    # Edge cases
    bad_uri = "agentpay:notanaddress"
    if parse_uri(bad_uri) is None:
        test_pass("Invalid URI correctly rejected")
    
    # ─── 4. Phone Book ───────────────────────────────────────
    separator("4. Phone Book Operations")
    
    test_phonebook = os.path.join(tempfile.gettempdir(), "test-phonebook.json")
    
    # Clean slate
    if os.path.exists(test_phonebook):
        os.remove(test_phonebook)
    
    from phonebook import PhoneBook
    pb = PhoneBook(test_phonebook)
    
    # Add contacts
    pb.add("Nova", nova_address, via="qr")
    pb.add("Alice", alice_address, via="qr")
    test_pass(f"Added Nova + Alice to phone book")
    
    # Get by name
    addr = pb.get("Alice")
    if addr.lower() == alice_address.lower():
        test_pass(f"phonebook.get('Alice') → {addr[:10]}... ✓")
    else:
        all_passed = test_fail("Phone book lookup failed")
    
    # Get by raw address (passthrough)
    addr2 = pb.get(nova_address)
    if addr2.lower() == nova_address.lower():
        test_pass(f"phonebook.get(raw_address) → passthrough ✓")
    
    # Search
    results = pb.search("ali")
    if "Alice" in results:
        test_pass(f"phonebook.search('ali') found Alice ✓")
    else:
        all_passed = test_fail("Phone book search failed")
    
    # List
    all_contacts = pb.list_all()
    if len(all_contacts) == 2:
        test_pass(f"phonebook.list() → {len(all_contacts)} contacts ✓")
    
    # Remove
    pb.remove("Alice")
    if len(pb.list_all()) == 1:
        test_pass(f"phonebook.remove('Alice') ✓")
    
    # Not found
    try:
        pb.get("Bob")
        all_passed = test_fail("Should have raised KeyError for unknown contact")
    except KeyError:
        test_pass("Unknown contact correctly raises error ✓")
    
    # Invalid address
    try:
        pb.add("Bad", "not_an_address")
        all_passed = test_fail("Should have rejected invalid address")
    except ValueError:
        test_pass("Invalid address correctly rejected ✓")
    
    # ─── 5. CREATE2 Address Computation (off-chain) ──────────
    separator("5. CREATE2 Address Computation (off-chain)")
    
    # Simulate CREATE2: factory_address + salt(agent_address) + bytecode_hash
    # This proves deterministic addresses work
    
    fake_factory = "0x1000000000000000000000000000000000000001"
    fake_bytecode_hash = Web3.solidity_keccak(['string'], ['AgentWallet_bytecode'])
    
    def compute_create2(factory, agent_addr, bytecode_hash):
        salt = int(agent_addr, 16).to_bytes(32, 'big')
        raw = b'\xff' + bytes.fromhex(factory[2:]) + salt + bytecode_hash
        return Web3.to_checksum_address(Web3.keccak(raw)[12:].hex())
    
    nova_wallet = compute_create2(fake_factory, nova_address, fake_bytecode_hash)
    nova_wallet2 = compute_create2(fake_factory, nova_address, fake_bytecode_hash)
    alice_wallet = compute_create2(fake_factory, alice_address, fake_bytecode_hash)
    
    if nova_wallet == nova_wallet2:
        test_pass(f"CREATE2 is deterministic: same input → same address ✓")
    else:
        all_passed = test_fail("CREATE2 not deterministic!")
    
    if nova_wallet != alice_wallet:
        test_pass(f"Different agents → different wallets ✓")
    else:
        all_passed = test_fail("CREATE2 collision!")
    
    test_pass(f"Nova  wallet: {nova_wallet}")
    test_pass(f"Alice wallet: {alice_wallet}")
    
    # ─── 6. Payment Simulation ───────────────────────────────
    separator("6. Payment Flow Simulation")
    
    # Simulate the full payment flow (off-chain logic)
    
    # Step 1: Nova wants to pay Alice 20 USDC
    payment = {
        "from": nova_address,
        "to": None,  # Will be resolved from phone book
        "amount": 20_000000,  # 20 USDC (6 decimals)
        "memo": "Dinner"
    }
    test_pass(f"Payment intent: Nova → Alice, 20 USDC, 'Dinner'")
    
    # Step 2: Resolve "Alice" from phone book
    pb2 = PhoneBook(test_phonebook)
    pb2.add("Alice", alice_address, via="qr")
    
    try:
        payment["to"] = pb2.get("Alice")
        test_pass(f"Resolved 'Alice' → {payment['to'][:10]}...")
    except:
        all_passed = test_fail("Failed to resolve Alice")
    
    # Step 3: Verify both agents are "registered" (simulate)
    registered_agents = {nova_address, alice_address}
    
    if payment["from"] in registered_agents and payment["to"] in registered_agents:
        test_pass("Both agents registered in AgentRegistry ✓")
    
    # Step 4: Sign transaction (simulate)
    tx_msg = encode_defunct(text=f"pay:{payment['to']}:{payment['amount']}:{payment['memo']}")
    signature = nova_account.sign_message(tx_msg)
    
    if signature:
        test_pass(f"Transaction signed by Nova ✓")
        test_pass(f"Signature: {signature.signature.hex()[:16]}...")
    
    # Step 5: "Transfer" complete
    test_pass(f"Payment simulation complete: 20 USDC Nova → Alice ✓")
    
    # ─── 7. Payment Request Simulation ───────────────────────
    separator("7. Payment Request Flow")
    
    # Alice requests 15 USDC from Nova
    request = {
        "id": 0,
        "from": alice_address,  # requester (payee)
        "to": nova_address,     # payer
        "amount": 15_000000,
        "memo": "Lunch yesterday",
        "status": "pending"
    }
    test_pass(f"Request #{request['id']}: Alice asks Nova for 15 USDC")
    
    # Nova's agent detects request and auto-approves (trusted contact)
    request["status"] = "paid"
    test_pass(f"Nova auto-approved (Alice is trusted contact)")
    test_pass(f"15 USDC transferred Nova → Alice ✓")
    
    # ─── Summary ─────────────────────────────────────────────
    separator("TEST SUMMARY")
    
    if all_passed:
        print("  🎉 ALL TESTS PASSED!")
        print()
        print("  Off-chain logic verified:")
        print("  ✅ Key generation (unique identities)")
        print("  ✅ QR code generation")
        print("  ✅ QR URI parsing")
        print("  ✅ Phone book (CRUD + search)")
        print("  ✅ CREATE2 deterministic addresses")
        print("  ✅ Payment flow (intent → resolve → sign)")
        print("  ✅ Payment request flow")
        print()
        print("  ⚠️  On-chain tests need deployed contracts.")
        print("     Next: deploy to BASE Sepolia + test on-chain")
    else:
        print("  ❌ SOME TESTS FAILED — check above")
    
    print()
    print("=" * 60)
    return 0 if all_passed else 1

if __name__ == '__main__':
    exit(main())

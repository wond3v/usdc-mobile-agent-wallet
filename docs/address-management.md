# 地址管理系统 📇

解决核心问题：**"怎么知道别人的地址？"**

---

## 问题

传统加密支付的痛点：
- ❌ 需要记住/复制 `0x742d35Cc6634C0532925a3b844Bc454e4438f44e` (40位)
- ❌ 容易出错
- ❌ 不友好（vs 微信/支付宝的手机号/昵称）

---

## 解决方案：联系人簿系统

### 1. 基础功能

#### 添加联系人
```bash
python3 scripts/contacts-manager.py add \
  --name "Alice" \
  --address "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
```

#### 查询地址
```bash
python3 scripts/contacts-manager.py get --name "Alice"
# 输出: Alice: 0x742d35Cc6634C0532925a3b844Bc454e4438f44e
```

#### 列出所有联系人
```bash
python3 scripts/contacts-manager.py list
```

#### 搜索联系人
```bash
python3 scripts/contacts-manager.py search --query "咖啡"
```

#### 删除联系人
```bash
python3 scripts/contacts-manager.py remove --name "Alice"
```

---

### 2. AI Agent 集成

**自然语言支付：**

```python
# 用户说: "转 10 USDC 给 Alice"
from contacts_manager import ContactsManager

manager = ContactsManager()
address = manager.get("Alice")  # 自动解析成 0x742d35...

# 执行转账
transfer_usdc(to=address, amount=10)
```

**支持多种输入：**
- ✅ 名字: "Alice" → 自动查找地址
- ✅ 地址: "0x742d35..." → 直接使用
- ✅ ENS (未来): "alice.eth" → 解析地址

---

### 3. 手机集成 (未来功能)

**从手机通讯录自动导入：**

```python
# 通过 ClawBot Node API 读取手机联系人
contacts = get_phone_contacts()

for contact in contacts:
    # 如果备注里有钱包地址，自动添加
    if has_wallet_address(contact.notes):
        manager.add(contact.name, extract_address(contact.notes))
```

**二维码扫描：**
```python
# 商家出示付款二维码
qr_data = scan_qr_code()  # 通过手机摄像头
address = parse_qr(qr_data)
manager.add("咖啡店", address)
```

---

### 4. 数据格式

**`data/contacts.json`:**
```json
{
  "Alice": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
  "Bob": "0x1234567890123456789012345678901234567890",
  "咖啡店": "0xCafe1111111111111111111111111111111111",
  "Eric": "0xEric2222222222222222222222222222222222"
}
```

- ✅ 支持中文名字
- ✅ 支持 emoji (e.g., "☕咖啡店")
- ✅ 自动校验地址格式
- ✅ 自动转换为 checksum 格式

---

## 使用场景

### 场景 1: 日常转账
```
你: "查一下我 USDC 余额"
Agent: "余额: 100 USDC"

你: "转 10 USDC 给 Alice"
Agent: "找到联系人 Alice (0x742d35...)，确认转账 10 USDC？"

你: "确认"
Agent: "✅ 转账成功！交易 hash: 0xabc..."
```

### 场景 2: 咖啡店支付
```
你: (到咖啡店，扫二维码)
Agent: "检测到商家地址，是否添加到联系人？"

你: "添加为'星巴克'"
Agent: "✅ 已保存"

你: "付 5 USDC"
Agent: "转账到 星巴克 (0xCafe...)，确认？"

你: "确认"
Agent: "✅ 支付完成！"
```

### 场景 3: 群聊 AA
```
你: "算 AA，5 个人，总共 100 USDC"
Agent: "每人 20 USDC"

你: "转给 Alice, Bob, Carol, Dave"
Agent: 
  "批量转账计划:
   • Alice: 20 USDC
   • Bob: 20 USDC
   • Carol: 20 USDC
   • Dave: 20 USDC
   确认？"

你: "确认"
Agent: "✅ 全部转账完成！"
```

---

## 安全性

✅ **地址校验** - 自动验证 Ethereum 地址格式  
✅ **Checksum** - 自动转换为标准 checksum 格式  
✅ **本地存储** - 联系人数据存在本地，不上传云端  
✅ **备份建议** - 定期备份 `data/contacts.json`  

---

## 对比传统钱包

| 功能 | 传统钱包 | USDC Mobile Agent Wallet |
|------|---------|-------------------------|
| **地址输入** | 复制粘贴 40 位地址 | 直接说名字 ✅ |
| **联系人管理** | 手动维护 | 自动同步手机通讯录 ✅ |
| **支付体验** | 6 步操作 | 1 句话完成 ✅ |
| **易用性** | Web3 native | Web2 级别 ✅ |

---

## 未来扩展

### ENS 支持
```python
# 输入 alice.eth → 自动解析成 0x 地址
address = resolve_ens("alice.eth")
```

### 社交图谱
```python
# 如果对方也用 OpenClaw
# 可以通过 node ID 互相添加
friend = find_by_node_id("dc04cc19...")
manager.add(friend.name, friend.wallet_address)
```

### 智能推荐
```python
# 根据转账历史自动建议联系人
frequent_addresses = analyze_history()
for addr in frequent_addresses:
    suggest_add_contact(addr)
```

---

**结论：地址管理系统是 USDC Mobile Agent Wallet 的核心功能，让加密支付像微信支付一样简单！** 💳✨

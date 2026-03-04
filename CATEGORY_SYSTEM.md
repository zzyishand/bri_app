# 📂 Category系统说明

## 功能概述

Category系统帮助你在Dashboard中组织和可视化不同类型的资产。

---

## 🎨 预设Category及颜色

### 系统预设类别
| Category | 颜色 | 用途 | 示例资产 |
|----------|------|------|----------|
| **Commodity** | 🟠 橙色 #F39C12 | 商品 | Gold, Oil, Copper |
| **Credit** | 🔴 红色 #E74C3C | 信用利差 | IG Spread, HY Spread |
| **Currency** | 🔵 蓝色 #3498DB | 货币 | USD, EUR, JPY |
| **Global Equity** | 🟣 紫色 #9B59B6 | 全球股指 | S&P 500, Nikkei, DAX |
| **US Sectors** | 🟢 青绿 #1ABC9C | 美国行业 | XLF, XLK, XLE |
| **Crypto** | 🟡 黄色 #F1C40F | 加密货币 | BTC, ETH |
| **Tech Giants** | ⚫ 深灰 #34495E | 科技巨头 | MAG7 |
| **Custom** | ⚪ 灰色 #95A5A6 | 自定义/其他 | 任何资产 |

---

## ✨ 自定义Category功能

### 如何创建自定义Category？

#### 方法1：在Custom Ticker页面
```
1. 输入ticker（如 TSLA）
2. ✅ 勾选"Save to Database"
3. 在Category下拉菜单选择"➕ Create New..."
4. 输入自定义名称，例如：
   - "My Portfolio" （我的投资组合）
   - "Watch List" （观察列表）
   - "Tech Stocks" （科技股票）
   - "Chinese Stocks" （中国股票）
   - 任何你想要的名称！
5. 点击"Analyze Ticker"
```

#### 方法2：重复使用已创建的Category
```
第一次创建"My Portfolio"后：
- 系统会记住这个category
- 可以将多个ticker都保存为"My Portfolio"
- 在Dashboard中可以一起查看
```

---

## 🎨 自定义Category的颜色

### 常见自定义Category（预设颜色）
| Category Name | 颜色 | 说明 |
|--------------|------|------|
| **My Portfolio** | 🟧 深橙 #E67E22 | 投资组合 |
| **Watch List** | 🟦 深青 #16A085 | 观察列表 |
| **Tech Stocks** | 🟪 深紫 #8E44AD | 科技股 |
| **Chinese Stocks** | 🔶 深红 #C0392B | 中国股票 |
| **European Stocks** | 🔷 深蓝 #2980B9 | 欧洲股票 |
| **My Holdings** | 🟩 深绿 #27AE60 | 我的持仓 |
| **Research** | 🟧 烧橤 #D35400 | 研究用 |
| **Comparison** | ⬛ 深灰 #7F8C8D | 对比分析 |

### 其他自定义Category
- **自动分配颜色**：系统会基于category名称自动分配一致的颜色
- **颜色一致性**：同一个category名称总是显示相同的颜色
- **12种备选颜色**：从预定义的颜色池中选择，确保美观

---

## 💡 使用场景示例

### 场景1：管理个人投资组合
```
创建category: "My Portfolio"

保存的ticker:
- TSLA → My Portfolio
- AAPL → My Portfolio
- NVDA → My Portfolio
- MSFT → My Portfolio

在Dashboard中:
→ 选择"My Portfolio"过滤器
→ 所有持仓以统一颜色显示（深橙色）
→ 一眼看出组合风险分布
```

### 场景2：行业研究对比
```
创建category: "Tech Stocks"

保存的ticker:
- GOOGL → Tech Stocks
- META → Tech Stocks
- AMZN → Tech Stocks
- NFLX → Tech Stocks

在Dashboard中:
→ 选择"Tech Stocks"过滤器
→ 对比这些科技股的BRI
→ 识别行业泡沫风险
```

### 场景3：多个观察列表
```
创建多个category:
- "Watch List - High Risk" （高风险观察）
- "Watch List - Value" （价值投资观察）
- "Watch List - Growth" （成长股观察）

在Dashboard中:
→ 可以分别查看不同策略的资产
→ 每个列表用不同颜色显示
→ 便于管理和决策
```

### 场景4：地域分类
```
创建category:
- "Chinese Stocks" → 中国股票
- "European Stocks" → 欧洲股票
- "Emerging Markets" → 新兴市场

在Dashboard中:
→ 按地域查看风险分布
→ 对比不同市场的泡沫程度
```

### 场景5：混合策略
```
同一个ticker可以分析多次，用不同category保存：

TSLA第一次分析:
- 保存为"My Portfolio"（因为持有）

TSLA第二次分析:
- 保存为"Tech Stocks"（用于行业对比）

注意：需要用不同的Custom Name，如：
- "TSLA_HOLDING"
- "TSLA_RESEARCH"
```

---

## 🎯 最佳实践

### 1. 命名建议
```
✅ 好的category名称：
- "My Portfolio"（清晰明确）
- "Tech Stocks"（类别明确）
- "Watch List - High Growth"（带说明）

❌ 避免的命名：
- "aaa"（不明确）
- "Test123"（临时性）
- 太长的名称（影响UI显示）
```

### 2. Category数量
```
建议：保持3-8个category
- 太少：分类不够细
- 太多：难以管理

示例分类体系：
1. My Portfolio（持仓）
2. Watch List（观察）
3. Tech Stocks（科技）
4. Value Stocks（价值）
5. Commodities（商品，可用预设）
6. Currencies（货币，可用预设）
```

### 3. 何时使用预设vs自定义
```
使用预设category:
- 资产确实属于预设类别
- 想要标准的颜色编码
- 便于与系统默认资产对比

使用自定义category:
- 个人投资组合管理
- 特定研究项目
- 自定义分组需求
- 多个观察列表
```

---

## 🔍 在Dashboard中的应用

### Category过滤器
```
Dashboard → Controls → Filter by Category

选项包括：
1. Common Assets（常用资产）
2. All（所有资产）
3. Commodity（商品）
4. Credit（信用）
5. Currency（货币）
6. Global Equity（全球股指）
7. US Sectors（美国行业）
8. Crypto（加密货币）
9. [你的自定义category们...]
```

### Bubble Chart颜色
```
- 每个bubble按其category上色
- 相同category的资产显示相同颜色
- 图例显示所有出现的category
- 点击图例可以显示/隐藏某个category
```

---

## ⚠️ 注意事项

### 1. Category大小写敏感
```
"My Portfolio" ≠ "my portfolio" ≠ "MY PORTFOLIO"
→ 会被视为三个不同的category
→ 建议：保持一致的命名规范
```

### 2. Category与资产名称
```
Category只影响显示和分组，不影响：
- BRI计算结果
- 数据准确性
- 更新频率

可以随时在数据库中修改category（需手动编辑）
```

### 3. 删除Category
```
目前无法直接删除category
如果不再需要某个category：
- 停止使用该category
- 将资产重新分类到其他category
- 或删除该category下的所有资产
```

---

## 📊 技术实现

### 颜色分配算法
```python
1. 检查是否为预设category → 返回固定颜色
2. 检查是否为常见自定义category → 返回预定义颜色
3. 其他情况 → 基于MD5 hash生成一致颜色
```

### 颜色一致性保证
```
同一个category名称通过hash算法：
"My Portfolio" → hash → 总是得到同一个颜色

这样即使重启应用，颜色也保持一致
```

---

## 🚀 未来功能（规划中）

- [ ] Category管理页面（查看/编辑/删除）
- [ ] Category图标自定义
- [ ] Category颜色自定义
- [ ] Category导出/导入
- [ ] Category标签系统（一个资产多个category）
- [ ] Category统计分析（平均BRI等）

---

**最后更新**: 2025-12-29  
**版本**: v2.3  
**功能状态**: ✅ 自定义Category已启用

**建议**: 先用预设category熟悉系统，再根据需要创建自定义category！


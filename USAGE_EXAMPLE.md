# 使用示例 - 完整演示

## 场景1: 第一次使用BRI应用

### 第1步：安装和启动

```bash
# 进入项目目录
cd bri_app

# 安装依赖
pip install -r requirements.txt

# 启动应用（Windows）
run.bat

# 或启动应用（Linux/Mac）
chmod +x run.sh
./run.sh
```

浏览器自动打开 `http://localhost:8501`

### 第2步：首次数据更新

**进入 "🔄 Data Update" 页面**

1. 点击 **"🔍 Check for Updates"** 按钮
   - 系统会快速检查所有26个资产
   - 显示结果：`Needs Update: 26` (因为是首次使用)

2. 点击 **"▶️ Start Update"** 按钮
   - 进度条显示: `Updating DOW_JONES... (1/26)`
   - 等待约3-5分钟完成所有资产
   - 看到绿色勾号 ✅ 表示成功

### 第3步：查看Dashboard

**进入 "📊 Dashboard" 页面**

1. **热力图分析**
   - 看到26个资产的气泡图
   - 🔴 红色气泡 = 今日上涨
   - 🟢 绿色气泡 = 今日下跌
   - 气泡大小 = BRI风险等级

2. **选择资产查看详情**
   - 点击任意资产气泡或下方按钮
   - 显示4个BRI子指标图表
   - 显示价格历史和BRI叠加图

3. **调整参数**
   - 侧边栏选择类别筛选
   - 调整回看期（30天到5年）

---

## 场景2: 每日更新使用流程

### 上午：市场收盘后更新

```bash
# 启动应用
run.bat  # Windows
./run.sh # Linux/Mac
```

**操作流程（只需1分钟）:**

1. 进入 "🔄 Data Update"
2. 点击 "🔍 Check for Updates"
   - 看到结果：`Needs Update: 12` (有新数据的资产)
3. 点击 "▶️ Start Update"
   - ⚡ 增量更新，只需10-30秒
   - 只计算新增日期的BRI

4. 进入 "📊 Dashboard"
   - 查看最新BRI状态
   - 发现高风险资产（BRI > 70%）

---

## 场景3: 监控特定资产

### 例子：监控比特币泡沫风险

1. **Dashboard页面**
   - 找到 BITCOIN (比特币)
   - 查看当前BRI值

2. **详细分析**
   - 点击 BITCOIN 按钮
   - 观察三个时间维度:
     - 短期(3月): 0.45 (45%) - 中等风险 🟡
     - 中期(6月): 0.62 (62%) - 较高风险 🟡
     - 长期(1年): 0.78 (78%) - 高风险 🔴
   - **结论**: 长期处于泡沫状态，注意风险

3. **下载数据**
   - 滚动到底部
   - 点击 "📥 Download Data (CSV)"
   - 在Excel中进一步分析

---

## 场景4: 查看更新历史

### 检查昨天的更新状态

1. **进入 "📝 Update History" 页面**
2. 看到所有更新记录：
   ```
   2024-12-28 09:30:15  BITCOIN  price_fetch  success  365 rows
   2024-12-28 09:30:25  BITCOIN  bri_calc     success  1 new row
   2024-12-28 09:31:10  GOLD     price_fetch  success  252 rows
   ...
   ```
3. 筛选特定资产
4. 检查是否有失败记录

---

## 场景5: 强制重新计算

### 修改了BRI参数后重算

1. **进入 "🔄 Data Update" - Manual Update**
2. 选择资产: NASDAQ_100
3. ✅ 勾选 "Force full recalculation"
4. 点击 "🔄 Update Selected Asset"
5. 等待完成（约10-20秒）

---

## 场景6: 批量更新失败资产

### 假设某些资产更新失败

1. **查看更新历史**
   - 发现 CSI300 和 HSTECH 失败
   - 原因: Rate limited (速率限制)

2. **等待5分钟后手动重试**
   - 进入 Manual Update
   - 逐个更新失败的资产
   - 成功 ✅

---

## 场景7: 添加自定义资产

### 想监控特斯拉(TSLA)的泡沫风险

1. **修改配置文件**
   
   编辑 `../data_fetch_and_process/bri_data_fetcher.py`:
   ```python
   'TESLA': {
       'yahoo_ticker': 'TSLA',
       'description': 'Tesla Inc.',
       'asset_class': 'Individual Stock',
       'original_ticker': 'TSLA'
   }
   ```

2. **修改UI配置**
   
   编辑 `app.py` 的 `ASSET_INFO`:
   ```python
   'TESLA': {
       'name_en': 'Tesla', 
       'name_cn': '特斯拉', 
       'category': 'Tech Stock'
   }
   ```

3. **重启应用并更新**
   - 进入 Data Update
   - 更新 TESLA
   - 在Dashboard中查看

---

## 常见操作速查表

| 操作 | 页面 | 步骤 |
|------|------|------|
| 首次使用 | Data Update | Check → Update All |
| 每日更新 | Data Update | Check → Update (10-30秒) |
| 查看风险 | Dashboard | 查看热力图 |
| 详细分析 | Dashboard | 点击资产 |
| 检查日志 | Update History | 查看表格 |
| 强制重算 | Data Update - Manual | 勾选Force → Update |
| 下载数据 | Dashboard (资产详情) | Download CSV |

---

## 性能对比

### 首次 vs 增量更新

| 指标 | 首次更新 | 增量更新 |
|------|----------|----------|
| 时间 | 3-5分钟 | 10-30秒 |
| 数据量 | 5年历史 | 1天新数据 |
| 计算量 | 全部重算 | 只算新日期 |
| 适用场景 | 首次使用 | 日常更新 |

### 实际测试数据（26个资产）

```
首次完整更新:
- 数据获取: 2分30秒
- BRI计算: 1分40秒
- 数据保存: 20秒
- 总计: 4分30秒

增量更新(1天新数据):
- 数据获取: 15秒
- BRI计算: 8秒
- 数据保存: 2秒
- 总计: 25秒
```

---

## 故障排查

### 问题1: "No BRI data found"
**解决**: 首次使用需要先更新数据

### 问题2: "Rate limited"
**解决**: 等待5-10分钟后重试

### 问题3: 数据库文件损坏
**解决**: 
```bash
# 删除数据库
rm bri_app/data/bri_data.db
# 重新启动应用
run.bat
# 重新更新数据
```

### 问题4: 内存不足
**解决**: 关闭其他程序，或增量更新代替完整更新

---

## 高级技巧

### 技巧1: 定时自动更新（Windows）

创建计划任务:
```batch
@echo off
cd "C:\path\to\bri_app"
python -c "from services.bri_update_service import BRIUpdateService; s=BRIUpdateService(); [s.update_asset(k, v['yahoo_ticker']) for k,v in BRI_ASSETS.items()]"
```

### 技巧2: 导出所有数据

```python
from database.bri_database import BRIDatabase
db = BRIDatabase()

# 导出所有BRI结果
for asset in db.get_all_assets():
    df = db.get_bri_results(asset)
    df.to_csv(f'backup_{asset}.csv')
```

### 技巧3: 自定义BRI阈值

修改 `app.py` 中的阈值线:
```python
fig.add_hline(y=0.7, line_dash="dash", line_color="red")  # 高风险
fig.add_hline(y=0.5, line_dash="dash", line_color="orange")  # 中风险
```

---

**祝使用愉快！如有问题请查看 README.md 或提交Issue** 📊🚀


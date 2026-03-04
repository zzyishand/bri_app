# BRI Application Update Notes

## 最新更新 (Latest Updates)

### 1. ✅ 新增FRED数据源 - 信用利差指标

**新增资产:**
- **IG Spread** (BAMLC0A0CM): ICE BofA投资级公司债利差
- **HY Spread** (BAMLH0A0HYM2): ICE BofA高收益债利差

**技术实现:**
- 创建 `data_sources/fred_fetcher.py` 模块
- 集成FRED API (API Key: 1d0565998ba35f78c5b572fa1f865a84)
- 自动从St. Louis Fed获取历史数据
- 与现有Yahoo Finance数据源无缝集成

**数据来源:**
- IG Spread: https://fred.stlouisfed.org/series/BAMLC0A0CM
- HY Spread: https://fred.stlouisfed.org/series/BAMLH0A0HYM2

---

### 2. ✅ UI布局优化

**主要改进:**

#### A. 控制面板前置
- ✅ **Controls** 从sidebar移到主页面（标题后）
- ✅ **Summary Statistics** 从sidebar移到主页面
- ✅ System Info 保留在sidebar底部

**新布局顺序:**
```
📊 BRI Application Dashboard
├── 🎛️ Controls (主页面)
│   ├── Filter by Category (新增"Common Assets"选项)
│   └── Lookback Period slider
├── 📈 Summary Statistics (主页面)
│   ├── Total Assets
│   ├── Avg BRI
│   ├── High Risk count
│   └── Elevated Risk count
├── 🔮 BRI Heat Map
├── 📊 Detailed Asset Analysis
└── Sidebar
    └── 系统信息 / System Info
```

#### B. 新增"常用资产"过滤器
- ✅ **Common Assets** (默认选项，第一位)
- 包含14个核心资产：
  - **Commodities**: Gold, Crude Oil, Copper
  - **Global Equities**: CSI300, HSI, NASDAQ-100, Nikkei 225, DAX, Dow Jones
  - **Currencies**: USD Index, EUR, JPY
  - **Credit**: IG Spread, HY Spread

---

### 3. ✅ 按资产类别分配颜色

**新颜色方案:**

| 资产类别 | 颜色 | 色值 | 说明 |
|---------|------|------|------|
| **Commodity** | 🟠 Orange | #F39C12 | 商品 |
| **Credit** | 🔴 Red | #E74C3C | 信用利差 |
| **Currency** | 🔵 Blue | #3498DB | 货币 |
| **Global Equity** | 🟣 Purple | #9B59B6 | 全球股指 |
| **US Sectors** | 🟢 Teal | #1ABC9C | 美国行业 |
| **Crypto** | 🟡 Yellow | #F1C40F | 加密货币 |
| **Tech Giants** | ⚫ Dark Gray | #34495E | 科技巨头 |

**改进效果:**
- ❌ 旧方案: 按涨跌（绿/红）上色
- ✅ 新方案: 按资产类别上色，图例显示类别
- 更易识别不同资产类别的风险分布
- 图例自动去重（每个类别只显示一次）

---

### 4. ✅ 数据获取优化

**解决Yahoo Finance限制:**
- ✅ 不再使用 `period='max'` (导致"delisted"错误)
- ✅ 改用 `period='10y'` (足够BRI计算，更稳定)
- ✅ 首次使用自动下载10年历史数据
- ✅ 增量更新下载2年数据

**FRED数据集成:**
- ✅ 自动识别FRED资产 (IG_SPREAD, HY_SPREAD)
- ✅ 使用FRED API而非Yahoo Finance
- ✅ 支持10年历史数据下载

---

## 文件变更清单

### 新增文件:
```
bri_app/
├── data_sources/
│   ├── __init__.py         (新增)
│   └── fred_fetcher.py     (新增) - FRED API数据获取器
├── test_fred_fetcher.py    (新增) - FRED功能测试
├── quick_test.py           (新增) - 配置快速测试
├── requirements.txt        (更新) - 添加requests依赖
└── UPDATE_NOTES.md         (新增) - 本文档
```

### 修改文件:
```
bri_app/
├── app.py                           (重大更新)
│   ├── ASSET_INFO: 更新category名称
│   ├── 新增: COMMON_ASSETS列表
│   ├── 新增: CATEGORY_COLORS映射
│   ├── 新增: get_category_color()函数
│   ├── dashboard_page(): 重构UI布局
│   └── create_bubble_chart(): 按类别上色
├── services/bri_update_service.py   (更新)
│   ├── __init__(): 添加fred_fetcher
│   ├── check_for_updates(): 支持FRED数据源
│   └── update_asset(): 智能选择数据源
└── data_fetch_and_process/bri_data_fetcher.py (更新)
    └── BRI_ASSETS: 添加IG_SPREAD和HY_SPREAD
```

---

## 使用指南

### 1. 测试FRED数据获取
```bash
cd bri_app
python test_fred_fetcher.py
```

### 2. 测试配置
```bash
python quick_test.py
```

### 3. 启动应用
```bash
.\run.bat
```

### 4. 首次使用
1. 打开 **🔄 Data Update** 页面
2. 点击 **🔍 Check for Updates**
3. 点击 **▶️ Start Update**
   - 将自动下载10年历史数据
   - 包含新增的IG和HY Spread
4. 返回 **📊 Dashboard**
5. 选择 **Common Assets** 查看核心资产

---

## 故障排除

### Q1: FRED数据获取失败
**解决方案:**
- 检查网络连接
- 验证API Key有效性
- 查看 `test_fred_fetcher.py` 输出

### Q2: Yahoo Finance "delisted" 错误
**已解决:**
- 现在使用 `period='10y'` 而非 `period='max'`
- 首次更新会自动使用正确的period

### Q3: 仍然看不到数据
**检查步骤:**
1. 删除旧数据库: `Remove-Item data\bri_data.db`
2. 重启应用: `.\run.bat`
3. 重新更新数据

---

## 技术细节

### Category标准化
| 旧名称 | 新名称 | 说明 |
|-------|--------|------|
| `Equity` | `Global Equity` | 更明确 |
| `Sector` | `US Sectors` | 区分美国行业 |
| `Credit Spread` | `Credit` | 简化 |

### FRED API限制
- 每日50,000次请求限制
- 数据更新延迟: T+1
- 仅工作日更新

---

## 下一步计划

### 待实现功能:
- [ ] 添加更多FRED指标 (VIX, Treasury spreads)
- [ ] 导出PDF报告
- [ ] 自定义警报阈值
- [ ] 历史回测功能

### 优化计划:
- [ ] 缓存FRED数据减少API调用
- [ ] 并行下载多个资产
- [ ] 增加数据验证层

---

**更新日期**: 2025-12-29
**版本**: v2.0
**作者**: BRI Development Team


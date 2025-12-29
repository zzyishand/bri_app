# BRI Bubble Risk Indicator Application

完整的泡沫风险指标（BRI）应用，包含数据获取、BRI计算、SQLite存储和可视化功能。

## 🎯 功能特性

### 1. **数据管理**
- ✅ 自动从Yahoo Finance获取26个资产的价格数据
- ✅ SQLite数据库存储，高效管理历史数据
- ✅ 支持增量更新，只下载和计算新数据
- ✅ 完整的更新日志记录

### 2. **BRI计算**
- ✅ 基于Bank of America方法论的BRI指标
- ✅ 短期(3月)、中期(6月)、长期(1年)三个时间维度
- ✅ 四个统计矩：Returns, Volatility, Momentum, Fragility
- ✅ 百分位数排名方法
- ✅ 智能增量计算，避免重复计算历史数据

### 3. **可视化界面**
- ✅ 交互式Dashboard，实时监控泡沫风险
- ✅ 气泡图热力图展示所有资产风险状况
- ✅ 详细的单资产分析（4个BRI子指标 + 价格图）
- ✅ 数据更新中心，一键检查和更新
- ✅ 更新历史日志查看

## 📊 支持的资产

### 全球股指 (9个)
- 道琼斯(DOW_JONES)、纳斯达克100(NASDAQ_100)、日经225(NIKKEI_225)
- 恒生指数(HSI)、恒生国企(HSCEI)、恒生科技(HSTECH)
- 德国DAX(DAX)、中证300(CSI300)、中证500(CSI500)

### 美国行业指数 (9个)
- 金融(XLF)、可选消费(XLY)、通信服务(XLC)
- 工业(XLI)、科技(XLK)、医疗(XLV)
- 能源(XLE)、能源指数(IXE)、生物科技(BIOTECH)

### 商品 (4个)
- 黄金(GOLD)、白银(SILVER)、原油(CRUDE_OIL)、铜(COPPER)

### 外汇 (3个)
- 美元指数(US_DOLLAR_INDEX)、日元(JPY)、欧元(EUR)

### 其他 (2个)
- 比特币(BITCOIN)、科技7巨头(MAG7)

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Windows/Linux/Mac

### 1. 安装依赖

```bash
cd bri_app
pip install -r requirements.txt
```

### 2. 启动应用

**Windows:**
```bash
run.bat
```

**Linux/Mac:**
```bash
chmod +x run.sh
./run.sh
```

**或者直接运行:**
```bash
streamlit run app.py
```

### 3. 访问应用

打开浏览器访问: `http://localhost:8501`

## 📖 使用指南

### 首次使用

1. **打开应用** → 进入 "🔄 Data Update" 页面
2. **点击 "🔍 Check for Updates"** → 检查所有资产
3. **点击 "▶️ Start Update"** → 开始下载数据和计算BRI
4. **等待完成** → 大约需要3-5分钟（26个资产）
5. **进入 "📊 Dashboard"** → 查看结果

### 日常更新

1. **进入 "🔄 Data Update"** 页面
2. **点击 "🔍 Check for Updates"** → 自动检测新数据
3. **选择需要更新的资产** → 点击 "▶️ Start Update"
4. **增量计算** → 只计算新增日期的BRI（速度快！）

### 查看历史

- **进入 "📝 Update History"** 页面
- 查看所有更新记录，包括成功/失败状态

## 📁 项目结构

```
bri_app/
├── app.py                      # Streamlit主应用
├── config.py                   # 配置文件
├── requirements.txt            # Python依赖
├── README.md                   # 说明文档
├── run.bat                     # Windows启动脚本
├── run.sh                      # Linux/Mac启动脚本
├── database/                   # 数据库模块
│   ├── __init__.py
│   └── bri_database.py        # SQLite数据库管理
├── services/                   # 业务逻辑
│   ├── __init__.py
│   └── bri_update_service.py  # 增量更新服务
├── data/                       # 数据存储（自动创建）
│   └── bri_data.db            # SQLite数据库文件
└── .streamlit/                 # Streamlit配置
    └── config.toml
```

## 🗄️ 数据库结构

### 表1: price_data（价格数据）
- 存储所有资产的历史价格（Open, High, Low, Close, Volume）
- 主键：(asset_name, date)

### 表2: bri_results（BRI结果）
- 存储计算的BRI指标
- 包含：composite_bri, short/mid/long indicators, percentiles
- 主键：(asset_name, date)

### 表3: update_log（更新日志）
- 记录所有更新操作
- 包含：时间戳、状态、影响行数、错误信息

### 表4: metadata（元数据）
- 每个资产的最新日期、记录数等信息

## 🔧 高级配置

### 修改BRI计算参数

编辑 `config.py`:
```python
BRI_CONFIG = 'default'  # 或 'conservative', 'aggressive'
```

### 修改数据库位置

编辑 `config.py`:
```python
DB_PATH = Path('/your/custom/path/bri_data.db')
```

## 📤 部署到Streamlit Cloud

### 准备工作

1. **将项目推送到GitHub仓库**
2. **确保包含以下文件:**
   - `app.py`
   - `requirements.txt`
   - `.streamlit/config.toml`
   - `database/` 和 `services/` 文件夹

### 部署步骤

1. 登录 [Streamlit Cloud](https://streamlit.io/cloud)
2. 点击 "New app"
3. 选择您的GitHub仓库
4. 设置:
   - **Main file path**: `bri_app/app.py`
   - **Python version**: 3.9+
5. 点击 "Deploy"

### 注意事项

⚠️ **Streamlit Cloud限制:**
- 免费版有1GB内存限制
- SQLite文件在重启后会丢失
- 建议定期备份数据库或使用外部数据库（PostgreSQL）

## 🐛 常见问题

### Q: 首次运行显示"No BRI data found"
**A:** 正常情况，请先到 "🔄 Data Update" 页面更新数据。

### Q: 更新失败提示"Rate limited"
**A:** Yahoo Finance限流，等待几分钟后重试，或在 `bri_data_fetcher.py` 中增加延迟时间。

### Q: 数据库文件在哪里？
**A:** 默认在 `bri_app/data/bri_data.db`

### Q: 如何重新计算所有历史数据？
**A:** 在 "🔄 Data Update" 页面的 "Manual Update" 部分，勾选 "Force full recalculation"。

### Q: 能否添加自定义资产？
**A:** 可以！编辑 `data_fetch_and_process/bri_data_fetcher.py` 的 `BRI_ASSETS` 字典，然后更新 `app.py` 的 `ASSET_INFO`。

## 📈 性能优化

### 增量更新 vs 完全重算

| 方式 | 速度 | 适用场景 |
|------|------|----------|
| 增量更新 | 快（秒级） | 日常更新 |
| 完全重算 | 慢（分钟级） | 首次使用、配置变更 |

### 建议的更新频率

- **工作日**: 每天收盘后更新一次
- **周末**: 无需更新（市场休市）
- **假期**: 按需更新

## 📚 技术文档

### BRI计算方法

详见: `indicator/BRI_METHODOLOGY_CORRECTED.md`

### API参考

- **BRIDatabase**: 数据库操作类
- **BRIUpdateService**: 更新服务类
- **BRICalculatorV2**: BRI计算器

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 📧 联系方式

如有问题，请提交Issue或联系开发者。

---

**祝使用愉快！Happy Trading! 📊🚀**


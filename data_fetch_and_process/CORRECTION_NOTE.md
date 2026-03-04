# 资产命名更正说明

## 更正日期
2025-12-12

## 更正内容

### ❌ 错误命名
之前将 ASHS ETF 错误标记为 **CSI1000** (中证1000指数)

### ✅ 正确命名
**CSI500** (中证500指数) - Xtrackers Harvest CSI 500 China A-Shares Small Cap ETF

---

## 详细说明

### ASHS ETF 实际追踪指数
- **Ticker**: ASHS
- **全名**: Xtrackers Harvest CSI 500 China A-Shares Small Cap ETF
- **追踪指数**: CSI 500 (中证500指数)
- **指数构成**: 中国 A 股市场市值排名 301-800 位的股票
- **市值类型**: 小型到中型企业

### CSI 500 vs CSI 1000 区别

| 指数 | 市值排名 | 公司数量 | 类型 | Yahoo Finance 可用性 |
|------|---------|---------|------|---------------------|
| **CSI 300** | 1-300 | 300 | 大盘股 | 有限 (000300.SS) |
| **CSI 500** | 301-800 | 500 | 中小盘股 | ✅ 通过 ASHS ETF |
| **CSI 1000** | 801-1800 | 1000 | 小盘股 | ❌ 不可用 |

### 为什么使用 CSI 500
1. **CSI 1000 不可用**: Yahoo Finance 无法获取中证1000指数数据 (000852.SS 无数据)
2. **CSI 500 是最佳替代**: 
   - 代表中国小型到中型企业
   - 通过 ASHS ETF 可获取完整历史数据 (2014年起)
   - 市值覆盖范围合理，反映中国经济活力

---

## 已更正的文件

### 1. 数据获取脚本
- ✅ `bri_data_fetcher.py` - 更新资产定义和描述

### 2. 文档
- ✅ `ASSET_REFERENCE.md` - 更新资产映射表
- ✅ `NEW_ASSETS_SUMMARY.md` - 更新新资产总结
- ✅ `README.md` - 更新资产列表

### 3. 数据文件
- ✅ `raw_data/CSI1000_20251212_015742.csv` → `raw_data/CSI500_20251212_015742.csv`

---

## 使用建议

### 分析中国市场时
```python
# 正确理解：CSI500 代表中国小型到中型企业
import pandas as pd

csi500_data = pd.read_csv('raw_data/CSI500_20251212_015742.csv', 
                          index_col='Date', parse_dates=True)

# 注意：这是 CSI 500，不是 CSI 1000
# 市值排名：301-800
# 适合分析中国中小盘股泡沫风险
```

### 对比不同市值板块
```python
# CSI 300 (大盘) vs CSI 500 (中小盘)
csi300 = pd.read_csv('raw_data/CSI300_*.csv', index_col='Date', parse_dates=True)
csi500 = pd.read_csv('raw_data/CSI500_*.csv', index_col='Date', parse_dates=True)

# 分析大盘股与中小盘股的泡沫风险差异
```

---

## 未来改进方向

### 如果需要真正的小盘股数据
由于 CSI 1000 不可用，可以考虑：
1. **使用其他数据源**: Bloomberg, Wind, Tushare (中国金融数据)
2. **使用相关 ETF**: 
   - 港股通小盘股 ETF
   - 其他追踪中国小盘股的基金
3. **自行构建**: 从个股数据构建小盘股指数

### 数据源建议
```python
# 示例：使用 Tushare 获取中国指数数据
# import tushare as ts
# pro = ts.pro_api('your_token')
# df = pro.index_daily(ts_code='000852.SH', start_date='20140101')
```

---

## 重要提醒

### ⚠️ 命名准确性很重要
- 在金融分析中，准确的指数命名至关重要
- CSI 500 和 CSI 1000 虽然都是小盘股相关，但覆盖的市值范围不同
- 误用可能导致错误的分析结论

### ✅ 当前方案
- 使用 **CSI 500 (ASHS)** 作为中国中小盘股的代表
- 明确标注这是 CSI 500，避免误导
- 在分析报告中注明数据来源和限制

---

## 致谢

感谢用户指出 ASHS 是 CSI 500 ETF 而非 CSI 1000 的错误。准确性是金融数据分析的基础。

---

**更正完成** ✅

所有相关文件和数据已更新为正确的 CSI500 命名。


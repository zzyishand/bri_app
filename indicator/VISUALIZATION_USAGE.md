# BRI 可视化使用指南

本项目提供两种可视化方式，适用于不同的使用场景。

---

## 📊 方式一：静态PNG图表（推荐用于报告/文档）

**脚本：** `simple_plot.py`  
**输出：** PNG图片文件  
**特点：** 清晰、简洁、易于分享

### 使用方法

#### 1. 为所有资产生成图表

```bash
cd indicator
python simple_plot.py
```

**输出目录：** `indicator/bri_plots/`  
**生成文件：** 每个资产3个图表
- `{ASSET}_BRI_price.png` - 🆕 **简化版：只有Composite BRI和价格**
- `{ASSET}_BRI_simple.png` - 完整版：所有BRI指标和价格
- `{ASSET}_percentiles.png` - 百分位排名图

#### 2. 为单个资产生成图表

```bash
cd indicator
python simple_plot.py NASDAQ_100
```

### 图表内容

**图表1：BRI + Price（简化版）** 🆕
- **上半部分：** Composite BRI（复合BRI）- 蓝色粗线
  - 阈值线：25%（绿色），50%（橙色），75%（红色）
  - 显示当前值、平均值、最大值
- **下半部分：** 价格曲线 - 绿色粗线
  - 显示当前价格
- **用途：** 快速查看BRI与价格的关系，最简洁清晰

**图表2：BRI指标（完整版）**
- Composite BRI（复合BRI）- 粗蓝线
- Short-term（短期）- 橙色虚线
- Mid-term（中期）- 绿色虚线
- Long-term（长期）- 红色虚线
- 价格曲线（右侧Y轴）
- 阈值线：50%（橙色）、75%（红色）
- **用途：** 查看各时间尺度的详细BRI

**图表3：百分位排名**
- 4个moment的percentile rank (0-100)
- Returns（收益）
- Volatility（波动率）
- Momentum（动量）
- Fragility（脆弱性）
- **用途：** 分析BRI的成分构成

---

## 🌐 方式二：交互式HTML仪表盘（推荐用于探索分析）

**脚本：** `create_visualizations.py`  
**输出：** HTML交互式仪表盘  
**特点：** 可缩放、可拖动、交互探索

### 使用方法

#### 1. 为所有资产生成仪表盘

```bash
cd indicator
python create_visualizations.py
```

**输出目录：** `indicator/bri_visualizations/`  
**生成文件：** 每个资产1个HTML文件
- `{ASSET}_dashboard_{timestamp}.html`

#### 2. 为单个资产生成仪表盘

```bash
cd indicator
python create_visualizations.py --asset NASDAQ_100
```

#### 3. 自定义X轴刻度

```bash
# 年度刻度（默认，推荐用于长期数据）
python create_visualizations.py --ticks Y

# 月度刻度（推荐用于1-5年数据）
python create_visualizations.py --ticks M

# 周度刻度（推荐用于1年内数据）
python create_visualizations.py --ticks W

# 日度刻度（推荐用于1个月内数据）
python create_visualizations.py --ticks D
```

#### 4. 单个资产 + 自定义刻度

```bash
python create_visualizations.py --asset BITCOIN --ticks M
```

### 交互功能

**打开HTML文件后，可以：**
- **缩放：** 在图表上点击并拖动
- **平移：** 按住Shift键并拖动
- **重置：** 双击图表
- **时间范围：** 拖动底部的范围滑块
- **图例：** 点击图例项来显示/隐藏曲线
- **悬停：** 鼠标悬停查看精确数值

---

## 📁 数据目录说明

### 输入数据
```
indicator/bri_results_v2_with_intermediates/
├── DOW_JONES_BRI_v2_*.csv
├── NASDAQ_100_BRI_v2_*.csv
├── NIKKEI_225_BRI_v2_*.csv
├── HSCEI_BRI_v2_*.csv
├── GOLD_BRI_v2_*.csv
├── CRUDE_OIL_BRI_v2_*.csv
├── BITCOIN_BRI_v2_*.csv
└── BIOTECH_BRI_v2_*.csv
```

### 输出目录

**静态PNG：**
```
indicator/bri_plots/
├── DOW_JONES_BRI_price.png       🆕 简化版（BRI+价格）
├── DOW_JONES_BRI_simple.png      完整版（所有BRI指标）
├── DOW_JONES_percentiles.png     百分位排名
├── NASDAQ_100_BRI_price.png      🆕 简化版
├── NASDAQ_100_BRI_simple.png     完整版
├── NASDAQ_100_percentiles.png    百分位排名
└── ...（每个资产3个图）
```

**交互式HTML：**
```
indicator/bri_visualizations/
├── DOW_JONES_dashboard_*.html
├── NASDAQ_100_dashboard_*.html
├── NIKKEI_225_dashboard_*.html
└── ...（每个资产1个HTML）
```

---

## 🎨 可视化对比

| 特性 | 静态PNG | 交互式HTML |
|------|---------|------------|
| **文件大小** | 小（~200KB/个） | 大（~2-5MB/个） |
| **加载速度** | 快 | 慢（需要浏览器） |
| **交互性** | ❌ 无 | ✅ 完全交互 |
| **分享** | ✅ 易于嵌入文档 | ⚠️ 需要浏览器 |
| **打印** | ✅ 优秀 | ⚠️ 一般 |
| **数据探索** | ❌ 受限 | ✅ 强大 |
| **适用场景** | 报告、论文、PPT | 数据分析、探索 |

---

## 💡 推荐使用场景

### 🖼️ 使用静态PNG（simple_plot.py）：
- 需要插入Word/PDF报告
- 制作PPT演示文稿
- 打印纸质分析报告
- 快速查看所有资产概览
- 需要轻量级文件
- **🆕 推荐使用 `*_BRI_price.png` 用于高层概览**
- **推荐使用 `*_BRI_simple.png` 用于详细分析**

### 🖥️ 使用交互式HTML（create_visualizations.py）：
- 深度数据分析
- 探索特定时间段
- 需要精确数值
- 多人在线分享（通过浏览器）
- 需要缩放细节

---

## 📝 实际使用示例

### 场景1：快速生成所有资产的报告图表

```bash
cd indicator
python simple_plot.py
```
✅ 生成24个PNG文件（8个资产 × 3个图表）  
📂 位置：`indicator/bri_plots/`  
📊 包括：简化版BRI+Price图、完整版BRI图、百分位排名图

### 场景2：深入分析NASDAQ的BRI

```bash
cd indicator
python create_visualizations.py --asset NASDAQ_100 --ticks M
```
✅ 生成1个交互式HTML  
📂 位置：`indicator/bri_visualizations/NASDAQ_100_dashboard_*.html`  
🖱️ 在浏览器中打开，可缩放查看任意时间段

### 场景3：为团队会议准备材料

```bash
# Step 1: 生成静态图表（用于PPT）
cd indicator
python simple_plot.py

# Step 2: 生成交互式仪表盘（用于现场探索）
python create_visualizations.py --ticks Y
```

✅ 两种格式都准备好  
📊 PPT用PNG，Q&A用HTML

### 场景4：管理层报告（只看BRI和价格）

```bash
cd indicator
python simple_plot.py
```

✅ 生成3类图表，**只使用 `*_BRI_price.png` 即可**  
📊 8个资产，每个一张简洁的图  
🎯 清晰展示BRI泡沫风险与价格的关系  
💡 适合：管理层汇报、投资决策会议

---

## 🛠️ 自定义修改

### 修改PNG图表样式

编辑 `indicator/simple_plot.py`：

```python
# 第53行：调整图表大小
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

# 第62行：修改线条颜色/粗细
ax1.plot(df.index, df['composite_bri'], 
        label='Composite BRI', color='#1f77b4', linewidth=2.5)

# 第78-79行：调整阈值线
ax1.axhline(y=0.5, color='orange', linestyle=':', linewidth=1)
ax1.axhline(y=0.75, color='red', linestyle=':', linewidth=1)
```

### 修改HTML仪表盘样式

编辑 `indicator/bri_visualizer.py`：

```python
# 第149-154行：修改线条样式
fig.add_trace(go.Scatter(
    x=df.index, y=df['composite_bri'],
    name='Composite BRI',
    line=dict(color='rgb(31, 119, 180)', width=3),
    mode='lines'
))
```

---

## ❓ 常见问题

### Q1: 为什么PNG图表看起来不清晰？
**A:** 编辑`simple_plot.py`第95行，增加DPI：
```python
plt.savefig(output_path, dpi=150, bbox_inches='tight')  # 改为150或更高
```

### Q2: HTML文件太大怎么办？
**A:** HTML包含所有日度数据点，这是正常的。如需减小：
- 使用PNG图表代替
- 或减少时间范围（编辑CSV文件）

### Q3: 可以同时生成两种格式吗？
**A:** 可以！依次运行两个脚本：
```bash
python simple_plot.py      # PNG
python create_visualizations.py  # HTML
```

### Q4: 如何只查看最近一年的数据？
**A:** 使用HTML交互式图表，用范围滑块选择时间段。  
或者在脚本中过滤数据（需要修改代码）。

### Q5: 三种PNG图表有什么区别？该用哪个？ 🆕
**A:** 
- **`*_BRI_price.png`（简化版）：** 只有Composite BRI和价格，最简洁
  - ✅ 适合：管理层报告、投资决策、快速概览
- **`*_BRI_simple.png`（完整版）：** 包含ST/MT/LT三个子指标
  - ✅ 适合：技术分析、详细研究、理解BRI构成
- **`*_percentiles.png`：** 显示4个moment的百分位排名
  - ✅ 适合：深度分析、理解BRI为什么高/低

**推荐：** 大多数情况下使用简化版 `*_BRI_price.png` 即可！

---

## 📚 相关文档

- **BRI计算方法：** `indicator/BRI_METHODOLOGY_CORRECTED.md`
- **项目结构：** `PROJECT_STRUCTURE.md`
- **可视化总结：** `VISUALIZATION_SUMMARY.md`
- **配置参数：** `indicator/bri_config.py`

---

## ✅ 快速开始

**最简单的方式（生成所有图表）：**

```bash
cd indicator
python simple_plot.py
```

**查看结果：**
- 打开 `indicator/bri_plots/` 文件夹
- 查看PNG图表

**完成！** 🎉


# BRI 可视化使用指南

## 📊 概述

BRI可视化系统为每个资产创建交互式HTML仪表板，包含：
- **BRI主图表**：复合BRI和三个子指标（短期/中期/长期）
- **价格叠加**：资产价格趋势
- **百分位图表**：每个时间范围的四个moment的百分位排名

## ✨ 关键特性

### 数据处理
- ✅ **使用所有daily数据点** - 不进行重采样，保留完整数据
- ✅ **仅调整X轴刻度** - 可选择显示日/周/月/年刻度
- ✅ **默认年度刻度** - 适合长时间序列

### 交互功能
- 🔍 **缩放**：在图表上点击并拖动
- 🖱️ **平移**：按住Shift键并拖动
- 🔄 **重置**：双击图表
- 📍 **范围滑块**：拖动底部滑块改变时间范围
- 👁️ **图例切换**：点击图例开关数据系列

## 🚀 快速开始

### 方式一：创建所有资产的可视化（推荐）

```bash
cd indicator
python create_visualizations.py
```

**默认设置**：
- 输入文件夹：`bri_results_v2_with_intermediates/`
- 输出文件夹：`bri_visualizations/`
- X轴刻度：年度（Y）

### 方式二：创建单个资产的可视化

```bash
python create_visualizations.py --asset NASDAQ_100 --ticks Y
```

**资产名称选项**：
- DOW_JONES
- NASDAQ_100
- NIKKEI_225
- HSCEI
- GOLD
- CRUDE_OIL
- BITCOIN
- BIOTECH

### 方式三：使用不同的刻度格式

```bash
# 每日刻度（数据点多时可能拥挤）
python create_visualizations.py --asset BITCOIN --ticks D

# 每周刻度
python create_visualizations.py --asset GOLD --ticks W

# 每月刻度（适合中等时间跨度）
python create_visualizations.py --asset NASDAQ_100 --ticks M

# 每年刻度（默认，适合长期数据）
python create_visualizations.py --asset NIKKEI_225 --ticks Y
```

## 📈 仪表板结构

每个HTML文件包含4个交互式图表：

### 1. BRI主图表
**顶部面板**：
- 蓝色粗线：复合BRI
- 橙色虚线：短期子指标
- 绿色虚线：中期子指标
- 红色虚线：长期子指标
- 阈值线：Warning (1.5), Bubble (2.0), Extreme (2.5)

**底部面板**：
- 紫色填充：资产价格

### 2. 短期百分位排名
显示3个月窗口的四个moment：
- 蓝色：Returns percentile
- 橙色：Volatility percentile
- 绿色：Momentum percentile
- 红色：Fragility percentile
- 黑色：加权平均percentile

### 3. 中期百分位排名
显示6个月窗口的四个moment

### 4. 长期百分位排名
显示1年窗口的四个moment

## 🎨 刻度格式详解

### 数据 vs 显示
```
数据层：所有daily数据点都在图表中
  ↓
显示层：仅X轴刻度标签改变
```

### 刻度格式选项

| 参数 | 描述 | 适用场景 | 示例标签 |
|------|------|----------|----------|
| `D` | 每日刻度 | 短期分析（<6个月） | 2024-12-11 |
| `W` | 每周刻度 | 中短期分析（6个月-2年） | 2024-12-11 |
| `M` | 每月刻度 | 中期分析（2-10年） | 2024-12 |
| `Y` | 每年刻度 | 长期分析（>5年）**默认** | 2024 |

### 为什么默认使用年度刻度？

1. ✅ **避免标签拥挤** - 60年数据（如Nikkei）用日刻度会非常密集
2. ✅ **更好的可读性** - 容易识别长期趋势
3. ✅ **保留所有数据** - 缩放时仍可看到daily级别
4. ✅ **专业外观** - 类似Bloomberg终端风格

## 💡 使用技巧

### 查看不同时间段

1. **使用范围滑块**（底部）
   - 拖动滑块两端调整可见范围
   - 适合快速浏览不同时期

2. **使用缩放**（鼠标）
   - 在感兴趣的区域拖动
   - 放大后可看到更多daily细节

3. **使用双击重置**
   - 快速返回全景视图

### 分析泡沫信号

1. **识别高风险期**
   - 复合BRI > 2.0：泡沫区域
   - 所有三个子指标同时升高：强烈信号

2. **检查moment贡献**
   - 切换到百分位图表
   - 查看哪个moment驱动高BRI
   - 高momentum + 高fragility = 经典泡沫模式

3. **跨资产比较**
   - 打开多个dashboard
   - 比较不同资产的BRI模式

### 导出和分享

1. **浏览器截图**
   - 使用浏览器内置截图工具
   - 或Ctrl+P打印为PDF

2. **分享HTML文件**
   - 文件是独立的，包含所有数据
   - 可通过邮件或云盘分享
   - 接收者只需浏览器即可查看

## 🔧 高级定制

### 修改默认设置

编辑 `create_visualizations.py`:

```python
# 第17行：改变默认刻度
tick_format = 'M'  # 改为月度刻度

# 第15-16行：改变输入/输出文件夹
results_dir = 'your_results_folder'
output_dir = 'your_output_folder'
```

### 编程方式使用

```python
from indicator.bri_visualizer import BRIVisualizer
import pandas as pd

# 加载数据
data = pd.read_csv('bri_results.csv', index_col=0, parse_dates=True)

# 创建visualizer
viz = BRIVisualizer()

# 创建dashboard
html_path = viz.create_dashboard(
    data,
    asset_name='My Asset',
    tick_format='M',  # 月度刻度
    output_path='my_dashboard.html'
)

print(f"Dashboard saved to: {html_path}")
```

### 只创建主图表（不含百分位）

```python
from indicator.bri_visualizer import BRIVisualizer
import pandas as pd

viz = BRIVisualizer()
data = pd.read_csv('bri_results.csv', index_col=0, parse_dates=True)

# 只创建BRI图表
fig = viz.create_bri_chart(
    data,
    asset_name='NASDAQ_100',
    tick_format='Y',
    show_price=True,
    show_thresholds=True
)

# 保存为HTML
fig.write_html('nasdaq_bri_only.html')
```

## 📁 输出文件

### 文件命名
```
{ASSET_NAME}_dashboard_{YYYYMMDD_HHMMSS}.html
```

例如：
- `NASDAQ_100_dashboard_20251211_154735.html`
- `GOLD_dashboard_20251211_154735.html`

### 文件位置
默认：`indicator/bri_visualizations/`

### 文件大小
- 典型大小：500KB - 2MB
- 包含所有daily数据和plotly库引用

## 🌐 浏览器兼容性

支持所有现代浏览器：
- ✅ Chrome/Edge（推荐）
- ✅ Firefox
- ✅ Safari
- ✅ Opera

**推荐**：Chrome或Edge以获得最佳性能

## 🐛 故障排除

### 问题：HTML文件无法打开

**解决方案**：
1. 确保使用现代浏览器
2. 检查文件路径中没有中文或特殊字符
3. 尝试复制文件到桌面再打开

### 问题：图表加载慢

**原因**：数据点太多（如60年的Nikkei）

**解决方案**：
1. 这是正常的，图表包含所有daily数据
2. 加载后交互会很流畅
3. 使用范围滑块限制可见范围

### 问题：X轴标签重叠

**解决方案**：
```bash
# 使用更少的刻度
python create_visualizations.py --asset YOUR_ASSET --ticks Y
```

### 问题：找不到数据文件

**错误信息**：`No results found for ASSET_NAME`

**解决方案**：
1. 确认在`bri_results_v2_with_intermediates/`文件夹中有数据
2. 检查资产名称拼写（大小写敏感）
3. 先运行`example_calculate_bri_v2.py`生成数据

## 📊 示例用例

### 用例1：识别当前泡沫风险

```bash
# 为所有资产创建可视化
python create_visualizations.py

# 打开所有HTML文件
# 寻找：
# - 复合BRI > 2.0的资产
# - 三个子指标都升高的资产
# - momentum和fragility percentile > 75的资产
```

### 用例2：历史泡沫分析

```bash
# 创建长期视图（年度刻度）
python create_visualizations.py --asset NASDAQ_100 --ticks Y

# 在HTML中：
# 1. 使用范围滑块移到2000年（dot-com泡沫）
# 2. 缩放查看BRI峰值
# 3. 检查百分位图表看哪些moment驱动
```

### 用例3：短期交易信号

```bash
# 使用周度刻度查看近期
python create_visualizations.py --asset BITCOIN --ticks W

# 在HTML中：
# 1. 使用范围滑块看最近6个月
# 2. 关注短期子指标的变化
# 3. 当短期BRI快速上升时警惕
```

## 📚 相关文档

- **BRI方法论**：`BRI_METHODOLOGY_CORRECTED.md`
- **计算逻辑**：`bri_calculator_v2.py`
- **配置说明**：`bri_config.py`
- **主README**：`README.md`

## 🎯 总结

**记住**：
1. ✅ 所有图表使用完整的daily数据
2. ✅ X轴刻度只影响标签显示
3. ✅ 默认年度刻度适合长期数据
4. ✅ 可以通过缩放看到任何级别的细节
5. ✅ 交互式HTML支持探索性分析

**祝分析愉快！** 📈


# 🚀 Streamlit Cloud 部署指南

## 📋 部署前准备

### 1. 确保所有文件已准备好
```
bri_app/
├── app.py                          ✅ 主应用
├── requirements.txt                ✅ Python依赖
├── packages.txt                    ✅ 系统依赖（可选）
├── .streamlit/
│   └── config.toml                 ✅ Streamlit配置
├── .gitignore                      ✅ Git忽略文件
├── database/
│   └── bri_database.py            ✅ 数据库模块
├── services/
│   ├── bri_update_service.py      ✅ 更新服务
│   └── custom_ticker_service.py   ✅ 自定义ticker服务
├── data_sources/
│   └── fred_fetcher.py            ✅ FRED数据源
└── data/                           ⚠️ 数据库文件（部署后自动创建）
```

---

## 🌐 方法1: Streamlit Cloud部署（推荐）

### Step 1: 准备GitHub仓库

#### 1.1 创建GitHub仓库
```bash
# 在GitHub上创建新仓库（例如：BRI-Dashboard）
# 不要初始化README、.gitignore或license（我们已经有了）
```

#### 1.2 初始化本地Git仓库
```bash
cd "C:\Users\ASUS\Desktop\python project\BRI\bri_app"

# 初始化Git
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: BRI Dashboard application"

# 连接到GitHub仓库（替换为你的仓库地址）
git remote add origin https://github.com/YOUR_USERNAME/BRI-Dashboard.git

# 推送到GitHub
git branch -M main
git push -u origin main
```

### Step 2: 部署到Streamlit Cloud

#### 2.1 访问Streamlit Cloud
```
1. 访问 https://share.streamlit.io/
2. 使用GitHub账号登录
3. 点击 "New app"
```

#### 2.2 配置应用
```
Repository: YOUR_USERNAME/BRI-Dashboard
Branch: main
Main file path: app.py

点击 "Deploy!"
```

#### 2.3 等待部署完成
```
部署通常需要3-5分钟
可以查看实时日志
```

---

## ⚙️ 方法2: 其他云平台部署

### Heroku部署

#### 2.1 创建Procfile
```bash
# 在bri_app目录创建Procfile（无扩展名）
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

#### 2.2 创建setup.sh
```bash
mkdir -p ~/.streamlit/

echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml
```

#### 2.3 部署命令
```bash
heroku login
heroku create your-bri-app
git push heroku main
```

### Railway.app部署

```
1. 访问 https://railway.app/
2. 连接GitHub仓库
3. 自动检测Streamlit应用
4. 点击Deploy
```

---

## 🔧 部署配置优化

### 1. 环境变量设置（可选）

如果需要保护FRED API Key，在Streamlit Cloud设置：

```
Settings → Secrets

添加：
FRED_API_KEY = "1d0565998ba35f78c5b572fa1f865a84"
```

然后修改 `data_sources/fred_fetcher.py`:
```python
import streamlit as st

# 尝试从secrets读取，否则使用默认值
try:
    FRED_API_KEY = st.secrets["FRED_API_KEY"]
except:
    FRED_API_KEY = '1d0565998ba35f78c5b572fa1f865a84'
```

### 2. 数据库持久化

⚠️ **重要**: Streamlit Cloud的文件系统是临时的！

#### 解决方案A: 使用云数据库（推荐生产环境）
```python
# 可以迁移到PostgreSQL或MySQL
# 修改 database/bri_database.py 支持远程数据库
```

#### 解决方案B: 使用Streamlit Cloud存储（简单方案）
```python
# 数据会在每次重启后丢失
# 适合演示和测试
# 用户需要重新更新数据
```

#### 解决方案C: 使用外部存储（S3/Google Drive）
```python
# 定期备份数据库到云存储
# 启动时从云存储恢复
```

### 3. 性能优化

#### 3.1 添加缓存
```python
# 已经使用了 @st.cache_resource
# 确保数据库和服务只初始化一次
```

#### 3.2 减少内存使用
```python
# 在 app.py 中添加：
import gc

# 在数据加载后
gc.collect()
```

---

## 📝 部署检查清单

### 部署前检查
- [ ] `requirements.txt` 包含所有依赖
- [ ] `.gitignore` 排除敏感文件和数据库
- [ ] `app.py` 路径引用正确（相对路径）
- [ ] 测试本地运行无错误
- [ ] Git仓库已推送到GitHub

### 部署后检查
- [ ] 应用成功启动
- [ ] 可以访问Dashboard页面
- [ ] Custom Ticker功能正常
- [ ] 数据更新功能正常
- [ ] 图表显示正常
- [ ] 没有错误日志

---

## 🐛 常见问题解决

### 问题1: ModuleNotFoundError
```
错误: No module named 'xxx'

解决:
1. 检查 requirements.txt 是否包含该模块
2. 确保版本号正确
3. 重新部署
```

### 问题2: 相对导入错误
```
错误: ImportError: attempted relative import with no known parent package

解决:
检查所有import语句，确保使用正确的相对导入：
- ✅ from database.bri_database import BRIDatabase
- ❌ from bri_app.database.bri_database import BRIDatabase
```

### 问题3: 数据库文件不存在
```
错误: No such file or directory: 'data/bri_data.db'

解决:
1. 确保 data/ 目录存在
2. 首次运行时数据库会自动创建
3. 用户需要先去 Data Update 页面更新数据
```

### 问题4: 内存超限
```
错误: MemoryError or app killed

解决:
1. 减少缓存的数据量
2. 使用 @st.cache_data 的 ttl 参数限制缓存时间
3. 升级到Streamlit Cloud付费计划
```

### 问题5: FRED API请求失败
```
错误: Request failed

解决:
1. 检查API Key是否正确
2. 检查网络连接
3. FRED API有请求限制（50,000/天）
```

---

## 🔐 安全建议

### 1. API Key保护
```python
# 使用Streamlit Secrets管理敏感信息
# 不要在代码中硬编码API Key
```

### 2. 数据库访问控制
```python
# 如果使用云数据库，设置访问权限
# 使用环境变量存储数据库凭证
```

### 3. 用户认证（可选）
```python
# 可以添加简单的密码保护
import streamlit as st

def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        return True

if check_password():
    # 显示应用内容
    main()
```

---

## 📊 监控和维护

### 1. 查看应用日志
```
Streamlit Cloud Dashboard → Your App → Logs
可以看到实时日志和错误信息
```

### 2. 应用重启
```
Settings → Reboot app
如果应用卡住或出错，可以重启
```

### 3. 更新应用
```bash
# 本地修改代码后
git add .
git commit -m "Update: description"
git push

# Streamlit Cloud会自动重新部署
```

### 4. 性能监控
```
Streamlit Cloud提供基本的性能指标：
- CPU使用率
- 内存使用率
- 请求数量
```

---

## 🎯 部署后优化建议

### 1. 添加欢迎页面
```python
# 在首次访问时显示使用说明
if 'first_visit' not in st.session_state:
    st.session_state.first_visit = True
    st.info("👋 Welcome! Please go to Data Update page to fetch initial data.")
```

### 2. 数据预加载
```python
# 可以预先加载一些示例数据
# 让用户无需等待即可看到效果
```

### 3. 添加分析统计
```python
# 使用Google Analytics追踪使用情况
# 了解哪些功能最受欢迎
```

---

## 📱 移动端优化

Streamlit应用自动响应式，但可以进一步优化：

```python
# 检测移动设备
import streamlit as st

# 移动端使用更紧凑的布局
if st.session_state.get('mobile_view', False):
    # 使用单列布局
    pass
else:
    # 使用多列布局
    pass
```

---

## 🔗 有用的链接

- **Streamlit Cloud**: https://share.streamlit.io/
- **Streamlit文档**: https://docs.streamlit.io/
- **部署指南**: https://docs.streamlit.io/streamlit-community-cloud/get-started
- **社区论坛**: https://discuss.streamlit.io/

---

## 📞 获取帮助

如果遇到部署问题：

1. **查看日志**: Streamlit Cloud Dashboard → Logs
2. **检查文档**: 本指南的故障排除部分
3. **社区支持**: Streamlit论坛
4. **GitHub Issues**: 在你的仓库创建issue

---

**最后更新**: 2025-12-29  
**部署状态**: ✅ 已准备好部署  
**预计部署时间**: 5-10分钟

**祝部署顺利！** 🚀


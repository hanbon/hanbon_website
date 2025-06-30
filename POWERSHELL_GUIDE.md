# PowerShell 启动指南

为了解决 PowerShell 中 `&&` 命令分隔符不被支持的问题，我们创建了专门的启动脚本。

## 可用的启动脚本

### 1. 启动完整项目 (推荐)
```powershell
.\start-all.ps1
```
这个脚本会自动：
- 启动 Python 后端服务器
- 启动 Vue3 前端开发服务器
- 自动安装缺失的依赖

### 2. 只启动前端
```powershell
cd hanbon-vue3-project
.\start.ps1
```

### 3. 只启动后端
```powershell
cd hanbon_python_backend
.\start.ps1
```

## 手动启动方式

如果你更喜欢手动启动，可以使用以下方式：

### 前端 (Vue3)
```powershell
# 进入前端目录
cd hanbon-vue3-project

# 安装依赖（如果需要）
npm install

# 启动开发服务器
npm run serve
```

### 后端 (Python)
```powershell
# 进入后端目录
cd hanbon_python_backend

# 激活虚拟环境
venv\Scripts\Activate.ps1

# 安装依赖（如果需要）
pip install -r requirements.txt

# 进入源码目录并启动
cd src
python app.py
```

## 解决的问题

1. **PowerShell 不支持 `&&` 命令分隔符**
   - 在 PowerShell 中应该使用 `;` 或分别执行命令
   - 我们的脚本自动处理了这个问题

2. **字符编码错误**
   - 修复了 AmapDisplay 组件中 SVG 字符串包含中文注释导致的 `btoa()` 编码错误
   - 移除了所有 SVG 中的中文注释

## 注意事项

- 确保已安装 Node.js 和 Python
- 确保 PowerShell 执行策略允许运行脚本
- 如果遇到权限问题，请以管理员身份运行 PowerShell 
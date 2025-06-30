# 🚀 食慧美食AI Agent - 快速启动指南

## 🎯 项目简介

**食慧美食AI Agent** 是一个基于Plan-Memory-Action架构的智能美食对话系统，集成DeepSeek AI、OpenMemory记忆系统和MCP工具协议。

## ⚡ 一键启动

### 1. 环境准备

```bash
# 克隆项目
git clone https://github.com/your-username/shihui_website.git
cd shihui_website

# 后端环境设置
cd shihui_python_backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux  
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 前端环境设置（新终端）
cd shihui-vue3-project
npm install
```

### 2. 配置API密钥

在 `shihui_python_backend` 目录创建 `.env` 文件：

```env
# 必需配置 - DeepSeek AI
DEEPSEEK_API_KEY=sk-your-deepseek-api-key-here

# 可选配置 - 增强功能
AMAP_API_KEY=your-amap-api-key-here
BING_API_KEY=your-bing-api-key-here  
WEATHER_API_KEY=your-openweather-api-key-here
OPENMEMORY_API_KEY=your-openmemory-api-key-here

# 应用配置
DEBUG=true
LOG_LEVEL=INFO
```

### 3. 启动服务

```bash
# 终端1 - 启动后端服务
cd shihui_python_backend/src
python app.py

# 终端2 - 启动前端服务
cd shihui-vue3-project  
npm run serve
```

### 4. 访问应用

- 🌐 **前端应用**: http://localhost:8080
- 📡 **API文档**: http://localhost:8000/docs
- 💊 **健康检查**: http://localhost:8000/health

## 🔑 API密钥获取

### DeepSeek AI (必需)
1. 访问 [DeepSeek 开放平台](https://platform.deepseek.com/)
2. 注册账号并创建API密钥
3. 复制密钥到 `.env` 文件

### 高德地图 (可选 - 地图搜索功能)
1. 访问 [高德开放平台](https://lbs.amap.com/)
2. 创建应用获取API Key
3. 启用Web服务API

### 必应搜索 (可选 - 搜索功能)
1. 访问 [Azure 认知服务](https://azure.microsoft.com/zh-cn/services/cognitive-services/bing-web-search-api/)
2. 创建必应搜索资源
3. 获取订阅密钥

### OpenWeather (可选 - 天气功能)
1. 访问 [OpenWeatherMap](https://openweathermap.org/api)
2. 免费注册获取API Key

## 🎮 使用指南

### 基础对话
- 💬 "推荐一些川菜"
- 🍳 "教我做宫保鸡丁"
- 📍 "附近有什么好吃的餐厅"
- 💡 "这道菜的营养价值如何"

### 工具功能
- 🗺️ **地图搜索**: 查找附近餐厅和美食地点
- ⭐ **智能推荐**: 基于偏好的个性化美食推荐
- 🌤️ **天气助手**: 根据天气推荐适宜美食
- 👩‍🍳 **菜谱生成**: AI生成详细制作步骤
- 🖼️ **图片搜索**: 美食相关图片查找
- 🔍 **信息搜索**: 最新美食资讯

### 快捷操作
- **Ctrl + N**: 新建对话
- **Ctrl + H**: 查看历史记录
- **Ctrl + ,**: 打开设置
- **Esc**: 关闭当前面板

## 🛠️ 开发调试

### 查看日志
```bash
# 后端日志
tail -f logs/shihui_agent.log

# 实时错误调试
cd shihui_python_backend/src
python app.py --debug
```

### 测试API
```bash
# 健康检查
curl http://localhost:8000/health

# 聊天测试
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "推荐川菜", "tools_enabled": ["food_recommendation"]}'
```

### 前端调试
```bash
cd shihui-vue3-project
npm run serve -- --mode development
```

## 🚨 常见问题

### 后端启动失败
1. 检查Python版本 (需要3.8+)
2. 确认已安装所有依赖
3. 验证 `.env` 文件配置
4. 检查端口8000是否被占用

### 前端无法访问后端
1. 确认后端服务运行在8000端口
2. 检查CORS配置
3. 验证防火墙设置

### AI功能异常
1. 验证DEEPSEEK_API_KEY是否正确
2. 检查API余额和限制
3. 查看后端日志错误信息

### 工具无法使用
1. 检查对应API密钥配置
2. 验证工具是否在前端启用
3. 确认API服务可用性

## 📦 Docker 快速部署

```bash
# 构建镜像
docker build -t shihui-food-ai .

# 运行容器
docker run -d \
  --name shihui-ai \
  -p 8000:8000 \
  -p 8080:8080 \
  -e DEEPSEEK_API_KEY=your-key \
  shihui-food-ai

# 查看日志
docker logs -f shihui-ai
```

## 🎉 开始享用

现在您可以开始与食慧美食AI助手对话了！

- 🍽️ 探索各种美食推荐
- 📖 学习烹饪技巧和菜谱
- 🗺️ 发现附近的美食地点
- 💭 享受智能化的美食对话体验

---

**有问题？** 查看 [完整文档](README.md) 或 [提交Issue](https://github.com/your-username/shihui_website/issues) 
# 🍽️ 食慧美食AI Agent 2.0

基于**Plan-Memory-Action架构**的智能美食对话系统，集成DeepSeek AI、OpenMemory记忆系统和MCP工具协议，为用户提供专业的美食咨询和推荐服务。

## ✨ 核心特性

### 🤖 AI能力
- **Plan**: 使用DeepSeek-Chat模型进行智能对话规划
- **Memory**: 集成OpenMemory实现长期记忆管理
- **Action**: 基于MCP协议的多工具协同执行

### 🛠️ 智能工具
- **🗺️ 高德地图搜索**: 附近餐厅、美食地点查找
- **⭐ 智能美食推荐**: 基于偏好的个性化推荐
- **🌤️ 天气美食助手**: 根据天气推荐适宜美食
- **👩‍🍳 AI菜谱生成**: 详细制作步骤和营养分析
- **🖼️ 美食图片搜索**: 视觉化美食展示
- **🔍 实时信息搜索**: 最新美食资讯获取

### 🎨 界面特色
- **现代化UI**: Vue3 + 响应式设计
- **3D背景效果**: 沉浸式视觉体验
- **流式对话**: 实时AI响应显示
- **智能工具面板**: 可视化工具配置
- **主题系统**: 浅色/深色模式支持

## 🏗️ 技术架构

### 后端技术栈
```
FastAPI + Python 3.8+
├── AI模型: DeepSeek Chat
├── 记忆系统: OpenMemory
├── 工具协议: MCP (Model Context Protocol)
├── 数据库: SQLite/PostgreSQL
├── 缓存: Redis (可选)
└── 部署: Docker + Uvicorn
```

### 前端技术栈
```
Vue 3 + TypeScript
├── 构建工具: Vue CLI
├── 3D渲染: Three.js
├── HTTP客户端: Axios
├── 图表库: Chart.js
└── 样式: CSS Variables + 响应式设计
```

## 🚀 快速开始

### 环境准备

1. **Python 环境**
```bash
cd shihui_python_backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Node.js 环境**
```bash
cd shihui-vue3-project
npm install
# 或使用 yarn
yarn install
```

### 配置文件

创建 `shihui_python_backend/.env` 文件：
```env
# DeepSeek AI 配置
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_API_BASE=https://api.deepseek.com/v1

# 高德地图 API
AMAP_API_KEY=your_amap_api_key_here

# 必应搜索 API
BING_API_KEY=your_bing_api_key_here

# 天气 API (OpenWeatherMap)
WEATHER_API_KEY=your_weather_api_key_here

# OpenMemory 配置 (可选)
OPENMEMORY_API_KEY=your_openmemory_api_key_here

# 应用配置
DEBUG=true
LOG_LEVEL=INFO
```

### 启动服务

1. **启动后端服务**
```bash
cd shihui_python_backend/src
python app.py
```
后端服务将在 `http://localhost:8000` 启动

2. **启动前端服务**
```bash
cd shihui-vue3-project
npm run serve
```
前端应用将在 `http://localhost:8080` 启动

### API文档
访问 `http://localhost:8000/docs` 查看自动生成的API文档

## 📋 功能清单

### ✅ 已完成功能

#### 后端核心
- [x] FastAPI应用框架
- [x] Plan-Memory-Action架构
- [x] DeepSeek AI集成
- [x] OpenMemory记忆系统
- [x] MCP工具管理框架
- [x] 流式响应支持
- [x] 健康检查接口
- [x] 配置管理系统

#### MCP工具实现
- [x] 高德地图搜索工具
- [x] 智能美食推荐工具
- [x] 天气API工具
- [x] AI菜谱生成工具
- [x] 必应搜索工具
- [x] 图片搜索工具

#### 前端界面
- [x] Vue3主应用框架
- [x] AI对话界面
- [x] 顶部导航栏
- [x] 工具配置面板
- [x] 系统设置面板
- [x] 浮动操作按钮
- [x] 聊天历史管理
- [x] 3D背景效果
- [x] 响应式设计
- [x] 主题系统

### 🔄 计划改进
- [ ] 用户认证系统
- [ ] 多语言国际化
- [ ] 语音对话功能
- [ ] 图片上传识别
- [ ] 社交分享功能
- [ ] 数据分析面板

## 🔧 开发指南

### 项目结构
```
shihui_website/
├── shihui_python_backend/              # 后端服务
│   ├── src/
│   │   ├── app.py                      # 主应用入口
│   │   ├── agents/                     # AI代理
│   │   │   └── food_agent.py           # 美食AI代理
│   │   ├── memory/                     # 记忆系统
│   │   │   └── openmemory_client.py
│   │   ├── mcp_tools/                  # MCP工具
│   │   │   ├── mcp_manager.py          # 工具管理器
│   │   │   └── tools/                  # 具体工具实现
│   │   └── config/                     # 配置文件
│   ├── requirements.txt                # Python依赖
│   └── tests/                          # 测试文件
├── shihui-vue3-project/                # 前端应用
│   ├── src/
│   │   ├── App.vue                     # 主应用组件
│   │   ├── components/                 # Vue组件
│   │   │   ├── ChatInterface.vue       # 对话界面
│   │   │   ├── HeaderNavigation.vue    # 导航栏
│   │   │   ├── ToolPanel.vue           # 工具面板
│   │   │   ├── SettingsPanel.vue       # 设置面板
│   │   │   ├── FloatingButtons.vue     # 浮动按钮
│   │   │   ├── ChatHistory.vue         # 历史记录
│   │   │   └── ThreeBackground.vue     # 3D背景
│   │   ├── assets/                     # 静态资源
│   │   └── main.js                     # 入口文件
│   ├── package.json                    # Node.js依赖
│   └── vue.config.js                   # Vue配置
└── README.md                           # 项目说明
```

### 添加新工具

1. **创建工具类** (`shihui_python_backend/src/mcp_tools/tools/new_tool.py`)
```python
class NewTool:
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        # 实现工具逻辑
        return {
            "success": True,
            "tool_name": "new_tool",
            "data": result
        }
```

2. **注册工具** (在 `mcp_manager.py` 中)
```python
from .tools.new_tool import NewTool

# 在 initialize 方法中添加
self.tools["new_tool"] = NewTool(config.NEW_TOOL_API_KEY)
```

3. **前端配置** (在 `ToolPanel.vue` 中添加工具配置)

### API接口说明

#### 主要接口
- `POST /chat` - 发送聊天消息
- `POST /chat/stream` - 流式聊天
- `GET /tools/available` - 获取可用工具
- `POST /tools/execute` - 执行工具
- `GET /health` - 健康检查

#### 请求示例
```javascript
// 发送聊天消息
const response = await fetch('/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: "推荐一些川菜",
    tools_enabled: ["food_recommendation", "amap_search"]
  })
})
```

## 🚢 部署指南

### Docker 部署
```bash
# 构建镜像
docker build -t shihui-food-ai .

# 运行容器
docker run -p 8000:8000 -p 8080:8080 \
  -e DEEPSEEK_API_KEY=your_key \
  -e AMAP_API_KEY=your_key \
  shihui-food-ai
```

### 生产环境配置
- 使用 PostgreSQL 数据库
- 配置 Redis 缓存
- 设置 Nginx 反向代理
- 启用 HTTPS
- 配置日志收集

## 🧪 测试

### 后端测试
```bash
cd shihui_python_backend
pytest tests/
```

### 前端测试
```bash
cd shihui-vue3-project
npm run test
```

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 💬 联系方式

- 项目维护者: 食慧科技团队
- 邮箱: contact@shihui.tech
- 项目主页: https://github.com/shihui/shihui_website

---

**🚀 享受AI美食之旅！** 如有问题，请查看文档或提交Issue。

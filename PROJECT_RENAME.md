# 🔄 项目重命名指南：汉邦 → 食慧

## 📋 重命名变更清单

### ✅ 已完成的变更

#### 📚 文档文件
- [x] `README.md` - 项目主文档
- [x] `PROJECT_RENAME.md` - 重命名指南（新增）

#### 🖥️ 前端项目 (hanbon-vue3-project → shihui-vue3-project)
- [x] `package.json` - 项目名称
- [x] `src/App.vue` - 应用名称、localStorage键名
- [x] `src/components/HeaderNavigation.vue` - 品牌名称、logo路径
- [x] `src/components/ChatInterface.vue` - 标题、logo路径
- [x] `src/components/SettingsPanel.vue` - 开发者信息、导出文件名
- [x] `src/components/FloatingButtons.vue` - 帮助文档
- [x] `src/components/ChatHistory.vue` - localStorage键名、导出文件名、分享文本

#### ⚙️ 后端项目 (hanbon_python_backend → shihui_python_backend)
- [x] `src/app.py` - 应用标题、描述、日志信息
- [x] `config/development.py` - 数据库名、日志文件名
- [x] `config/production.py` - 日志文件名、CORS域名

## 🎯 核心名称变更

| 原名称 | 新名称 | 说明 |
|--------|--------|------|
| 汉邦 | 食慧 | 中文品牌名 |
| hanbon | shihui | 英文标识符 |
| 汉邦美食AI Agent | 食慧美食AI Agent | 完整产品名 |
| hanbon_settings | shihui_settings | localStorage键名 |
| hanbon_enabled_tools | shihui_enabled_tools | localStorage键名 |
| hanbon_chat_history | shihui_chat_history | localStorage键名 |
| hanbon_agent.db | shihui_agent.db | 数据库文件名 |
| hanbon_agent.log | shihui_agent.log | 日志文件名 |

## 📂 目录重命名建议

为了保持一致性，建议手动重命名以下目录：

```bash
# 前端项目目录
mv hanbon-vue3-project shihui-vue3-project

# 后端项目目录  
mv hanbon_python_backend shihui_python_backend

# 如果有的话，主项目目录
mv hanbon_website shihui_website
```

## 🖼️ 资源文件更新

需要更新的资源文件：
- [ ] `src/assets/hanbon_logo.png` → `src/assets/shihui_logo.png`
- [ ] 网站favicon
- [ ] 其他品牌相关图片资源

## 🔧 环境配置更新

### .env 文件
保持不变，因为使用的是第三方API密钥，与品牌名无关。

### Docker 配置
如果使用Docker，需要更新：
```bash
# 原命令
docker build -t hanbon-food-ai .

# 新命令
docker build -t shihui-food-ai .
```

## 🌐 域名和部署

### 生产环境域名更新
- 原域名：`hanbon.xyz`、`www.hanbon.xyz`
- 新域名：`shihui.xyz`、`www.shihui.xyz`

### 部署脚本更新
如果有部署脚本，需要更新：
- 项目路径
- 容器名称
- 服务名称

## 📝 API文档更新

FastAPI自动生成的文档会自动反映新的应用名称：
- 访问 `http://localhost:8000/docs` 查看更新后的API文档

## ✅ 验证清单

重命名完成后，请验证以下功能：

### 前端验证
- [ ] 页面标题显示为"食慧美食AI"
- [ ] Logo和品牌名正确显示
- [ ] 设置导出文件名包含"shihui"
- [ ] 聊天历史导出文件名包含"shihui"
- [ ] localStorage中使用新的键名

### 后端验证
- [ ] API文档标题为"食慧美食AI Agent"
- [ ] 健康检查返回正确的应用名称
- [ ] 日志文件使用新的文件名
- [ ] 数据库文件使用新的文件名

### 功能验证
- [ ] AI对话功能正常
- [ ] 工具执行正常
- [ ] 设置保存/加载正常
- [ ] 聊天历史管理正常

## 🎉 重命名完成

恭喜！项目已成功从"汉邦"重命名为**"食慧"**！

新的品牌名称"食慧"更好地体现了：
- 🧠 **智慧**：AI技术的智能化
- 🍽️ **美食**：专注食物领域的专业性
- 💭 **好记**：简洁明了，朗朗上口
- 🎯 **现代**：符合现代科技产品的命名趋势

---

*如有遗漏的地方，请及时补充更新。* 
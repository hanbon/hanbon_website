# 🌟 Hanbon 全栈项目

欢迎来到 Hanbon 全栈项目！这是一个结合 Vue3 前端、Python 后端和 Three.js 动态背景的现代化 Web 应用。让我们一起探索这个项目的魅力吧！✨

## 📦 项目结构

- **前端**: 使用 Vue3 和 Three.js 构建的动态背景和智能搜索功能。
  - **ThreeBackground.vue**: 使用 Three.js 创建的动态背景组件。
  - **SearchComponent.vue**: 提供智能搜索功能的组件。
- **后端**: 使用 Python 构建的后端服务，提供 API 支持。
  - **see.py**: 处理后端逻辑的核心文件。
- **部署脚本**: 使用 PowerShell 脚本进行自动化部署。
  - **deploy.ps1**: 部署和配置服务器的脚本。
- **SSL 证书**: 确保数据传输的安全性。
  - **hanbon.xyz.key**: 私钥文件。
  - **hanbon.xyz_bundle.pem**: 证书文件。

## 🚀 快速开始

### 安装依赖

```bash
yarn install
```

### 启动开发服务器

```bash
yarn serve
```

### 构建生产版本

```bash
yarn build
```

### 代码检查与修复

```bash
yarn lint
```

## 🌈 功能亮点

- **动态背景**: 使用 Three.js 创建的炫酷动态背景，提升用户体验。
- **智能搜索**: 通过后端 API 提供智能搜索功能，快速获取所需信息。
- **响应式设计**: 适配各种设备，确保最佳的用户体验。
- **自动化部署**: 使用 PowerShell 脚本轻松部署和配置服务器。

## 🔧 配置指南

### SSL 配置

项目中包含 SSL 证书配置，确保数据传输的安全性。请根据 `deploy.ps1` 脚本中的说明进行配置。

### 部署

使用 `deploy.ps1` 脚本可以轻松部署前端和后端代码。支持首次部署、更新代码、重启服务等功能。

## 📚 参考资料

- [Vue.js 官方文档](https://vuejs.org/)
- [Three.js 官方文档](https://threejs.org/docs/)
- [Python 官方文档](https://docs.python.org/3/)
- [小红书风格设计指南](https://www.xiaohongshu.com/)

## ❤️ 感谢

感谢所有为这个项目贡献代码和创意的开发者们！如果你喜欢这个项目，欢迎给我们一个 Star ⭐️！

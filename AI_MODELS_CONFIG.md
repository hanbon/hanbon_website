# 🤖 AI模型配置指南

## 概述

食慧美食AI Agent现在支持多个AI模型，您可以根据需要配置不同的模型并在聊天时自由切换。

## 支持的AI模型

### 1. DeepSeek（主要推荐）
- **模型ID**: `deepseek`
- **描述**: 专业的中文对话模型，针对中文优化
- **获取API**: https://platform.deepseek.com/
- **配置项**:
  ```env
  DEEPSEEK_API_KEY=your_deepseek_api_key_here
  DEEPSEEK_API_BASE=https://api.deepseek.com/v1
  DEEPSEEK_MODEL=deepseek-chat
  DEEPSEEK_MAX_TOKENS=4000
  DEEPSEEK_TEMPERATURE=0.7
  ```

### 2. Qwen（通义千问）
- **模型ID**: `qwen`
- **描述**: 阿里云通义千问大模型
- **获取API**: https://dashscope.aliyuncs.com/
- **配置项**:
  ```env
  QWEN_API_KEY=your_qwen_api_key_here
  QWEN_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
  QWEN_MAX_TOKENS=4000
  QWEN_TEMPERATURE=0.7
  ```

### 3. ChatGPT
- **模型ID**: `chatgpt`
- **描述**: OpenAI GPT-3.5 Turbo
- **获取API**: https://platform.openai.com/
- **配置项**:
  ```env
  OPENAI_API_KEY=your_openai_api_key_here
  OPENAI_API_BASE=https://api.openai.com/v1
  OPENAI_MAX_TOKENS=4000
  OPENAI_TEMPERATURE=0.7
  ```

### 4. GPT-4
- **模型ID**: `gpt4`
- **描述**: OpenAI GPT-4 高级模型
- **获取API**: https://platform.openai.com/
- **配置项**:
  ```env
  OPENAI_API_KEY=your_openai_api_key_here
  OPENAI_API_BASE=https://api.openai.com/v1
  GPT4_MAX_TOKENS=8000
  GPT4_TEMPERATURE=0.7
  ```

## 配置步骤

### 1. 创建环境变量文件
在 `hanbon_python_backend` 目录下创建 `.env` 文件：

```bash
cd hanbon_python_backend
cp .env.example .env  # 如果有示例文件
# 或者直接创建新文件
touch .env
```

### 2. 配置API密钥
编辑 `.env` 文件，添加您的API密钥：

```env
# 设置默认模型
DEFAULT_AI_MODEL=deepseek

# DeepSeek配置（推荐）
DEEPSEEK_API_KEY=sk-your-deepseek-key-here

# 可选：其他模型配置
QWEN_API_KEY=your-qwen-key-here
OPENAI_API_KEY=sk-your-openai-key-here
```

### 3. 重启服务
```bash
# 停止当前服务
# 重新启动后端服务
cd hanbon_python_backend
python src/app.py
```

## 使用方法

### 在前端界面选择模型
1. 打开聊天界面
2. 在输入框上方找到"🤖 选择AI模型"下拉框
3. 选择您想使用的模型
4. 开始聊天，所有消息将使用选定的模型处理

### API调用时指定模型
```json
{
  "message": "推荐一道川菜",
  "model": "deepseek",
  "session_id": "session_123",
  "tools_enabled": ["food_recommendation"]
}
```

## 模型特点对比

| 模型 | 中文能力 | 响应速度 | 费用 | 推荐场景 |
|------|----------|----------|------|----------|
| DeepSeek | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 中文美食咨询（推荐） |
| Qwen | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 专业知识问答 |
| ChatGPT | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 通用对话 |
| GPT-4 | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | 复杂推理任务 |

## 故障排除

### 模型不显示在选择列表中
- 检查 `.env` 文件中的API密钥是否正确配置
- 确认API密钥有效且有余额
- 查看后端日志是否有错误信息

### 选择模型后无响应
- 检查对应模型的API端点是否可访问
- 验证API密钥权限
- 查看网络连接是否正常

### 模型响应错误
- 检查API配额是否用完
- 验证模型配置参数（max_tokens, temperature等）
- 查看后端错误日志

## 最佳实践

1. **推荐配置**: 至少配置DeepSeek模型，它对中文和美食场景优化最好
2. **备用模型**: 配置多个模型作为备用，提高服务可用性
3. **模型选择**: 
   - 日常美食咨询 → DeepSeek
   - 专业营养分析 → Qwen
   - 创意菜谱 → GPT-4
   - 快速问答 → ChatGPT

4. **成本控制**: 根据使用频率和预算选择合适的模型组合

## 注意事项

- API密钥请妥善保管，不要泄露
- 不同模型有不同的计费方式，请注意成本控制
- 某些模型可能有地区限制，请确认可用性
- 建议定期检查API配额和余额 
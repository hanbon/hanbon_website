# AI模型配置指南

## 概述

后端支持多种AI模型配置方式：
1. **内置模型配置**：通过环境变量配置
2. **自定义模型配置**：通过API动态添加

## 环境变量配置

在 `.env` 文件中配置以下环境变量：

### DeepSeek 配置
```env
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_API_BASE=https://api.deepseek.com/v1
DEEPSEEK_MAX_TOKENS=4000
DEEPSEEK_TEMPERATURE=0.7
```

### OpenAI 配置
```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_MAX_TOKENS=4000
OPENAI_TEMPERATURE=0.7
GPT4_MAX_TOKENS=8000
GPT4_TEMPERATURE=0.7
```

### Qwen 配置
```env
QWEN_API_KEY=your_qwen_api_key
QWEN_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MAX_TOKENS=4000
QWEN_TEMPERATURE=0.7
```

### Claude 配置
```env
ANTHROPIC_API_KEY=your_anthropic_api_key
ANTHROPIC_API_BASE=https://api.anthropic.com
CLAUDE_MAX_TOKENS=4000
CLAUDE_TEMPERATURE=0.7
```

### Moonshot 配置
```env
MOONSHOT_API_KEY=your_moonshot_api_key
MOONSHOT_API_BASE=https://api.moonshot.cn/v1
MOONSHOT_MAX_TOKENS=8000
MOONSHOT_TEMPERATURE=0.7
```

### 默认模型设置
```env
DEFAULT_AI_MODEL=deepseek
```

## API接口使用

### 1. 获取可用模型
```http
GET /models/available
```

响应：
```json
{
  "models": [
    {
      "id": "deepseek",
      "name": "DeepSeek",
      "description": "专业的中文对话模型",
      "supports_streaming": true,
      "max_tokens": 4000,
      "type": "builtin"
    }
  ],
  "default_model": "deepseek",
  "count": 1
}
```

### 2. 添加自定义模型
```http
POST /models/{model_id}
Content-Type: application/json

{
  "name": "我的自定义模型",
  "model": "gpt-3.5-turbo",
  "api_key": "your_api_key",
  "api_base": "https://api.openai.com/v1",
  "max_tokens": 4000,
  "temperature": 0.7,
  "supports_streaming": true,
  "description": "自定义OpenAI模型",
  "enabled": true
}
```

### 3. 更新模型配置
```http
PUT /models/{model_id}
Content-Type: application/json

{
  "temperature": 0.8,
  "max_tokens": 6000,
  "enabled": true
}
```

### 4. 删除自定义模型
```http
DELETE /models/{model_id}
```

### 5. 验证模型配置
```http
POST /models/{model_id}/validate
```

### 6. 刷新模型配置
```http
POST /models/refresh
```

## 前端使用

### 在聊天接口中指定模型
```http
POST /chat
Content-Type: application/json

{
  "message": "你好",
  "model": "gpt4",
  "user_id": "user123",
  "session_id": "session456"
}
```

### 流式聊天中指定模型
```http
POST /chat/stream
Content-Type: application/json

{
  "message": "告诉我一道菜的做法",
  "model": "deepseek",
  "tools_enabled": ["recipe_generator"]
}
```

## 配置文件

自定义模型配置存储在：`config/custom_models.json`

示例配置：
```json
{
  "my_custom_gpt": {
    "name": "我的GPT",
    "model": "gpt-3.5-turbo",
    "api_key": "sk-...",
    "api_base": "https://api.openai.com/v1",
    "max_tokens": 4000,
    "temperature": 0.7,
    "supports_streaming": true,
    "description": "自定义GPT配置",
    "enabled": true,
    "type": "custom"
  }
}
```

## 安全注意事项

1. **API密钥保护**：永远不要在响应中返回完整的API密钥
2. **权限控制**：只有管理员用户应该能够添加/修改模型配置
3. **验证配置**：添加新模型前会自动验证配置是否有效
4. **备份配置**：重要的自定义配置应定期备份

## 故障排除

### 模型不可用
1. 检查API密钥是否正确
2. 检查API基础URL是否可访问
3. 验证模型名称是否正确
4. 查看日志文件获取详细错误信息

### 配置不生效
1. 重启应用服务
2. 调用刷新配置接口
3. 检查环境变量是否设置正确
4. 验证JSON配置文件格式 
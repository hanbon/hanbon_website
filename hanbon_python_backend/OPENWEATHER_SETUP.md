# OpenWeather API 配置指南

## 🌤️ 关于 OpenWeather API

OpenWeather API 是一个免费的天气数据服务，提供全球实时天气信息和天气预报。我们使用它来替换之前的高德天气API，以获得更好的国际化支持和更丰富的天气数据。

## 📋 获取 API 密钥

### 1. 注册账号
访问 [OpenWeather](https://openweathermap.org/api) 官网并注册账号。

### 2. 获取 API 密钥
1. 登录后进入 [API keys](https://home.openweathermap.org/api_keys) 页面
2. 复制默认生成的 API 密钥，或创建新的密钥
3. API 密钥通常在几分钟内生效

### 3. 免费版本限制
- **调用频率**: 每分钟 60 次
- **每日限制**: 1,000 次
- **支持功能**: 当前天气、5天预报、历史数据

## ⚙️ 配置步骤

### 1. 设置环境变量
在项目的 `.env` 文件中添加以下配置：

```bash
# OpenWeather API配置
OPENWEATHER_API_KEY=你的API密钥
```

如果没有 `.env` 文件，请复制 `environment_example.txt` 并重命名为 `.env`。

### 2. 验证配置
重启后端服务后，尝试调用天气查询功能：

```bash
# 进入后端目录
cd hanbon_python_backend

# 重启服务
./start.ps1
```

## 🔧 API 功能特性

### 支持的查询方式
- **城市名查询**: `"Beijing,CN"`, `"New York,US"`
- **经纬度查询**: `lat=39.9042, lon=116.4074`
- **当前天气**: `extensions="base"`
- **天气预报**: `extensions="forecast"`

### 返回的天气数据
- 温度（摄氏度）
- 湿度百分比
- 风向和风速
- 体感温度
- 大气压力
- 能见度
- 天气描述（中文）

### 美食建议功能
根据天气状况自动生成相应的美食建议：
- 🌧️ 雨天：热茶、暖胃粥品
- ☀️ 晴天：户外烧烤、清爽沙拉
- ❄️ 雪天：热乎火锅、温热饮品
- 🌡️ 高温：冰镇啤酒、凉面、冰淇淋
- 🌡️ 低温：热汤面条、麻辣火锅

## 🔍 故障排除

### 常见错误

#### 401 Unauthorized
- **原因**: API 密钥无效或未设置
- **解决**: 检查 `.env` 文件中的 `OPENWEATHER_API_KEY` 是否正确

#### 429 Too Many Requests
- **原因**: 超过了API调用频率限制
- **解决**: 等待一分钟后重试，或升级到付费版本

#### 400 Bad Request
- **原因**: 请求参数错误（如城市名不存在）
- **解决**: 检查城市名格式，建议使用 `"城市名,国家代码"` 格式

### 检查日志
查看后端日志以获取详细错误信息：

```bash
# Windows PowerShell
Get-Content hanbon_python_backend/logs/hanbon_agent.log -Tail 50
```

## 📚 API 文档参考

- [OpenWeather Current Weather API](https://openweathermap.org/current)
- [OpenWeather 5 Day Forecast API](https://openweathermap.org/forecast5)
- [API 参数说明](https://openweathermap.org/api/one-call-api)

## 🆙 升级选项

如果需要更高的调用限制，可以考虑升级到付费版本：
- **Startup**: $40/月，100万次调用
- **Developer**: $180/月，300万次调用
- **Professional**: $600/月，1500万次调用

## 📞 技术支持

如果在配置过程中遇到问题，请检查：
1. API 密钥是否正确复制
2. 网络连接是否正常
3. 防火墙是否阻止了 API 请求
4. 后端服务是否正常启动

配置完成后，您就可以享受更准确、更丰富的天气查询功能了！🌈 
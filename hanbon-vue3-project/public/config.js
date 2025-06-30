// 全局配置文件
window.APP_CONFIG = {
  // 高德地图API密钥 - 请替换为您的实际密钥
  // 获取方式：https://lbs.amap.com/
  AMAP_KEY: "41fe5ec8dbd72f2411389d53f4a41e57",
  
  // 后端API地址
  API_BASE_URL: process?.env?.NODE_ENV === 'production' ? 'https://your-domain.com' : 'http://localhost:8000',
  
  // MCP工具配置
  MCP_TOOLS: {
    // 高德地图工具
    amap: {
      enabled: true,
      name: '高德地图搜索',
      description: '搜索附近餐厅和位置信息'
    },
    
    // 图片搜索工具
    image_search: {
      enabled: true,
      name: '图片搜索',
      description: '搜索美食相关图片'
    }
  },
  
  // 地图默认配置
  MAP_CONFIG: {
    // 默认中心点坐标 (长沙)
    center: [112.982279, 28.194090],
    // 默认缩放级别
    zoom: 13,
    // 搜索半径（米）
    radius: 5000
  },
  
  // 调试模式
  DEBUG: true
}

// 兼容性检查
console.log('🎯 应用配置已加载:', window.APP_CONFIG)

// 开发环境提示
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
  console.log('🔧 当前运行在开发环境')
  
  if (window.APP_CONFIG.AMAP_KEY === '请在这里输入您的高德地图API密钥') {
    console.warn('⚠️ 请在 public/config.js 中设置您的高德地图API密钥')
    console.info('📋 获取API密钥：https://lbs.amap.com/')
  } else {
    console.log('✅ 高德地图API密钥已配置:', window.APP_CONFIG.AMAP_KEY.substring(0, 8) + '...')
  }
} else {
  console.log('🌍 当前运行在生产环境')
} 
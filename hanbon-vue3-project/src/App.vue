<template>
  <div id="app">
    <!-- 3D背景 -->
    <!-- <ThreeBackground /> -->
    
    <!-- 主界面容器 -->
    <div class="main-container">
      <!-- 顶部导航栏 -->
      <HeaderNavigation 
        @toggleSettings="showSettings = !showSettings"
        @toggleTools="showToolPanel = !showToolPanel"
      />
      
      <!-- 开发者测试按钮 -->
      <div class="dev-test-button">
        <button @click="toggleTestMode" class="test-btn">
          {{ showTestMode ? '关闭测试' : '开发测试' }}
        </button>
      </div>
      
      <!-- 调试状态面板 -->
      <div class="debug-panel" v-if="showTestMode">
        <h4>调试信息</h4>
        <div class="debug-item">
          <span>聊天历史面板: </span>
          <span :class="{ active: showChatHistory }">{{ showChatHistory ? '已显示' : '已隐藏' }}</span>
          <button @click="showChatHistory = !showChatHistory" class="toggle-btn">切换</button>
        </div>
        <div class="debug-item">
          <span>记忆管理面板: </span>
          <span :class="{ active: showMemoryPanel }">{{ showMemoryPanel ? '已显示' : '已隐藏' }}</span>
          <button @click="showMemoryPanel = !showMemoryPanel" class="toggle-btn">切换</button>
        </div>
        <div class="debug-item">
          <span>设置面板: </span>
          <span :class="{ active: showSettings }">{{ showSettings ? '已显示' : '已隐藏' }}</span>
          <button @click="showSettings = !showSettings" class="toggle-btn">切换</button>
        </div>
        <div class="debug-item">
          <span>工具面板: </span>
          <span :class="{ active: showToolPanel }">{{ showToolPanel ? '已显示' : '已隐藏' }}</span>
          <button @click="showToolPanel = !showToolPanel" class="toggle-btn">切换</button>
        </div>
      </div>
      
      <!-- 测试模式切换 -->
      <div class="test-mode-toggle" v-if="showTestMode">
        <button @click="currentView = 'main'" :class="{ active: currentView === 'main' }">
          主界面
        </button>
        <button @click="currentView = 'image-test'" :class="{ active: currentView === 'image-test' }">
          图片搜索测试
        </button>
        <button @click="currentView = 'map-test'" :class="{ active: currentView === 'map-test' }">
          地图测试
        </button>
      </div>
      
      <!-- 主界面视图 -->
      <div v-if="currentView === 'main'">
        <!-- AI对话界面 -->
        <ChatInterface 
          ref="chatInterface"
          :enabled-tools="enabledTools"
          @toolsUsed="handleToolsUsed"
          @messagesChanged="handleMessagesChanged"
        />
        
        <!-- 工具面板 -->
        <ToolPanel 
          v-if="showToolPanel"
          :enabled-tools="enabledTools"
          @toggleTool="toggleTool"
          @close="showToolPanel = false"
        />
        
        <!-- 设置面板 -->
        <SettingsPanel 
          v-if="showSettings"
          :settings="settings"
          @updateSettings="updateSettings"
          @close="showSettings = false"
        />
        
        <!-- 浮动按钮组 -->
        <FloatingButtons 
          :has-messages="hasMessages"
          @newChat="startNewChat"
          @showHistory="showHistory"
          @showSettings="showSettingsPanel"
          @showMemory="showMemoryManagement"
        />
        
        <!-- 聊天历史面板 -->
        <ChatHistory 
          v-if="showChatHistory"
          @close="showChatHistory = false"
          @loadChat="loadChatHistory"
        />
        
        <!-- 记忆管理面板 -->
        <MemoryPanel 
          v-if="showMemoryPanel"
          :memory-enabled="settings.enableMemory"
          :user-id="currentUser.id"
          @close="showMemoryPanel = false"
          @toggleMemory="handleToggleMemory"
          @memoryUpdated="handleMemoryUpdated"
        />
      </div>
      
      <!-- 图片搜索测试视图 -->
      <div v-if="currentView === 'image-test'">
        <ImageGalleryTest />
      </div>
      
      <!-- 地图测试视图 -->
      <div v-if="currentView === 'map-test'">
        <MapTest />
      </div>
    </div>
  </div>
</template>

<script>
// import ThreeBackground from './components/ThreeBackground.vue'
import HeaderNavigation from './components/HeaderNavigation.vue'
import ChatInterface from './components/ChatInterface.vue'
import ToolPanel from './components/ToolPanel.vue'
import SettingsPanel from './components/SettingsPanel.vue'
import FloatingButtons from './components/FloatingButtons.vue'
import ChatHistory from './components/ChatHistory.vue'
import MemoryPanel from './components/MemoryPanel.vue'
import ImageGalleryTest from './components/ImageGalleryTest.vue'
import MapTest from './components/MapTest.vue'

/**
 * @description 食慧美食AI Agent主应用组件
 * 集成AI对话、工具选择、设置管理等功能
 */
export default {
  name: 'App',
  components: {
    // ThreeBackground,
    HeaderNavigation,
    ChatInterface,
    ToolPanel,
    SettingsPanel,
    FloatingButtons,
    ChatHistory,
    MemoryPanel,
    ImageGalleryTest,
    MapTest
  },
  data() {
    return {
      // 界面状态
      showSettings: false,
      showToolPanel: false,
      showChatHistory: false,
      showMemoryPanel: false,
      showTestMode: false,
      currentView: 'main',
      
      // 工具配置
      enabledTools: [
        'amap_search',
        'food_recommendation',
        'weather_api',
        'image_search'
      ],
      
      // 应用设置
      settings: {
        theme: 'light',
        language: 'zh-CN',
        aiPersonality: 'friendly_food_expert',
        enableNotifications: true,
        autoSaveHistory: true,
        streamResponse: true,
        enableMemory: true,
        autoSaveMemory: true,
        maxMemoryCount: 200,
        maxMessageHistory: 50
      },
      
      // 用户信息
      currentUser: {
        id: 'default',
        name: '美食爱好者',
        preferences: {
          cuisine: ['川菜', '湘菜'],
          spicyLevel: '中辣',
          dietaryRestrictions: []
        }
      },
      
      // 消息状态
      hasMessages: false
    }
  },
  mounted() {
    this.initializeApp()
    
    // 添加全局错误处理器
    window.addEventListener('error', this.handleGlobalError)
    window.addEventListener('unhandledrejection', this.handleUnhandledRejection)
  },
  beforeUnmount() {
    // 清理全局错误处理器
    window.removeEventListener('error', this.handleGlobalError)
    window.removeEventListener('unhandledrejection', this.handleUnhandledRejection)
  },
  methods: {
    /**
     * @description 初始化应用
     */
    async initializeApp() {
      try {
        // 加载用户设置
        await this.loadUserSettings()
        
        // 应用主题
        this.applyTheme()
        
        // 尝试检查后端连接（但不阻塞应用启动）
        this.checkBackendConnection().catch(error => {
          console.warn('后端服务暂时不可用，将使用前端模式:', error.message)
        })
        
        console.log('食慧美食AI Agent初始化完成')
      } catch (error) {
        console.error('应用初始化失败:', error)
        // 移除可能不存在的通知方法
        console.warn('应用初始化部分失败，但前端功能仍可使用')
      }
    },
    
    /**
     * @description 加载用户设置
     */
    async loadUserSettings() {
      try {
        const savedSettings = localStorage.getItem('hanbon_settings')
        const savedTools = localStorage.getItem('hanbon_enabled_tools')
        const savedUser = localStorage.getItem('hanbon_user')
        
        if (savedSettings) {
          this.settings = { ...this.settings, ...JSON.parse(savedSettings) }
        }
        
        if (savedTools) {
          this.enabledTools = JSON.parse(savedTools)
        }
        
        if (savedUser) {
          this.currentUser = { ...this.currentUser, ...JSON.parse(savedUser) }
        }
      } catch (error) {
        console.warn('加载用户设置失败:', error)
      }
    },
    
    /**
     * @description 检查后端连接
     */
    async checkBackendConnection() {
      try {
        // 添加超时控制
        const controller = new AbortController()
        const timeoutId = setTimeout(() => controller.abort(), 5000) // 5秒超时
        
        const response = await fetch(`/api/health`, {
          signal: controller.signal,
          method: 'GET',
          headers: {
            'Content-Type': 'application/json'
          }
        })
        
        clearTimeout(timeoutId)
        
        if (!response.ok) {
          throw new Error(`后端服务返回错误状态: ${response.status}`)
        }
        
        const data = await response.json()
        console.log('✅ 后端服务连接成功:', data)
        return data
        
      } catch (error) {
        if (error.name === 'AbortError') {
          console.warn('⏰ 后端连接超时')
          throw new Error('后端连接超时')
        } else if (error instanceof TypeError) {
          console.warn('🔌 后端服务未启动或网络不可达')
          throw new Error('后端服务不可用')
        } else {
          console.warn('❌ 后端连接失败:', error.message)
          throw error
        }
      }
    },
    
    /**
     * @description 应用主题
     */
    applyTheme() {
      const root = document.documentElement
      
      if (this.settings.theme === 'dark') {
        root.classList.add('dark-theme')
        root.classList.remove('light-theme')
      } else {
        root.classList.add('light-theme')
        root.classList.remove('dark-theme')
      }
    },
    
    /**
     * @description 切换工具状态
     * @param {string} toolName - 工具名称
     */
    toggleTool(toolName) {
      const index = this.enabledTools.indexOf(toolName)
      
      if (index > -1) {
        this.enabledTools.splice(index, 1)
      } else {
        this.enabledTools.push(toolName)
      }
      
      // 保存到本地存储
      localStorage.setItem('hanbon_enabled_tools', JSON.stringify(this.enabledTools))
    },
    
    /**
     * @description 更新设置
     * @param {Object} newSettings - 新设置
     */
    updateSettings(newSettings) {
      this.settings = { ...this.settings, ...newSettings }
      
      // 应用主题变更
      if (newSettings.theme) {
        this.applyTheme()
      }
      
      // 保存设置
      localStorage.setItem('hanbon_settings', JSON.stringify(this.settings))
    },
    
    /**
     * @description 处理工具使用事件
     * @param {Array} usedTools - 使用的工具列表
     */
    handleToolsUsed(usedTools) {
      console.log('本次对话使用的工具:', usedTools)
      
      // 可以在这里添加工具使用统计等逻辑
    },
    
    /**
     * @description 开始新对话
     */
    startNewChat() {
      console.log('🚀 App: 接收到新建对话事件')
      // 触发聊天界面重置
      this.$refs.chatInterface?.resetChat?.()
      // 重置消息状态
      this.hasMessages = false
      console.log('✅ App: 新对话已创建')
    },
    
    /**
     * @description 加载聊天历史
     * @param {Object} chatData - 聊天数据
     */
    loadChatHistory(chatData) {
      console.log('📚 App: 接收到加载聊天历史事件', chatData)
      // 加载指定的聊天历史
      this.$refs.chatInterface?.loadChat?.(chatData)
      this.showChatHistory = false
      console.log('✅ App: 聊天历史面板已关闭')
    },
    
    /**
     * @description 切换记忆功能
     * @param {boolean} enabled - 是否启用记忆
     */
    handleToggleMemory(enabled) {
      this.updateSettings({ enableMemory: enabled })
      
      if (enabled) {
        console.log('记忆功能已启用')
      } else {
        console.log('记忆功能已禁用')
      }
    },
    
    /**
     * @description 处理记忆更新事件
     */
    handleMemoryUpdated() {
      console.log('用户记忆已更新')
      // 可以在这里添加记忆更新后的处理逻辑
      // 比如刷新相关UI组件等
    },
    
    /**
     * @description 处理消息状态变化
     */
    handleMessagesChanged() {
      // 使用$nextTick确保DOM更新后再检查消息数量
      this.$nextTick(() => {
        const chatInterface = this.$refs.chatInterface
        if (chatInterface && chatInterface.messages) {
          this.hasMessages = chatInterface.messages.length > 0
        }
      })
    },
    
    /**
     * @description 显示聊天历史
     */
    showHistory() {
      console.log('📚 App: 接收到显示聊天历史事件')
      console.log('📚 App: 当前showChatHistory状态:', this.showChatHistory)
      this.showChatHistory = true
      console.log('📚 App: 更新后showChatHistory状态:', this.showChatHistory)
      console.log('✅ App: 聊天历史面板应该已显示')
    },
    
    /**
     * @description 显示设置面板
     */
    showSettingsPanel() {
      console.log('⚙️ App: 接收到显示设置面板事件')
      console.log('⚙️ App: 当前showSettings状态:', this.showSettings)
      this.showSettings = true
      console.log('⚙️ App: 更新后showSettings状态:', this.showSettings)
      console.log('✅ App: 设置面板应该已显示')
    },
    
    /**
     * @description 显示记忆管理面板
     */
    showMemoryManagement() {
      console.log('🧠 App: 接收到显示记忆管理事件')
      console.log('🧠 App: 当前showMemoryPanel状态:', this.showMemoryPanel)
      this.showMemoryPanel = true
      console.log('🧠 App: 更新后showMemoryPanel状态:', this.showMemoryPanel)
      console.log('✅ App: 记忆管理面板应该已显示')
      
      // 强制触发重新渲染
      this.$nextTick(() => {
        console.log('🔄 App: 下一帧渲染完成，面板状态:', this.showMemoryPanel)
      })
    },
    
    /**
     * @description 切换测试模式
     */
    toggleTestMode() {
      this.showTestMode = !this.showTestMode
    },
    
    /**
     * @description 处理全局错误
     */
    handleGlobalError(event) {
      console.error('全局错误:', event.error)
      // 可以在这里添加全局错误处理逻辑
    },
    
    /**
     * @description 处理未处理的拒绝
     */
    handleUnhandledRejection(event) {
      console.error('未处理的拒绝:', event.reason)
      // 可以在这里添加未处理的拒绝处理逻辑
    }
  }
}
</script>

<style>
/* 全局样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Icons", 
               "Helvetica Neue", Helvetica, Arial, sans-serif;
  margin: 0;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  overflow-x: hidden;
}

#app {
  position: relative;
  min-height: 100vh;
  /* 更现代的动态渐变背景 */
  background: linear-gradient(-45deg, #667eea, #764ba2, #6C63FF, #86A8E7, #91EAE4);
  background-size: 400% 400%;
  animation: gradientShift 15s ease infinite;
}

@keyframes gradientShift {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

.main-container {
  position: relative;
  z-index: 10;
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  backdrop-filter: blur(1px);
}

/* 主题样式 */
.light-theme {
  --primary-color: #6C63FF;
  --secondary-color: #86A8E7;
  --background-color: #F7F9FB;
  --surface-color: #FFFFFF;
  --text-primary: #232946;
  --text-secondary: #6C63FF;
  --border-color: #E3E8F0;
  --shadow-color: rgba(134, 168, 231, 0.10);
  --success-color: #20c997;
  --warning-color: #fd7e14;
  --error-color: #e74c3c;
  --info-color: #6C63FF;
}

.dark-theme {
  --primary-color: #6C63FF;
  --secondary-color: #232946;
  --background-color: #181A20;
  --surface-color: #232946;
  --text-primary: #F7F9FB;
  --text-secondary: #A0A8C3;
  --border-color: #232946;
  --shadow-color: rgba(108, 99, 255, 0.15);
  --success-color: #20c997;
  --warning-color: #fd7e14;
  --error-color: #e74c3c;
  --info-color: #6C63FF;
}

/* 响应式布局 */
@media (max-width: 768px) {
  .main-container {
    padding: 0 10px;
  }
}

@media (max-width: 480px) {
  body {
    font-size: 14px;
  }
}

/* 滚动条美化 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: var(--surface-color);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--text-secondary);
}

/* 动画效果 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.slide-enter-active, .slide-leave-active {
  transition: transform 0.3s ease;
}

.slide-enter-from {
  transform: translateX(100%);
}

.slide-leave-to {
  transform: translateX(-100%);
}

/* 工具提示 */
.tooltip {
  position: relative;
  cursor: help;
}

.tooltip:hover::after {
  content: attr(data-tooltip);
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
}

/* 测试模式切换样式 */
.test-mode-toggle {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
  display: flex;
  background: var(--surface-color);
  border-radius: 8px;
  box-shadow: 0 4px 12px var(--shadow-color);
  overflow: hidden;
  border: 1px solid var(--border-color);
}

.test-mode-toggle button {
  padding: 8px 16px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  border-right: 1px solid var(--border-color);
}

.test-mode-toggle button:last-child {
  border-right: none;
}

.test-mode-toggle button:hover {
  background: var(--background-color);
}

.test-mode-toggle button.active {
  background: var(--primary-color);
  color: white;
}

/* 开发者测试按钮样式 */
.dev-test-button {
  position: fixed;
  top: 80px;
  right: 20px;
  z-index: 999;
}

.dev-test-button .test-btn {
  padding: 8px 16px;
  background: #ff4757;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(255, 71, 87, 0.3);
}

.dev-test-button .test-btn:hover {
  background: #ff3838;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255, 71, 87, 0.4);
}

/* 调试状态面板样式 */
.debug-panel {
  position: fixed;
  top: 120px;
  right: 20px;
  z-index: 999;
  background: var(--surface-color);
  border-radius: 8px;
  box-shadow: 0 4px 12px var(--shadow-color);
  padding: 16px;
  border: 1px solid var(--border-color);
}

.debug-panel h4 {
  margin-bottom: 16px;
  font-size: 18px;
  font-weight: 600;
}

.debug-item {
  margin-bottom: 8px;
}

.debug-item span {
  font-weight: 500;
}

.debug-item span.active {
  color: var(--primary-color);
  font-weight: 600;
}

.toggle-btn {
  margin-left: 8px;
  padding: 4px 8px;
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.toggle-btn:hover {
  background: var(--border-color);
}

/* 加载动画 */
.loading-spinner {
  border: 2px solid var(--border-color);
  border-top: 2px solid var(--primary-color);
  border-radius: 50%;
  width: 20px;
  height: 20px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 按钮通用样式 */
.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-primary {
  background: linear-gradient(90deg, var(--primary-color) 60%, var(--secondary-color) 100%);
  color: #fff;
  box-shadow: 0 2px 12px var(--shadow-color);
  border: none;
}

.btn-primary:hover {
  background: linear-gradient(90deg, #5A55CA 60%, #86A8E7 100%);
  box-shadow: 0 4px 20px var(--shadow-color);
}

.btn-secondary {
  background: var(--surface-color);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.btn-secondary:hover {
  background: var(--border-color);
}

/* 卡片样式 */
.card {
  background: var(--surface-color);
  border-radius: 18px;
  padding: 24px;
  box-shadow: 0 4px 24px var(--shadow-color);
  border: 1px solid var(--border-color);
  transition: box-shadow 0.2s, transform 0.2s;
}

.card:hover {
  transform: translateY(-4px) scale(1.02);
  box-shadow: 0 8px 32px var(--shadow-color);
}
</style>

<template>
  <div class="chat-interface">
    <!-- 科技感背景 -->
    <div class="tech-background">
      <div class="gradient-orb orb-1"></div>
      <div class="gradient-orb orb-2"></div>
      <div class="gradient-orb orb-3"></div>
      <div class="tech-grid"></div>
    </div>
    
    <!-- 欢迎界面 -->
    <div v-if="!hasMessages" class="welcome-screen">
      <div class="welcome-content">
        <!-- Logo和标题区域 -->
        <div class="hero-section">
          <div class="logo-container">
            <img src="@/assets/hanbon_logo.png" alt="食慧美食AI" class="logo">
          </div>
          <h1 class="main-title">
            <span class="title-gradient">食慧美食AI</span>
          </h1>
          <p class="subtitle">
            <span class="subtitle-text">您的专属美食智能顾问</span>
            <span class="food-emoji">🍴</span>
          </p>
        </div>
        
        <!-- 功能卡片网格 -->
        <div class="features-grid">
          <div 
            v-for="(item, index) in quickStartItems"
            :key="item.id"
            class="feature-card"
            :style="{ animationDelay: `${index * 0.1}s` }"
            @click="handleQuickStart(item.message)"
          >
            <div class="card-background"></div>
            <div class="card-content">
              <div class="card-icon-wrapper">
                <span class="card-icon">{{ item.icon }}</span>
              </div>
              <div class="card-text">
                <h3 class="card-title">{{ item.label }}</h3>
                <p class="card-description">{{ getCardDescription(item.id) }}</p>
              </div>
            </div>
            <div class="card-hover-effect"></div>
          </div>
        </div>
        
        <!-- 智能控制面板已移到输入框内 -->

        <!-- 输入区域 -->
        <div class="input-section">
          <!-- 推荐例子气泡 -->
          <!-- <div class="example-bubbles" v-if="!inputMessage.trim()">
            <div class="bubbles-label">💡 试试这些：</div>
            <div class="bubbles-container">
              <div 
                v-for="example in quickExamples"
                :key="example.id"
                class="example-bubble"
                @click="handleExampleClick(example.text)"
              >
                <span class="bubble-icon">{{ example.icon }}</span>
                <span class="bubble-text">{{ example.text }}</span>
              </div>
            </div>
          </div> -->
          
          <!-- 集成输入卡片 -->
          <div class="integrated-input-card">
            <!-- AI模型选择器 -->
            <div class="input-model-section">
              <div class="model-header">
                <span class="model-icon">🤖</span>
                <span class="model-label">AI 大脑</span>
              </div>
              <div class="model-selector-wrapper">
                <select 
                  v-model="selectedModel" 
                  class="integrated-model-selector"
                  :disabled="isLoading"
                >
                  <option 
                    v-for="model in availableModels" 
                    :key="model.id" 
                    :value="model.id"
                  >
                    {{ model.name }} - {{ model.description }}
                  </option>
                </select>
                <div class="selector-chevron">
                  <svg viewBox="0 0 24 24" width="16" height="16">
                    <path fill="currentColor" d="M7 10l5 5 5-5z"/>
                  </svg>
                </div>
              </div>
            </div>

            <!-- 智能工具状态 -->
            <div v-if="enabledTools.length" class="input-tools-section">
              <div class="tools-header">
                <span class="tools-icon">🛠️</span>
                <span class="tools-label">智能工具</span>
                <span class="tools-count">{{ enabledTools.length }}</span>
              </div>
              <div class="input-tools-grid">
                <div 
                  v-for="tool in enabledTools.slice(0, 6)"
                  :key="tool"
                  class="input-tool-chip"
                >
                  {{ getToolName(tool) }}
                </div>
                <div v-if="enabledTools.length > 6" class="input-tool-chip more-tools-chip">
                  +{{ enabledTools.length - 6 }}
                </div>
              </div>
            </div>
            
            <!-- 输入框区域 -->
            <div class="input-wrapper">
              <textarea 
                ref="welcomeMessageInput"
                v-model="inputMessage"
                placeholder="✨ 与AI开始对话，探索美食的无限可能..."
                class="main-input"
                @keydown="handleKeydown"
                @input="adjustHeight"
                :disabled="isLoading"
              ></textarea>
              
              <button 
                class="send-button"
                @click="sendMessage"
                :disabled="!canSend"
              >
                <span v-if="!isLoading" class="send-content">
                  <span class="send-text">发送</span>
                  <span class="send-icon">→</span>
                </span>
                <div v-else class="loading-spinner">
                  <div class="spinner"></div>
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 对话消息区域 -->
    <div v-else class="messages-container" ref="messagesContainer">
      <div class="messages-list">
        <div
          v-for="(message, index) in messages"
          :key="message.id"
          class="message-wrapper"
          :class="message.type"
        >
          <!-- 在最后一条AI消息之前显示思维链 -->
          <ThinkingChain 
            v-if="message.type === 'assistant' && index === messages.length - 1 && currentThinkingSteps.length > 0" 
            ref="thinkingChain"
            :steps="currentThinkingSteps"
            class="message-thinking-chain"
          />
          
          <div class="message-bubble" :class="{ error: message.isError }">
            <div class="message-content" v-html="formatMessage(message.content)"></div>
            
            <!-- 工具结果展示 -->
            <div v-if="message.toolResults && message.toolResults.length" class="tool-results-container">
              <ToolResultDisplay 
                v-for="(result, index) in message.toolResults"
                :key="`${message.id}-tool-${index}`"
                :data="result"
                @requestRecipe="handleRecipeRequest"
                @requestImages="handleImageRequest"
                @retryTool="handleToolRetry"
              />
            </div>
            
            <div class="message-meta">
              <span class="timestamp">{{ formatTime(message.timestamp) }}</span>
              <div v-if="message.toolsUsed && message.toolsUsed.length" class="tools-used">
                <span v-for="tool in message.toolsUsed" :key="tool" class="tool-tag">
                  {{ getToolName(tool) }}
                </span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- AI思考中提示（只在没有思维链时显示） -->
        <div v-if="isLoading && currentThinkingSteps.length === 0" class="thinking-indicator">
          <div class="thinking-animation">
            <div class="thinking-dots">
              <div class="dot"></div>
              <div class="dot"></div>
              <div class="dot"></div>
            </div>
            <span class="thinking-text">AI正在思考中...</span>
          </div>
        </div>
      </div>
      
              <!-- 对话界面的输入区域 -->
        <div class="chat-input-container">
        <!-- 推荐例子气泡（对话界面） -->
        <!-- <div class="chat-example-bubbles" v-if="!inputMessage.trim() && !isLoading">
          <div class="chat-bubbles-container">
            <div 
              v-for="example in chatQuickExamples"
              :key="example.id"
              class="chat-example-bubble"
              @click="handleExampleClick(example.text)"
            >
              <span class="chat-bubble-icon">{{ example.icon }}</span>
              <span class="chat-bubble-text">{{ example.text }}</span>
            </div>
          </div>
        </div> -->
        
        <!-- 集成输入框 -->
        <div class="chat-integrated-input-card">
          <!-- AI大脑和智能工具水平排列 -->
          <div class="chat-controls-row">
            <!-- AI模型选择器 -->
            <div class="chat-model-section">
              <div class="chat-model-header">
                <span class="chat-model-icon">🤖</span>
                <span class="chat-model-label">AI 大脑</span>
              </div>
              <div class="chat-model-wrapper">
                <select 
                  v-model="selectedModel" 
                  class="chat-model-selector"
                  :disabled="isLoading"
                >
                  <option 
                    v-for="model in availableModels" 
                    :key="model.id" 
                    :value="model.id"
                  >
                    {{ model.name }}
                  </option>
                </select>
                <div class="chat-selector-chevron">
                  <svg viewBox="0 0 24 24" width="14" height="14">
                    <path fill="currentColor" d="M7 10l5 5 5-5z"/>
                  </svg>
                </div>
              </div>
            </div>

            <!-- 智能工具状态 -->
            <div v-if="enabledTools.length" class="chat-tools-section">
              <div class="chat-tools-header">
                <span class="chat-tools-icon">🛠️</span>
                <span class="chat-tools-label">智能工具</span>
                <span class="chat-tools-count">{{ enabledTools.length }}</span>
              </div>
              <div class="chat-tools-chips">
                <div 
                  v-for="tool in enabledTools.slice(0, 3)"
                  :key="tool"
                  class="chat-tool-chip"
                >
                  {{ getToolName(tool) }}
                </div>
                <div v-if="enabledTools.length > 3" class="chat-more-chip">
                  +{{ enabledTools.length - 3 }}
                </div>
              </div>
            </div>
          </div>
          
          <!-- 输入框区域 -->
          <div class="chat-input-wrapper">
            <div class="input-field-container">
              <textarea
                ref="messageInput"
                v-model="inputMessage"
                placeholder="继续对话... (Shift+Enter换行，Enter发送)"
                class="chat-input"
                @keydown="handleKeydown"
                @input="adjustHeight"
                @focus="handleInputFocus"
                @blur="handleInputBlur"
                :disabled="isLoading"
                rows="1"
              ></textarea>
              
              <!-- 字数统计 -->
              <div v-if="inputMessage.length > 0" class="char-count">
                {{ inputMessage.length }}
              </div>
            </div>
            
            <button 
              class="chat-send-btn"
              @click="sendMessage"
              :disabled="!canSend"
              :class="{ 'has-content': inputMessage.trim().length > 0 }"
            >
              <span v-if="!isLoading" class="send-icon">
                <svg viewBox="0 0 24 24" width="18" height="18">
                  <path fill="currentColor" d="M2,21L23,12L2,3V10L17,12L2,14V21Z"/>
                </svg>
              </span>
              <div v-else class="mini-spinner"></div>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ToolResultDisplay from './ToolResultDisplay.vue'
import ThinkingChain from './ThinkingChain.vue'
import { marked } from 'marked'

// 配置 marked 选项
marked.setOptions({
  breaks: true, // 支持换行符转为 <br>
  gfm: true, // 启用 GitHub 风格的 Markdown
  sanitize: false, // 不进行 HTML 清理（我们会手动处理）
  smartLists: true, // 智能列表
  smartypants: true // 智能标点符号
})

export default {
  name: 'ChatInterface',
  components: {
    ToolResultDisplay,
    ThinkingChain
  },
  props: {
    enabledTools: {
      type: Array,
      default: () => []
    }
  },
  emits: ['toolsUsed', 'messagesChanged'],
  data() {
    return {
      messages: [],
      inputMessage: '',
      isLoading: false,
      sessionId: '',
      
      // AI模型相关
      availableModels: [],
      selectedModel: '',
      defaultModel: '',
      
      // 打字机效果相关
      typewriterBuffer: '', // 缓冲区存储接收到的内容
      typewriterRunning: false, // 是否正在执行打字机效果
      currentTypingMessage: null, // 当前正在打字的消息
      
      // 思维链相关
      currentThinkingSteps: [], // 当前正在处理的思维链步骤
      
      quickStartItems: [
        { id: 1, label: '推荐美食', icon: '🍽️', message: '请推荐一些适合现在的美食' },
        { id: 2, label: '查看菜谱', icon: '📚', message: '我想学做一道家常菜' },
        { id: 3, label: '附近餐厅', icon: '📍', message: '帮我找找附近有什么好吃的餐厅' },
        { id: 4, label: '营养分析', icon: '🥗', message: '能帮我分析一下食物的营养成分吗？' }
      ],
      
      // 欢迎界面推荐例子
      quickExamples: [
        { id: 1, icon: '🍜', text: '推荐川菜' },
        { id: 2, icon: '📍', text: '附近餐厅' },
        { id: 3, icon: '🥘', text: '学做菜谱' },
        { id: 4, icon: '🍰', text: '甜点制作' },
        { id: 5, icon: '🥗', text: '营养分析' },
        { id: 6, icon: '🌶️', text: '辣味推荐' }
      ],
      
      // 对话界面推荐例子（更简洁）
      chatQuickExamples: [
        { id: 1, icon: '🍳', text: '换个菜谱' },
        { id: 2, icon: '📍', text: '查看位置' },
        { id: 3, icon: '🔍', text: '搜索图片' },
        { id: 4, icon: '💡', text: '更多建议' }
      ],
      
      toolsMap: {
        'amap_search': '地图搜索',
        'food_recommendation': '美食推荐',
        'weather_api': '天气助手',
        'image_search': '图片搜索',
        'bing_search': '网络搜索',
        'recipe_generator': '菜谱生成'
      }
    }
  },
  computed: {
    hasMessages() {
      return this.messages.length > 0
    },
    canSend() {
      return this.inputMessage.trim() && !this.isLoading
    }
  },
  async mounted() {
    this.sessionId = this.generateSessionId()
    await this.loadAvailableModels()
    this.initImageViewer()
  },
  methods: {
    async loadAvailableModels() {
      try {
        const response = await fetch('http://localhost:8000/models/available')
        if (response.ok) {
          const data = await response.json()
          this.availableModels = data.models || []
          this.defaultModel = data.default_model || ''
          this.selectedModel = this.defaultModel
          console.log('可用模型列表:', this.availableModels)
        } else {
          console.error('获取模型列表失败:', response.status)
          // 设置默认模型作为回退
          this.availableModels = [
            { id: 'deepseek', name: 'DeepSeek', description: '专业的中文对话模型' }
          ]
          this.selectedModel = 'deepseek'
        }
      } catch (error) {
        console.error('加载模型列表失败:', error)
        // 设置默认模型作为回退
        this.availableModels = [
          { id: 'deepseek', name: 'DeepSeek', description: '专业的中文对话模型' }
        ]
        this.selectedModel = 'deepseek'
      }
    },

    generateSessionId() {
      return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    },
    
    handleQuickStart(message) {
      this.inputMessage = message
      this.sendMessage()
    },
    
    /**
     * @description 处理推荐例子点击
     * @param {string} exampleText - 例子文本
     */
    handleExampleClick(exampleText) {
      this.inputMessage = exampleText
      // 自动调整输入框高度
      this.$nextTick(() => {
        this.adjustHeight()
      })
    },
    
    handleKeydown(event) {
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault()
        this.sendMessage()
      }
    },
    
    adjustHeight() {
      // 在欢迎界面时使用welcomeMessageInput，在对话界面时使用messageInput
      const textarea = this.hasMessages 
        ? this.$refs.messageInput 
        : this.$refs.welcomeMessageInput
        
      if (textarea) {
        textarea.style.height = 'auto'
        const newHeight = Math.min(textarea.scrollHeight, 120)
        textarea.style.height = `${newHeight}px`
        
        // 如果内容超过最大高度，显示滚动条
        if (textarea.scrollHeight > 120) {
          textarea.style.overflowY = 'auto'
        } else {
          textarea.style.overflowY = 'hidden'
        }
      }
    },

    /**
     * @description 处理输入框获得焦点
     */
    handleInputFocus() {
      // 输入框获得焦点时的处理
      this.$nextTick(() => {
        this.scrollToBottom()
      })
    },

    /**
     * @description 处理输入框失去焦点
     */
    handleInputBlur() {
      // 输入框失去焦点时的处理
      // 可以在这里添加保存草稿等功能
    },
    
    async sendMessage() {
      if (!this.canSend) return
      
      const messageText = this.inputMessage.trim()
      this.inputMessage = ''
      this.adjustHeight()
      
      // 添加用户消息
      const userMessage = {
        id: this.generateMessageId(),
        type: 'user',
        content: messageText,
        timestamp: new Date().toISOString()
      }
      
      this.messages.push(userMessage)
      this.scrollToBottom()
      
      // 通知父组件消息状态变化
      this.$emit('messagesChanged')
      
      // 获取AI响应
      await this.getAIResponse(messageText)
    },
    
    async getAIResponse(message) {
      this.isLoading = true
      
      // 添加AI消息占位符
      const aiMessage = {
        id: this.generateMessageId(),
        type: 'assistant',
        content: '',
        timestamp: new Date().toISOString(),
        toolsUsed: []
      }
      
      this.messages.push(aiMessage)
      this.scrollToBottom()
      
      try {
        const response = await fetch(`http://localhost:8000/chat/stream`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            message: message,
            session_id: this.sessionId,
            tools_enabled: this.enabledTools,
            model: this.selectedModel
          })
        })
        
        if (!response.ok) {
          throw new Error('网络请求失败')
        }
        
        await this.processStreamResponse(response, aiMessage)
        
      } catch (error) {
        console.error('AI响应失败:', error)
        aiMessage.content = '抱歉，AI服务暂时不可用，请稍后再试。'
        aiMessage.isError = true
        // 立即重置loading状态
        this.isLoading = false
      } finally {
        // 确保状态被重置（双重保险）
        this.isLoading = false
        // 重置打字机状态
        this.typewriterBuffer = ''
        this.typewriterRunning = false
        this.currentTypingMessage = null
      }
    },
    
    async processStreamResponse(response, aiMessage) {
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      
      try {
        // eslint-disable-next-line no-constant-condition
        while (true) {
          const { done, value } = await reader.read()
          if (done) break
          
          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split('\n')
          
          // 保留最后一行（可能不完整）
          buffer = lines.pop() || ''
          
          for (const line of lines) {
            const trimmedLine = line.trim()
            if (trimmedLine.startsWith('data: ')) {
              try {
                const jsonStr = trimmedLine.slice(6).trim()
                if (jsonStr && jsonStr !== '[DONE]') {
                  const data = JSON.parse(jsonStr)
                  
                  // 处理各种类型的流式数据
                  if (data.type === 'start') {
                    console.log('开始处理:', data.content)
                    // 重置思维链步骤
                    this.currentThinkingSteps = []
                  } else if (data.type === 'thinking_step') {
                    // 处理思维链步骤
                    this.handleThinkingStep(data)
                    // 如果是第四步完成，记录完成状态
                    if (data.step === 4 && data.status === 'completed') {
                      console.log('思维链第四步已完成')
                    }
                  } else if (data.type === 'plan') {
                    console.log('计划阶段:', data.content)
                  } else if (data.type === 'action') {
                    console.log('执行工具:', data.content)
                  } else if (data.type === 'generating') {
                    console.log('生成回复:', data.content)
                  } else if (data.type === 'response_chunk') {
                     // 这是真正的回复内容，添加到缓冲区
                     this.addToTypewriterBuffer(aiMessage, data.content || '')
                   } else if (data.type === 'content' || data.type === 'chunk') {
                     // 兼容其他格式，添加到缓冲区
                     this.addToTypewriterBuffer(aiMessage, data.content || '')
                                                       } else if (data.type === 'complete') {
                    // 处理完成信号
                    if (data.content && data.content.tools_used) {
                      aiMessage.toolsUsed = data.content.tools_used
                      this.$emit('toolsUsed', aiMessage.toolsUsed)
                    }
                    console.log('回复完成')
                    // 立即关闭loading状态
                    this.isLoading = false
                    // 等待打字机效果完成
                    await this.waitForTypewriterComplete()
                    // 完成后触发思维链自动收起（延迟执行，确保思维链组件已经渲染）
                    this.$nextTick(() => {
                      this.triggerThinkingChainAutoCollapse()
                    })
                    break
                  } else if (data.type === 'action_result') {
                    // 处理工具执行结果
                    if (data.content) {
                      if (!aiMessage.toolResults) {
                        aiMessage.toolResults = []
                      }
                      // 将工具结果添加到消息中
                      if (Array.isArray(data.content)) {
                        aiMessage.toolResults.push(...data.content)
                      } else {
                        aiMessage.toolResults.push(data.content)
                      }
                    }
                  } else if (data.type === 'error') {
                    aiMessage.content += `\n[错误: ${data.content}]`
                    aiMessage.isError = true
                    this.scrollToBottom()
                  }
                }
              } catch (e) {
                console.warn('解析流数据失败:', trimmedLine, e)
              }
            }
          }
        }
      } finally {
        reader.releaseLock()
        // 确保loading状态被重置
        this.isLoading = false
      }
    },
    
    /**
     * @description 添加内容到打字机缓冲区
     * @param {Object} message - 消息对象
     * @param {string} content - 要添加的内容
     */
    addToTypewriterBuffer(message, content) {
      if (!content) return
      
      // 将内容添加到缓冲区
      this.typewriterBuffer += content
      
      // 如果打字机没有运行，启动它
      if (!this.typewriterRunning && message) {
        this.currentTypingMessage = message
        this.startTypewriter()
      }
    },
    
    /**
     * @description 启动打字机效果
     */
    async startTypewriter() {
      if (this.typewriterRunning) return
      
      this.typewriterRunning = true
      
      while (this.typewriterBuffer.length > 0 || (this.isLoading && this.currentTypingMessage)) {
        if (this.typewriterBuffer.length > 0 && this.currentTypingMessage) {
          // 取出一个字符
          const char = this.typewriterBuffer.charAt(0)
          this.typewriterBuffer = this.typewriterBuffer.slice(1)
          
          // 显示字符
          this.currentTypingMessage.content += char
          this.scrollToBottom()
          
          // 控制打字速度
          await this.delay(20) // 20ms 比较快的打字速度
        } else if (this.isLoading) {
          // 只有在加载中且有当前消息时才等待
          await this.delay(50)
        } else {
          // 既没有内容也不在加载中，退出循环
          break
        }
      }
      
      this.typewriterRunning = false
      this.currentTypingMessage = null
    },
    
    /**
     * @description 等待打字机效果完成
     */
    async waitForTypewriterComplete() {
      while (this.typewriterRunning || this.typewriterBuffer.length > 0) {
        await this.delay(100)
      }
    },
    
    /**
     * @description 延迟函数
     * @param {number} ms - 延迟毫秒数
     */
    delay(ms) {
      return new Promise(resolve => setTimeout(resolve, ms))
    },
    
    generateMessageId() {
      return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    },
    
    scrollToBottom() {
      this.$nextTick(() => {
        const container = this.$refs.messagesContainer
        if (container) {
          container.scrollTop = container.scrollHeight
        }
      })
    },
    
    formatMessage(content) {
      // 首先尝试解析JSON格式的工具结果
      try {
        // 检查是否包含工具结果的标识
        if (content.includes('【图片展示】') || content.includes('图片展示：')) {
          return this.formatImageResults(content)
        }
        
        if (content.includes('📍') || content.includes('地址：') || content.includes('位置：')) {
          return this.formatLocationResults(content)
        }
        
        if (content.includes('🍽️') || content.includes('菜谱：') || content.includes('制作步骤：')) {
          return this.formatRecipeResults(content)
        }
      } catch (e) {
        console.log('工具结果解析失败，使用默认格式化:', e)
      }
      
      // 使用 marked 库进行完整的 Markdown 渲染
      let formatted = ''
      try {
        formatted = marked(content)
      } catch (e) {
        console.warn('Markdown 渲染失败，使用基础格式化:', e)
        // 回退到基础处理
        formatted = content
          .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
          .replace(/\*(.*?)\*/g, '<em>$1</em>')
          .replace(/\n/g, '<br>')
      }
      
      // 处理图片URL (http开头的图片链接)
      formatted = this.processImageUrls(formatted)
      
      // 处理地图链接
      formatted = this.processMapLinks(formatted)
      
      return formatted
    },
    
    /**
     * 格式化图片搜索结果
     */
    formatImageResults(content) {
      // 提取图片URL的正则表达式
      const imageUrlRegex = /(https?:\/\/[^\s]+\.(?:jpg|jpeg|png|gif|webp|bmp)(?:\?[^\s]*)?)/gi
      const urls = content.match(imageUrlRegex) || []
      
      if (urls.length === 0) {
        return this.processImageUrls(content)
      }
      
      // 构建图片画廊HTML
      let galleryHtml = `
        <div class="tool-result-container image-gallery">
          <div class="tool-result-header">
            <span class="tool-icon">📷</span>
            <span class="tool-title">图片搜索结果</span>
          </div>
          <div class="image-grid">
      `
      
             urls.forEach((url, index) => {
         if (index < 6) { // 最多显示6张图片
           galleryHtml += `
             <div class="image-item">
               <img src="${url}" alt="美食图片 ${index + 1}" 
                    onclick="window.showImageModal(event, '${url}')"
                    onerror="this.style.display='none'"
                    loading="lazy" />
             </div>
           `
         }
       })
      
      galleryHtml += `
          </div>
          ${urls.length > 6 ? `<div class="image-count">还有 ${urls.length - 6} 张图片...</div>` : ''}
        </div>
      `
      
      // 移除原始URL，保留其他文本内容
      let cleanContent = content
      urls.forEach(url => {
        cleanContent = cleanContent.replace(url, '')
      })
      
      // 使用 marked 库渲染剩余的文本内容
      try {
        cleanContent = marked(cleanContent.replace(/\s+/g, ' ').trim())
      } catch (e) {
        cleanContent = cleanContent
          .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
          .replace(/\*(.*?)\*/g, '<em>$1</em>')
          .replace(/\n/g, '<br>')
          .replace(/\s+/g, ' ')
          .trim()
      }
      
      return cleanContent + galleryHtml
    },
    
    /**
     * 格式化地理位置结果
     */
    formatLocationResults(content) {
      // 提取地址和位置信息的正则表达式
      const addressRegex = /地址[：:]\s*([^\n\r]+)/g
      const coordRegex = /location[：:]\s*([0-9.]+),([0-9.]+)/g
      
      let locationHtml = ''
      let match
      
      // 提取地址信息
      const addresses = []
      while ((match = addressRegex.exec(content)) !== null) {
        addresses.push(match[1].trim())
      }
      
      // 提取坐标信息
      const coordinates = []
      while ((match = coordRegex.exec(content)) !== null) {
        coordinates.push({
          lng: parseFloat(match[1]),
          lat: parseFloat(match[2])
        })
      }
      
      if (addresses.length > 0 || coordinates.length > 0) {
        locationHtml = `
          <div class="tool-result-container location-result">
            <div class="tool-result-header">
              <span class="tool-icon">📍</span>
              <span class="tool-title">位置信息</span>
            </div>
            <div class="location-list">
        `
        
        addresses.forEach((address, index) => {
          const coord = coordinates[index]
          locationHtml += `
            <div class="location-item">
              <div class="location-address">${address}</div>
              ${coord ? `
                <div class="location-actions">
                  <a href="https://uri.amap.com/marker?position=${coord.lng},${coord.lat}&name=${encodeURIComponent(address)}" 
                     target="_blank" class="map-link">
                    🗺️ 在地图中查看
                  </a>
                </div>
              ` : ''}
            </div>
          `
        })
        
        locationHtml += `
            </div>
          </div>
        `
      }
      
      // 清理内容
      let cleanContent = content
        .replace(addressRegex, '')
        .replace(coordRegex, '')
        .replace(/\s+/g, ' ')
        .trim()
      
      // 使用 marked 库渲染剩余的文本内容
      try {
        cleanContent = marked(cleanContent)
      } catch (e) {
        cleanContent = cleanContent
          .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
          .replace(/\*(.*?)\*/g, '<em>$1</em>')
          .replace(/\n/g, '<br>')
      }
      
      return cleanContent + locationHtml
    },
    
    /**
     * 格式化菜谱结果
     */
    formatRecipeResults(content) {
      // 提取制作步骤
      const stepsRegex = /(\d+)\.\s*([^\n\r]+)/g
      const ingredientsRegex = /【食材准备】([\s\S]*?)【|【食材.*?】([\s\S]*?)【/
      
      let recipeHtml = ''
      let match
      const steps = []
      
      // 提取步骤
      while ((match = stepsRegex.exec(content)) !== null) {
        steps.push({
          number: match[1],
          instruction: match[2].trim()
        })
      }
      
      // 提取食材
      const ingredientsMatch = content.match(ingredientsRegex)
      const ingredients = ingredientsMatch ? 
        (ingredientsMatch[1] || ingredientsMatch[2]).split(/[,，\n]/).filter(item => item.trim()) : []
      
      if (steps.length > 0 || ingredients.length > 0) {
        recipeHtml = `
          <div class="tool-result-container recipe-result">
            <div class="tool-result-header">
              <span class="tool-icon">👨‍🍳</span>
              <span class="tool-title">菜谱详情</span>
            </div>
        `
        
        if (ingredients.length > 0) {
          recipeHtml += `
            <div class="recipe-section">
              <h4 class="recipe-section-title">🥘 食材准备</h4>
              <div class="ingredients-list">
                ${ingredients.map(ingredient => `
                  <span class="ingredient-item">${ingredient.trim()}</span>
                `).join('')}
              </div>
            </div>
          `
        }
        
        if (steps.length > 0) {
          recipeHtml += `
            <div class="recipe-section">
              <h4 class="recipe-section-title">📝 制作步骤</h4>
              <div class="steps-list">
                ${steps.map(step => `
                  <div class="step-item">
                    <span class="step-number">${step.number}</span>
                    <span class="step-instruction">${step.instruction}</span>
                  </div>
                `).join('')}
              </div>
            </div>
          `
        }
        
        recipeHtml += `</div>`
      }
      
      // 清理内容
      let cleanContent = content
        .replace(stepsRegex, '')
        .replace(ingredientsRegex, '')
        .replace(/【[^】]*】/g, '')
        .replace(/\s+/g, ' ')
        .trim()
      
      // 使用 marked 库渲染剩余的文本内容
      try {
        cleanContent = marked(cleanContent)
      } catch (e) {
        cleanContent = cleanContent
          .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
          .replace(/\*(.*?)\*/g, '<em>$1</em>')
          .replace(/\n/g, '<br>')
      }
      
      return cleanContent + recipeHtml
    },
    
    /**
     * 处理图片URL
     */
    processImageUrls(content) {
      const imageUrlRegex = /(https?:\/\/[^\s<>"]+\.(?:jpg|jpeg|png|gif|webp|bmp)(?:\?[^\s<>"]*)?)/gi
      
      return content.replace(imageUrlRegex, (url) => {
        const imageId = `img_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
        return `
          <div class="inline-image" id="${imageId}_container">
            <img src="${url}" alt="图片" 
                 id="${imageId}"
                 onclick="window.showImageModal(event, '${url}')"
                 onload="this.parentElement.classList.add('loaded')"
                 onerror="this.parentElement.innerHTML='<div class=\\"image-error\\">❌ 图片加载失败</div>'"
                 loading="lazy" />
          </div>
        `
      })
    },
    
    /**
     * 初始化全局图片查看器
     */
    initImageViewer() {
      // 设置全局图片查看器方法
      window.showImageModal = (event, imageUrl) => {
        const fullUrl = imageUrl || event.target.src
        
        // 创建模态框
        const modal = document.createElement('div')
        modal.className = 'image-modal'
        modal.innerHTML = `
          <div class="image-modal-backdrop" onclick="this.parentElement.remove()">
            <div class="image-modal-content" onclick="event.stopPropagation()">
              <img src="${fullUrl}" alt="放大图片" />
              <button class="image-modal-close" onclick="this.closest('.image-modal').remove()">
                ✕
              </button>
            </div>
          </div>
        `
        
        document.body.appendChild(modal)
        
        // 添加键盘事件监听（ESC关闭）
        const handleKeydown = (e) => {
          if (e.key === 'Escape') {
            modal.remove()
            document.removeEventListener('keydown', handleKeydown)
          }
        }
        document.addEventListener('keydown', handleKeydown)
      }
    },
    
    /**
     * 处理地图链接
     */
    processMapLinks(content) {
      const mapUrlRegex = /(https?:\/\/(?:uri\.amap\.com|maps\.google\.com|map\.baidu\.com)[^\s<>"]+)/gi
      
      return content.replace(mapUrlRegex, (url) => {
        return `<a href="${url}" target="_blank" class="map-link">🗺️ 在地图中查看</a>`
      })
    },
    
    formatTime(timestamp) {
      const date = new Date(timestamp)
      return date.toLocaleTimeString('zh-CN', { 
        hour: '2-digit', 
        minute: '2-digit' 
      })
    },
    
    getToolName(tool) {
      return this.toolsMap[tool] || tool
    },
    
    getCardDescription(id) {
      const descriptions = {
        1: '获得个性化美食推荐',
        2: '学习详细制作步骤',
        3: '发现周边优质餐厅',
        4: '了解食物营养成分'
      }
      return descriptions[id] || ''
    },
    
    /**
     * @description 处理菜谱请求
     */
    handleRecipeRequest(dishName) {
      this.inputMessage = `请生成${dishName}的详细菜谱`
      this.sendMessage()
    },
    
    /**
     * @description 处理图片搜索请求  
     */
    handleImageRequest(dishName) {
      this.inputMessage = `给我看看${dishName}的图片`
      this.sendMessage()
    },
    
    /**
     * @description 处理工具重试
     */
    handleToolRetry(toolName) {
      console.log('重试工具:', toolName)
      // 可以重新执行上一次的消息
    },

    resetChat() {
      this.messages = []
      this.sessionId = this.generateSessionId()
      // 重置打字机状态
      this.typewriterBuffer = ''
      this.typewriterRunning = false
      this.currentTypingMessage = null
      // 通知父组件消息状态变化
      this.$emit('messagesChanged')
    },

    /**
     * @description 处理思维链步骤
     * @param {Object} data - 思维链步骤数据
     */
    handleThinkingStep(data) {
      const { step, title, content, status } = data
      
      // 查找是否已存在该步骤
      const existingStepIndex = this.currentThinkingSteps.findIndex(s => s.step === step)
      
      if (existingStepIndex !== -1) {
        // 更新现有步骤
        this.currentThinkingSteps[existingStepIndex] = {
          step,
          title,
          content,
          status,
          timestamp: new Date().toISOString()
        }
      } else {
        // 添加新步骤
        this.currentThinkingSteps.push({
          step,
          title,
          content,
          status,
          timestamp: new Date().toISOString()
        })
      }
      
      // 按步骤编号排序
      this.currentThinkingSteps.sort((a, b) => a.step - b.step)
      
      // 滚动到底部以显示最新的思维链步骤
      this.scrollToBottom()
    },
    
    /**
     * @description 清理思维链步骤（对话完成后调用）
     */
    clearThinkingSteps() {
      // 等待2秒后清理思维链步骤，让用户有时间查看
      setTimeout(() => {
        this.currentThinkingSteps = []
      }, 3000)
    },

    /**
     * @description 触发思维链自动收起
     */
    triggerThinkingChainAutoCollapse() {
      // 使用ref访问ThinkingChain组件
      const thinkingChainComponent = this.$refs.thinkingChain
      if (thinkingChainComponent && typeof thinkingChainComponent.autoCollapse === 'function') {
        console.log('🎯 手动触发思维链自动收起')
        thinkingChainComponent.autoCollapse()
      } else {
        console.log('⚠️ 未找到ThinkingChain组件或autoCollapse方法')
      }
    }
  }
}
</script>

<style scoped>
/* 全局placeholder样式覆盖 */
::v-deep input::placeholder,
::v-deep textarea::placeholder {
  color: #bbb !important;
  opacity: 1 !important;
}
/* CSS变量定义 */
.chat-interface {
  /* 定义组件内部使用的CSS变量 */
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
  
  /* 额外的CSS变量用于交互效果 */
  --card-background: rgba(255, 255, 255, 0.95);
  --card-border: rgba(108, 99, 255, 0.1);
  --card-hover-background: rgba(255, 255, 255, 1);
  --card-hover-border: rgba(108, 99, 255, 0.3);
  --card-shadow: 0 8px 32px rgba(108, 99, 255, 0.1);
  --card-hover-shadow: 0 16px 40px rgba(108, 99, 255, 0.2);
  
  /* 按钮样式变量 */
  --btn-background: linear-gradient(135deg, #6C63FF 0%, #86A8E7 100%);
  --btn-hover-background: linear-gradient(135deg, #5A52E8 0%, #7B9FE0 100%);
  --btn-shadow: 0 4px 15px rgba(108, 99, 255, 0.3);
  --btn-hover-shadow: 0 6px 20px rgba(108, 99, 255, 0.4);
}

.chat-interface {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: var(--background-color);
  border-radius: 0;
  margin: 0;
  overflow: hidden;
  box-shadow: none;
  position: relative;
}

.tech-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  overflow: hidden;
  pointer-events: none;
}

.gradient-orb {
  position: absolute;
  width: 200px;
  height: 200px;
  border-radius: 50%;
  opacity: 0.1;
  animation: orbit 20s linear infinite;
}

.orb-1 {
  top: -50px;
  left: -50px;
  background: radial-gradient(circle, rgba(108, 99, 255, 0.1) 0%, rgba(134, 168, 231, 0.1) 100%);
}

.orb-2 {
  top: 100px;
  right: -50px;
  background: radial-gradient(circle, rgba(145, 234, 228, 0.1) 0%, rgba(108, 99, 255, 0.1) 100%);
}

.orb-3 {
  bottom: -50px;
  left: 100px;
  background: radial-gradient(circle, rgba(108, 99, 255, 0.1) 0%, rgba(134, 168, 231, 0.1) 100%);
}

.tech-grid {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0) 70%);
  animation: grid-spin 10s linear infinite;
}

@keyframes orbit {
  0%, 100% {
    transform: translate(-20px, -20px) rotate(0deg);
  }
  50% {
    transform: translate(20px, 20px) rotate(180deg);
  }
}

@keyframes grid-spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.welcome-screen {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: linear-gradient(135deg, 
    rgba(108, 99, 255, 0.1) 0%, 
    rgba(134, 168, 231, 0.1) 50%, 
    rgba(145, 234, 228, 0.1) 100%
  );
  backdrop-filter: blur(20px);
  position: relative;
  overflow: hidden;
}

.welcome-screen::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(45deg, 
    transparent 30%, 
    rgba(108, 99, 255, 0.05) 50%, 
    transparent 70%
  );
  animation: floating-bg 20s ease-in-out infinite;
}

@keyframes floating-bg {
  0%, 100% {
    transform: translate(-20px, -20px) rotate(0deg);
  }
  50% {
    transform: translate(20px, 20px) rotate(180deg);
  }
}

.welcome-content {
  text-align: center;
  max-width: 700px;
  position: relative;
  z-index: 10;
  animation: fadeInUp 1s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.hero-section {
  margin-bottom: 50px;
  animation: heroFloat 3s ease-in-out infinite;
}

@keyframes heroFloat {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
}

.logo-container {
  margin-bottom: 24px;
  display: flex;
  justify-content: center;
}

.logo {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  transition: all 0.3s ease;
  box-shadow: 0 8px 25px rgba(108, 99, 255, 0.3);
  border: 2px solid rgba(255, 255, 255, 0.2);
}

.logo:hover {
  transform: scale(1.1) rotate(5deg);
  box-shadow: 0 25px 50px rgba(108, 99, 255, 0.4);
}

.main-title {
  font-size: 3.2em;
  font-weight: 800;
  margin-bottom: 16px;
  background: linear-gradient(135deg, #6C63FF 0%, #86A8E7 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.02em;
  text-shadow: 0 4px 12px rgba(108, 99, 255, 0.3);
}

.subtitle {
  font-size: 1.4em;
  opacity: 0.8;
  margin-bottom: 16px;
  color: #5A67D8;
  font-weight: 500;
}

.subtitle-text {
  margin-right: 8px;
}

.food-emoji {
  font-size: 1.2em;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-top: 30px;
  margin-bottom: 35px;
}

.feature-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: var(--card-background);
  border: 2px solid var(--card-border);
  border-radius: 16px;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(20px);
  position: relative;
  overflow: hidden;
  box-shadow: var(--card-shadow);
  text-align: left;
  animation: slideInUp 0.5s ease-out;
  z-index: 5;
  pointer-events: auto;
}

.feature-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, 
    transparent, 
    rgba(108, 99, 255, 0.1), 
    transparent
  );
  transition: left 0.6s ease;
}

.feature-card:hover::before {
  left: 100%;
}

.feature-card:hover {
  background: var(--card-hover-background);
  border-color: var(--card-hover-border);
  transform: translateY(-4px) scale(1.02);
  box-shadow: var(--card-hover-shadow);
  color: var(--text-primary);
}

.card-icon-wrapper {
  flex-shrink: 0;
  filter: drop-shadow(0 4px 8px rgba(108, 99, 255, 0.3));
  transition: transform 0.3s ease;
}

.feature-card:hover .card-icon-wrapper {
  transform: scale(1.1) rotate(5deg);
}

.card-content {
  flex: 1;
  text-align: left;
}

.card-title {
  font-size: 1.05em;
  font-weight: 700;
  margin-bottom: 4px;
  color: #2D3748;
}

.card-description {
  font-size: 0.85em;
  opacity: 0.7;
  color: #718096;
  line-height: 1.3;
  margin: 0;
}

/* 智能控制面板 */
.control-panel {
  background: linear-gradient(135deg, 
    rgba(255, 255, 255, 0.95) 0%, 
    rgba(255, 255, 255, 0.85) 100%);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(108, 99, 255, 0.15);
  border-radius: 20px;
  padding: 24px;
  margin: 30px 0;
  box-shadow: 
    0 8px 32px rgba(108, 99, 255, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
  transition: all 0.3s ease;
}

.control-panel:hover {
  border-color: rgba(108, 99, 255, 0.25);
  box-shadow: 
    0 12px 40px rgba(108, 99, 255, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.9);
}

.control-section {
  margin-bottom: 20px;
}

.control-section:last-child {
  margin-bottom: 0;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: 600;
  color: #4A5568;
}

.section-icon {
  font-size: 16px;
}

.section-title {
  flex: 1;
}

.tools-count {
  background: linear-gradient(135deg, #6C63FF 0%, #86A8E7 100%);
  color: white;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
  min-width: 20px;
  text-align: center;
}

.modern-selector {
  width: 100%;
  background: linear-gradient(135deg, 
    rgba(255, 255, 255, 0.9) 0%, 
    rgba(248, 250, 252, 0.9) 100%);
  border: 1px solid rgba(108, 99, 255, 0.2);
  border-radius: 14px;
  padding: 14px 16px;
  padding-right: 45px;
  font-size: 14px;
  color: var(--text-primary);
  cursor: pointer;
  outline: none;
  transition: all 0.3s ease;
  appearance: none;
  box-shadow: 
    0 2px 8px rgba(108, 99, 255, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
  font-weight: 500;
}

.modern-selector:focus {
  border-color: var(--primary-color);
  box-shadow: 
    0 0 0 3px rgba(108, 99, 255, 0.12),
    0 4px 12px rgba(108, 99, 255, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.9);
  background: linear-gradient(135deg, 
    rgba(255, 255, 255, 0.95) 0%, 
    rgba(248, 250, 252, 0.95) 100%);
}

.modern-selector:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background: rgba(248, 250, 252, 0.5);
}

.selector-chevron {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: #6B7280;
  pointer-events: none;
  transition: all 0.3s ease;
}

.modern-selector:focus + .selector-chevron {
  color: var(--primary-color);
  transform: translateY(-50%) rotate(180deg);
}

.tools-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tool-chip {
  background: linear-gradient(135deg, #6C63FF 0%, #86A8E7 100%);
  color: white;
  padding: 6px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(108, 99, 255, 0.3);
  transition: all 0.3s ease;
}

.tool-chip:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(108, 99, 255, 0.4);
}

.more-tools-chip {
  background: linear-gradient(135deg, 
    rgba(108, 99, 255, 0.1) 0%, 
    rgba(134, 168, 231, 0.1) 100%);
  color: #6C63FF;
  border: 1px solid rgba(108, 99, 255, 0.2);
}

/* 推荐例子气泡样式 */
.example-bubbles {
  margin-bottom: 20px;
  text-align: center;
}

.bubbles-label {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 12px;
  font-weight: 500;
}

.bubbles-container {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
  max-width: 600px;
  margin: 0 auto;
}

.example-bubble {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  user-select: none;
}

.example-bubble:hover {
  background: rgba(108, 99, 255, 0.15);
  border-color: rgba(108, 99, 255, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(108, 99, 255, 0.15);
}

.example-bubble:active {
  transform: translateY(0);
  transition: transform 0.1s ease;
}

.bubble-icon {
  font-size: 14px;
  display: inline-block;
}

.bubble-text {
  font-size: 13px;
  font-weight: 500;
  white-space: nowrap;
}

/* 对话界面推荐例子气泡样式 */
.chat-example-bubbles {
  padding: 0 20px 12px 20px;
  text-align: center;
}

.chat-bubbles-container {
  display: flex;
  justify-content: center;
  gap: 8px;
  flex-wrap: wrap;
}

.chat-example-bubble {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 12px;
  color: var(--text-secondary);
  user-select: none;
}

.chat-example-bubble:hover {
  background: rgba(108, 99, 255, 0.12);
  border-color: rgba(108, 99, 255, 0.25);
  color: var(--text-primary);
  transform: translateY(-1px);
}

.chat-example-bubble:active {
  transform: translateY(0);
}

.chat-bubble-icon {
  font-size: 12px;
  display: inline-block;
}

.chat-bubble-text {
  font-size: 11px;
  font-weight: 500;
  white-space: nowrap;
}

/* 欢迎界面输入框样式 */
.input-section {
  margin-top: 50px;
  width: 100%;
  animation: inputGlow 2s ease-in-out infinite alternate;
}

@keyframes inputGlow {
  0% {
    filter: drop-shadow(0 0 8px rgba(108, 99, 255, 0.3));
  }
  100% {
    filter: drop-shadow(0 0 16px rgba(108, 99, 255, 0.5));
  }
}

.input-card {
  display: flex;
  align-items: flex-end;
  gap: 16px;
  background: linear-gradient(135deg, 
    rgba(255, 255, 255, 0.98) 0%, 
    rgba(255, 255, 255, 0.95) 100%);
  border: 2px solid rgba(108, 99, 255, 0.2);
  border-radius: 24px;
  padding: 24px 28px;
  backdrop-filter: blur(20px);
  box-shadow: 
    0 12px 40px rgba(108, 99, 255, 0.15),
    0 4px 16px rgba(108, 99, 255, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.9);
  transition: all 0.3s ease;
  pointer-events: auto;
  position: relative;
  overflow: hidden;
  animation: cardPulse 3s ease-in-out infinite;
}

@keyframes cardPulse {
  0%, 100% {
    transform: translateY(0px) scale(1);
    box-shadow: 
      0 12px 40px rgba(108, 99, 255, 0.15),
      0 4px 16px rgba(108, 99, 255, 0.1),
      inset 0 1px 0 rgba(255, 255, 255, 0.9);
  }
  50% {
    transform: translateY(-2px) scale(1.01);
    box-shadow: 
      0 16px 50px rgba(108, 99, 255, 0.2),
      0 6px 20px rgba(108, 99, 255, 0.15),
      inset 0 1px 0 rgba(255, 255, 255, 0.95);
  }
}

.input-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, 
    transparent, 
    rgba(108, 99, 255, 0.08), 
    transparent);
  animation: shimmer 4s ease-in-out infinite;
}

@keyframes shimmer {
  0% {
    left: -100%;
  }
  50% {
    left: 100%;
  }
  100% {
    left: 100%;
  }
}

.input-card:focus-within {
  border-color: rgba(108, 99, 255, 0.4);
  box-shadow: 
    0 16px 50px rgba(108, 99, 255, 0.25),
    0 8px 25px rgba(108, 99, 255, 0.2),
    0 0 0 4px rgba(108, 99, 255, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.95);
  transform: translateY(-3px) scale(1.02);
  animation: none;
}

.main-input {
  flex: 1;
  border: none;
  background: transparent;
  color: var(--text-primary);
  font-size: 16px;
  line-height: 1.5;
  padding: 18px 22px;
  resize: none;
  outline: none;
  min-height: 28px;
  max-height: 120px;
  font-family: inherit;
  pointer-events: auto;
  position: relative;
  z-index: 2;
}

.main-input::placeholder {
  color: rgba(108, 99, 255, 0.6) !important;
  opacity: 1;
  font-weight: 500;
  background: linear-gradient(45deg, #6C63FF, #86A8E7, #91EAE4);
  background-size: 200% 200%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: gradientFlow 3s ease-in-out infinite;
}

@keyframes gradientFlow {
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

/* 聊天输入框placeholder样式 */
.chat-input {
  flex: 1;
  border: none;
  background: transparent;
  color: var(--text-primary);
  font-size: 16px;
  line-height: 1.5;
  resize: none;
  outline: none;
  min-height: 24px;
  max-height: 120px;
  font-family: inherit;
  pointer-events: auto;
}

.chat-input::placeholder {
  color: #bbb !important;
  opacity: 1;
  font-weight: 400;
}

.send-button {
  background: linear-gradient(135deg, #6C63FF 0%, #86A8E7 100%);
  color: white;
  border: none;
  border-radius: 16px;
  padding: 12px 20px;
  cursor: pointer;
  font-weight: 600;
  font-size: 16px;
  transition: all 0.3s ease;
  box-shadow: 
    0 4px 16px rgba(108, 99, 255, 0.3),
    0 2px 8px rgba(108, 99, 255, 0.2);
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  min-width: 80px;
  pointer-events: auto;
  z-index: 10;
}

.send-button:hover:not(:disabled) {
  background: linear-gradient(135deg, #584DE6 0%, #7294D3 100%);
  transform: translateY(-2px);
  box-shadow: 
    0 8px 25px rgba(108, 99, 255, 0.4),
    0 4px 16px rgba(108, 99, 255, 0.3);
}

.send-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* 移除旧的模型选择器样式 */

.model-selector-wrapper {
  position: relative;
  flex: 1;
}

.model-selector {
  flex: 1;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(108, 99, 255, 0.2);
  border-radius: 12px;
  padding: 12px 16px;
  font-size: 14px;
  color: var(--text-primary);
  cursor: pointer;
  outline: none;
  transition: all 0.3s ease;
  appearance: none;
  pointer-events: auto;
  z-index: 10;
}

.model-selector:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(108, 99, 255, 0.1);
}

.model-selector:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.selector-arrow {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 16px;
  color: var(--text-secondary);
  pointer-events: none;
}

/* 对话界面相关样式 */
.messages-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.messages-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  scroll-behavior: smooth;
}

.message-wrapper {
  margin-bottom: 20px;
}

.message-wrapper.user {
  display: flex;
  justify-content: flex-end;
}

.message-wrapper.assistant {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.message-bubble {
  max-width: 75%;
  padding: 16px 20px;
  border-radius: 18px;
  line-height: 1.5;
  position: relative;
}

.message-wrapper.assistant .message-bubble {
  align-self: flex-start;
}

.message-wrapper.user .message-bubble {
  background: var(--btn-background);
  color: white;
  border-bottom-right-radius: 6px;
}

.message-wrapper.assistant .message-bubble {
  background: var(--surface-color);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  border-bottom-left-radius: 6px;
}

.message-bubble.error {
  background: rgba(231, 76, 60, 0.1);
  border-color: var(--error-color);
  color: var(--error-color);
}

.message-content {
  font-size: 15px;
  line-height: 1.6;
  margin: 0;
  margin-left: 30px;
}

/* Markdown 元素样式 */
.message-content h1,
.message-content h2,
.message-content h3,
.message-content h4,
.message-content h5,
.message-content h6 {
  margin: 12px 0 8px 0;
  color: var(--text-primary);
  font-weight: 600;
}

.message-content h1 { font-size: 1.5em; }
.message-content h2 { font-size: 1.3em; }
.message-content h3 { font-size: 1.2em; }
.message-content h4 { font-size: 1.1em; }
.message-content h5 { font-size: 1.05em; }
.message-content h6 { font-size: 1em; }

.message-content p {
  margin: 8px 0;
}

.message-content ul,
.message-content ol {
  margin: 8px 0;
  padding-left: 24px;
}

.message-content li {
  margin: 4px 0;
}

.message-content blockquote {
  margin: 12px 0;
  padding: 8px 16px;
  border-left: 4px solid var(--primary-color);
  background: rgba(108, 99, 255, 0.1);
  border-radius: 0 8px 8px 0;
  font-style: italic;
}

.message-content code {
  background: rgba(108, 99, 255, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Monaco', 'Consolas', 'Courier New', monospace;
  font-size: 0.9em;
  color: var(--text-primary);
}

.message-content pre {
  background: rgba(108, 99, 255, 0.1);
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 12px 0;
  border: 1px solid var(--border-color);
}

.message-content pre code {
  background: none;
  padding: 0;
  border-radius: 0;
}

.message-content a {
  color: var(--primary-color);
  text-decoration: none;
  border-bottom: 1px solid transparent;
  transition: border-color 0.3s ease;
}

.message-content a:hover {
  border-bottom-color: var(--primary-color);
}

.message-content table {
  width: 100%;
  border-collapse: collapse;
  margin: 12px 0;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
}

.message-content th,
.message-content td {
  padding: 8px 12px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.message-content th {
  background: var(--surface-color);
  font-weight: 600;
  color: var(--text-primary);
}

.message-content tr:last-child th,
.message-content tr:last-child td {
  border-bottom: none;
}

.message-content hr {
  border: none;
  height: 1px;
  background: var(--border-color);
  margin: 16px 0;
}

.message-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 12px;
  opacity: 0.7;
}

.timestamp {
  color: inherit;
}

.tools-used {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.tool-tag {
  background: var(--primary-color);
  color: white;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 10px;
  font-weight: 500;
}

.thinking-indicator {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0 20px 20px;
  padding: 16px 20px;
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: 18px;
  color: var(--text-secondary);
  font-size: 14px;
}

.thinking-animation {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding: 16px 20px;
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: 18px;
  color: var(--text-secondary);
  font-size: 14px;
}

.thinking-dots {
  display: flex;
  gap: 4px;
}

.thinking-dots .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--primary-color);
  animation: thinkingPulse 1.4s ease-in-out infinite both;
}

.thinking-dots .dot:nth-child(2) {
  animation-delay: 0.2s;
}

.thinking-dots .dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes thinkingPulse {
  0%, 80%, 100% {
    transform: scale(0);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

/* 输入区域样式 */
.chat-input-container {
  padding: 20px;
  background: var(--surface-color);
  border-top: 1px solid var(--border-color);
}

.chat-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.chat-model-selector {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  font-size: 13px;
}

.chat-model-selector .model-icon {
  font-size: 16px;
  color: var(--text-secondary);
}

.chat-model-selector .model-title {
  flex: 1;
}

.model-dropdown {
  border: none;
  background: transparent;
  font-size: 13px;
  color: var(--text-primary);
  cursor: pointer;
  outline: none;
  padding: 2px 4px;
}

.model-dropdown:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.chat-tools-status {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: var(--background-color);
  border: 1px solid var(--border-color);
  border-radius: 12px;
}

.tools-icon {
  font-size: 16px;
  color: var(--text-secondary);
}

.tools-chips {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tool-chip {
  background: var(--btn-background);
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  box-shadow: var(--btn-shadow);
}

.more-chip {
  background: rgba(108, 99, 255, 0.1);
  color: var(--primary-color);
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.chat-input-wrapper {
  display: flex;
  align-items: flex-end;
  gap: 16px;
  background: linear-gradient(135deg, 
    rgba(255, 255, 255, 0.9) 0%, 
    rgba(248, 250, 252, 0.9) 100%);
  border: 2px solid rgba(108, 99, 255, 0.12);
  border-radius: 20px;
  padding: 18px 22px;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  box-shadow: 
    0 4px 20px rgba(108, 99, 255, 0.06),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
}

.chat-input-wrapper:focus-within {
  border-color: rgba(108, 99, 255, 0.4);
  box-shadow: 
    0 8px 25px rgba(108, 99, 255, 0.15),
    0 4px 16px rgba(108, 99, 255, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.9);
  transform: translateY(-2px);
  background: linear-gradient(135deg, 
    rgba(255, 255, 255, 0.95) 0%, 
    rgba(248, 250, 252, 0.95) 100%);
}

/* 新增输入字段容器样式 */
.input-field-container {
  flex: 1;
  position: relative;
  display: flex;
  flex-direction: column;
}

/* 优化输入框样式 */
.chat-input {
  width: 100%;
  min-height: 24px;
  max-height: 120px;
  resize: none;
  border: none;
  outline: none;
  background: transparent;
  font-size: 16px;
  font-family: inherit;
  line-height: 1.5;
  color: var(--text-primary);
  overflow-y: hidden;
  transition: all 0.2s ease;
}

.chat-input::placeholder {
  color: rgba(108, 99, 255, 0.6);
  font-style: italic;
}

.chat-input:focus::placeholder {
  color: rgba(108, 99, 255, 0.4);
}

/* 字数统计样式 */
.char-count {
  position: absolute;
  bottom: 2px;
  right: 8px;
  font-size: 11px;
  color: var(--text-secondary);
  background: rgba(255, 255, 255, 0.9);
  padding: 2px 6px;
  border-radius: 8px;
  pointer-events: none;
  transition: all 0.2s ease;
}

/* 发送按钮优化 */
.chat-send-btn {
  background: linear-gradient(135deg, #6C63FF 0%, #86A8E7 100%);
  color: white;
  border: none;
  border-radius: 50%;
  width: 44px;
  height: 44px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  flex-shrink: 0;
  box-shadow: 
    0 4px 16px rgba(108, 99, 255, 0.3),
    0 2px 8px rgba(108, 99, 255, 0.2);
  pointer-events: auto;
  transform: scale(0.95);
}

.chat-send-btn.has-content {
  transform: scale(1);
  background: linear-gradient(135deg, #584DE6 0%, #7294D3 100%);
  box-shadow: 
    0 6px 20px rgba(108, 99, 255, 0.4),
    0 3px 12px rgba(108, 99, 255, 0.3);
}

.chat-send-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #4C45D9 0%, #6689CB 100%);
  transform: translateY(-2px) scale(1.05);
  box-shadow: 
    0 8px 25px rgba(108, 99, 255, 0.5),
    0 4px 16px rgba(108, 99, 255, 0.4);
}

.chat-send-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: scale(0.95);
}

.send-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s ease;
}

.chat-send-btn:hover .send-icon {
  transform: translateX(1px);
}

.chat-send-btn:active {
  transform: translateY(-1px) scale(0.98);
}

.chat-input-card {
  display: flex;
  align-items: flex-end;
  gap: 16px;
  background: linear-gradient(135deg, 
    rgba(255, 255, 255, 0.95) 0%, 
    rgba(255, 255, 255, 0.85) 100%);
  border: 1px solid rgba(108, 99, 255, 0.15);
  border-radius: 20px;
  padding: 16px 20px;
  backdrop-filter: blur(20px);
  box-shadow: 
    0 8px 32px rgba(108, 99, 255, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
  transition: all 0.3s ease;
  pointer-events: auto;
}

.chat-input-card:focus-within {
  border-color: rgba(108, 99, 255, 0.25);
  box-shadow: 
    0 12px 40px rgba(108, 99, 255, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.9);
  transform: translateY(-1px);
}



.mini-spinner {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 移动端优化 */
@media (max-width: 768px) {
  .chat-interface {
    margin: 8px;
    height: calc(100vh - 16px);
    border-radius: 8px;
  }
  
  .welcome-screen {
    padding: 20px 15px;
  }
  
  .title {
    font-size: 2.2em;
    line-height: 1.2;
    margin-bottom: 12px;
  }
  
  .subtitle {
    font-size: 1.1em;
    line-height: 1.4;
    margin-bottom: 20px;
  }
  
  .logo {
    width: 70px;
    height: 70px;
    margin-bottom: 16px;
  }
  
  .logo-section {
    margin-bottom: 35px;
  }
  
  .quick-start-cards {
    grid-template-columns: 1fr;
    gap: 14px;
    margin-top: 30px;
    margin-bottom: 30px;
  }
  
  .quick-start-card {
    padding: 18px;
    border-radius: 16px;
    gap: 16px;
  }
  
  .card-icon {
    font-size: 2.3em;
  }
  
  .card-title {
    font-size: 1.05em;
    margin-bottom: 6px;
  }
  
  .card-description {
    font-size: 0.88em;
    line-height: 1.3;
  }
  
  .welcome-tools-status {
    margin-bottom: 25px;
    padding: 14px 16px;
    border-radius: 12px;
  }
  
  .welcome-tools-status .tools-label {
    font-size: 13px;
    display: block;
    margin-bottom: 8px;
    margin-right: 0;
  }
  
  .welcome-tools-status .tools-list {
    display: flex;
    gap: 6px;
  }
  
  .welcome-tools-status .tool-badge {
    font-size: 11px;
    padding: 3px 10px;
  }
  
  .welcome-input-section {
    margin-top: 30px;
  }
  
  .welcome-input-wrapper {
    padding: 14px 16px;
    border-radius: 18px;
    gap: 12px;
  }
  
  .welcome-message-input {
    font-size: 16px; /* 防止iOS自动缩放 */
    min-height: 20px;
  }
  
  .welcome-send-btn {
    padding: 12px 20px;
    font-size: 14px;
    border-radius: 14px;
    min-height: 44px; /* 触摸友好的最小高度 */
  }
  
  .messages-list {
    padding: 12px;
  }
  
  .message-wrapper {
    margin-bottom: 16px;
  }
  
  .message-bubble {
    max-width: 82%;
    padding: 14px 16px;
    border-radius: 16px;
  }
  
  .message-content {
    font-size: 15px;
    line-height: 1.5;
  }
  
  .message-meta {
    font-size: 11px;
    margin-top: 6px;
  }
  
  .thinking-indicator {
    margin: 0 12px 16px;
    padding: 14px 16px;
    border-radius: 12px;
  }
  
  .input-container {
    padding: 12px;
  }
  
  .tools-status {
    margin-bottom: 12px;
    padding: 10px 12px;
    border-radius: 10px;
  }
  
  .tools-status .tools-label {
    font-size: 13px;
    display: block;
    margin-bottom: 6px;
    margin-right: 0;
  }
  
  .tools-status .tools-list {
    gap: 6px;
  }
  
  .tools-status .tool-badge {
    font-size: 11px;
    padding: 3px 8px;
  }
  
  .input-wrapper {
    padding: 12px 14px;
    border-radius: 14px;
    gap: 10px;
  }

  .input-wrapper::placeholder {
  color: #000000; /* 设置你想要的颜色 */
}
  
  .message-input {
    font-size: 16px; /* 防止iOS自动缩放 */
    min-height: 20px;
  }
  
  .send-btn {
    padding: 10px 16px;
    font-size: 14px;
    border-radius: 10px;
    min-height: 40px; /* 触摸友好的最小高度 */
  }
  
  /* 移动设备上的工具结果样式调整 */
  .tool-result-container {
    margin: 12px 0;
  }
  
  .tool-result-header {
    padding: 10px 12px;
    font-size: 13px;
  }
  
  /* 移动端图片网格优化 */
  .tool-result-container.image-gallery {
    margin: 12px 0;
  }
  
  .tool-result-header {
    padding: 12px 16px;
    font-size: 14px;
  }
  
  .image-gallery .image-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    padding: 16px;
  }
  
  .image-item {
    min-height: 120px;
  }
  
  .image-item img {
    min-height: 120px;
  }
  
  .inline-image img {
    min-height: 120px;
  }
  
  .location-result .location-list {
    padding: 12px;
  }
  
  .location-item {
    padding: 10px;
    margin-bottom: 8px;
  }
  
  .location-address {
    font-size: 14px;
  }
  
  .map-link {
    padding: 8px 12px;
    font-size: 11px;
  }
  
  .recipe-section {
    padding: 12px;
  }
  
  .recipe-section-title {
    font-size: 15px;
  }
  
  .ingredients-list {
    gap: 6px;
  }
  
  .ingredient-item {
    padding: 4px 8px;
    font-size: 12px;
  }
  
  .step-item {
    padding: 10px;
    gap: 10px;
  }
  
  .step-number {
    width: 20px;
    height: 20px;
    font-size: 11px;
  }
  
  .step-instruction {
    font-size: 14px;
  }
}

/* 工具结果容器样式 */
.tool-results-container {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* 覆盖ToolResultDisplay中的一些样式以适配消息气泡 */
.message-bubble .tool-result-display .result-container {
  margin: 0;
  border-radius: 8px;
  box-shadow: none;
  border: 1px solid var(--border-color);
}

.message-bubble .tool-result-display .result-header {
  padding: 12px 16px;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
}

/* 调整AI消息中的工具结果样式 */
.message-wrapper.assistant .tool-result-display .result-container {
  background: rgba(255, 255, 255, 0.8);
}

.message-wrapper.assistant .tool-result-display .result-container:hover {
  background: rgba(255, 255, 255, 0.95);
}

/* 移动端适配 */
@media (max-width: 768px) {
  .tool-results-container {
    margin-top: 12px;
    gap: 8px;
  }
  
  .message-bubble .tool-result-display .result-header {
    padding: 10px 12px;
    font-size: 14px;
  }
}

@media (max-width: 480px) {
  .chat-interface {
    margin: 4px;
    height: calc(100vh - 8px);
    border-radius: 6px;
  }
  
  .welcome-screen {
    padding: 16px 12px;
  }
  
  .welcome-content {
    max-width: 100%;
  }
  
  .title {
    font-size: 1.8em;
    margin-bottom: 10px;
  }
  
  .subtitle {
    font-size: 0.95em;
    margin-bottom: 16px;
  }
  
  .logo {
    width: 60px;
    height: 60px;
    margin-bottom: 14px;
  }
  
  .logo-section {
    margin-bottom: 28px;
  }
  
  .quick-start-cards {
    gap: 10px;
    margin-top: 25px;
    margin-bottom: 25px;
  }
  
  .quick-start-card {
    padding: 14px;
    flex-direction: column;
    text-align: center;
    gap: 10px;
    border-radius: 14px;
    min-height: 100px; /* 确保触摸目标足够大 */
  }
  
  .card-content {
    text-align: center;
  }
  
  .card-icon {
    font-size: 1.8em;
  }
  
  .card-title {
    font-size: 0.95em;
    margin-bottom: 4px;
  }
  
  .card-description {
    font-size: 0.8em;
    line-height: 1.25;
  }
  
  .welcome-tools-status {
    margin-bottom: 20px;
    padding: 12px 14px;
  }
  
  .welcome-tools-status .tools-label {
    font-size: 12px;
  }
  
  .welcome-tools-status .tool-badge {
    font-size: 10px;
    padding: 2px 8px;
  }
  
  .welcome-input-section {
    margin-top: 25px;
  }
  
  .welcome-input-wrapper {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
    padding: 12px 14px;
    border-radius: 16px;
  }
  
  .welcome-message-input {
    font-size: 16px; /* 防止iOS自动缩放 */
    min-height: 24px;
    text-align: center;
  }
  
  .welcome-send-btn {
    align-self: center;
    min-width: 140px;
    min-height: 48px; /* 更大的触摸目标 */
    padding: 14px 24px;
    font-size: 15px;
    border-radius: 16px;
  }
  
  .messages-list {
    padding: 8px;
  }
  
  .message-wrapper {
    margin-bottom: 12px;
  }
  
  .message-bubble {
    max-width: 88%;
    padding: 12px 14px;
    border-radius: 14px;
  }
  
  .message-content {
    font-size: 14px;
    line-height: 1.4;
  }
  
  .message-meta {
    font-size: 10px;
    margin-top: 4px;
  }
  
  .tool-tag {
    font-size: 9px;
    padding: 1px 6px;
  }
  
  .thinking-indicator {
    margin: 0 8px 12px;
    padding: 12px 14px;
    border-radius: 10px;
  }
  
  .thinking-indicator span {
    font-size: 13px;
  }
  
  .input-container {
    padding: 8px;
  }
  
  .tools-status {
    margin-bottom: 10px;
    padding: 8px 10px;
    border-radius: 8px;
  }
  
  .tools-status .tools-label {
    font-size: 12px;
    margin-bottom: 5px;
  }
  
  .tools-status .tool-badge {
    font-size: 10px;
    padding: 2px 6px;
  }
  
  .input-wrapper {
    flex-direction: column;
    gap: 10px;
    align-items: stretch;
    padding: 10px 12px;
    border-radius: 12px;
  }
  
  .message-input {
    font-size: 16px; /* 防止iOS自动缩放 */
    min-height: 24px;
    text-align: left;
  }
  
  .send-btn {
    align-self: center;
    min-width: 120px;
    min-height: 44px; /* 触摸友好的高度 */
    padding: 12px 20px;
    font-size: 14px;
    border-radius: 12px;
  }
}

/* 超小屏幕优化 (iPhone SE 等) */
@media (max-width: 375px) {
  .welcome-screen {
    padding: 12px 8px;
  }
  
  .title {
    font-size: 1.6em;
  }
  
  .subtitle {
    font-size: 0.9em;
  }
  
  .logo {
    width: 50px;
    height: 50px;
  }
  
  .quick-start-card {
    padding: 12px;
    min-height: 90px;
  }
  
  .card-icon {
    font-size: 1.6em;
  }
  
  .card-title {
    font-size: 0.9em;
  }
  
  .card-description {
    font-size: 0.75em;
  }
  
  .welcome-input-wrapper {
    padding: 10px 12px;
  }
  
  .welcome-send-btn {
    min-width: 120px;
    padding: 12px 20px;
    font-size: 14px;
  }
  
  .message-bubble {
    max-width: 90%;
    padding: 10px 12px;
  }
  
  .message-content {
    font-size: 13px;
  }
}

/* 横屏模式优化 */
@media (max-width: 768px) and (orientation: landscape) {
  .welcome-screen {
    padding: 12px 15px;
  }
  
  .logo-section {
    margin-bottom: 20px;
  }
  
  .title {
    font-size: 1.6em;
  }
  
  .subtitle {
    font-size: 0.9em;
  }
  
  .logo {
    width: 50px;
    height: 50px;
    margin-bottom: 8px;
  }
  
  .quick-start-cards {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    margin-top: 20px;
    margin-bottom: 20px;
  }
  
  .quick-start-card {
    padding: 12px;
    min-height: auto;
  }
  
  .card-icon {
    font-size: 1.5em;
  }
  
  .welcome-input-section {
    margin-top: 20px;
  }
  
  .chat-interface {
    height: calc(100vh - 8px);
  }
}

/* 防止缩放和改善触摸体验 */
@media (max-width: 768px) {
  /* 防止双击缩放 */
  .quick-start-card,
  .welcome-send-btn,
  .send-btn {
    touch-action: manipulation;
    -webkit-tap-highlight-color: transparent;
  }
  
  /* 改善滚动性能 */
  .messages-list {
    -webkit-overflow-scrolling: touch;
    overscroll-behavior: contain;
  }
  
  /* 优化输入框体验 */
  .welcome-message-input,
  .message-input {
    -webkit-appearance: none;
    -moz-appearance: none;
    appearance: none;
    border-radius: 0;
    -webkit-tap-highlight-color: transparent;
  }
  
  /* 优化按钮点击反馈 */
  .quick-start-card:active {
    transform: translateY(-2px) scale(0.98);
    transition-duration: 0.1s;
  }
  
  .welcome-send-btn:active,
  .send-btn:active {
    transform: scale(0.95);
    transition-duration: 0.1s;
  }
  
  /* 防止iOS Safari底部工具栏影响 */
  .chat-interface {
    min-height: calc(100vh - 16px);
    min-height: calc(100dvh - 16px); /* 动态视口高度 */
  }
  
  .messages-container {
    height: calc(100vh - 40px);
    height: calc(100dvh - 40px); /* 动态视口高度 */
  }
}

/* iOS 特殊优化 */
@supports (-webkit-touch-callout: none) {
  .welcome-message-input,
  .message-input {
    /* 禁用iOS的自动缩放 */
    -webkit-text-size-adjust: 100%;
    font-size: 16px !important; /* 防止iOS缩放 */
  }
  
  /* iOS安全区域适配 */
  .chat-interface {
    padding-top: env(safe-area-inset-top);
    padding-bottom: env(safe-area-inset-bottom);
    padding-left: env(safe-area-inset-left);
    padding-right: env(safe-area-inset-right);
  }
  
  /* iOS键盘弹出优化 */
  @media (max-width: 768px) {
    .input-container {
      padding-bottom: calc(12px + env(safe-area-inset-bottom));
    }
    
    .welcome-input-section {
      padding-bottom: env(safe-area-inset-bottom);
    }
  }
}

/* Android 特殊优化 */
@media (max-width: 768px) {
  /* Android Chrome地址栏隐藏适配 */
  .chat-interface {
    min-height: -webkit-fill-available;
  }
  
  /* 优化Android键盘体验 */
  .welcome-message-input:focus,
  .message-input:focus {
    transform: translateZ(0); /* 强制硬件加速 */
  }
}

/* PWA和全屏模式优化 */
@media (display-mode: standalone) {
  .chat-interface {
    height: 100vh;
    margin: 0;
    border-radius: 0;
  }
  
  .welcome-screen {
    padding-top: calc(20px + env(safe-area-inset-top));
  }
}

/* 高DPI屏幕优化 */
@media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {
  .logo {
    image-rendering: -webkit-optimize-contrast;
    image-rendering: crisp-edges;
  }
  
  .card-icon {
    text-rendering: optimizeLegibility;
  }
}

/* 减少动画以节省电池（用户偏好） */
@media (prefers-reduced-motion: reduce) {
  .quick-start-card,
  .welcome-send-btn,
  .send-btn,
  .message-bubble,
  .thinking-dots .dot {
    animation: none !important;
    transition: none !important;
  }
  
  .quick-start-card:hover,
  .welcome-send-btn:hover,
  .send-btn:hover {
    transform: none !important;
  }
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  @media (max-width: 768px) {
    .welcome-screen {
      background: linear-gradient(135deg, 
        rgba(45, 55, 72, 0.9) 0%, 
        rgba(55, 65, 81, 0.9) 50%, 
        rgba(75, 85, 99, 0.9) 100%
      );
    }
    
    .quick-start-card {
      background: rgba(45, 55, 72, 0.95);
      border-color: rgba(108, 99, 255, 0.3);
      color: #F7FAFC;
    }
    
    .card-title {
      color: #F7FAFC;
    }
    
    .card-description {
      color: #CBD5E0;
    }
    
    .welcome-input-wrapper,
    .input-wrapper {
      background: rgba(45, 55, 72, 0.9);
      border-color: rgba(108, 99, 255, 0.3);
    }
    
    .welcome-message-input,
    .message-input {
      color: #F7FAFC;
    }
    
    .welcome-message-input::placeholder,
    .message-input::placeholder {
      color: #A0AEC0;
    }
    
    .message-wrapper.assistant .message-bubble {
      background: rgba(45, 55, 72, 0.95);
      color: #F7FAFC;
      border-color: rgba(108, 99, 255, 0.2);
    }
    
    .tools-status,
    .welcome-tools-status {
      background: rgba(45, 55, 72, 0.8);
      border-color: rgba(108, 99, 255, 0.2);
    }
    
    .thinking-indicator {
      background: rgba(45, 55, 72, 0.9);
      color: #F7FAFC;
      border-color: rgba(108, 99, 255, 0.2);
    }
  }
}

/* 新增科技感样式 */
.title-gradient {
  background: linear-gradient(135deg, #6C63FF 0%, #86A8E7 50%, #91EAE4 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: gradientShift 3s ease-in-out infinite;
}

@keyframes gradientShift {
  0%, 100% { filter: hue-rotate(0deg); }
  50% { filter: hue-rotate(15deg); }
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.card-background {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
  border-radius: inherit;
  opacity: 0;
  transition: all 0.3s ease;
}

.feature-card:hover .card-background {
  opacity: 1;
}

.card-hover-effect {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(108, 99, 255, 0.1) 0%, rgba(134, 168, 231, 0.1) 100%);
  border-radius: inherit;
  opacity: 0;
  transition: all 0.3s ease;
}

.feature-card:hover .card-hover-effect {
  opacity: 1;
}

.send-content {
  display: flex;
  align-items: center;
  gap: 6px;
}

.send-text {
  font-weight: 600;
}

.send-icon {
  font-size: 18px;
  transition: transform 0.3s ease;
}

.send-button:hover .send-icon {
  transform: translateX(2px);
}

.loading-spinner {
  display: flex;
  align-items: center;
  justify-content: center;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.mini-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 优化后的响应式设计 */
@media (max-width: 768px) {
  .chat-interface {
    margin: 0;
    height: 100vh;
    border-radius: 0;
    overflow-x: hidden;
  }

  .welcome-screen {
    padding: 16px;
    min-height: 100vh;
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
  }

  .welcome-content {
    padding: 20px 0;
    max-width: 100%;
    min-height: calc(100vh - 40px);
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
  }

  .hero-section {
    margin-bottom: 24px;
    text-align: center;
  }

  .logo-container {
    margin-bottom: 16px;
  }

  .logo {
    width: 80px;
    height: 80px;
  }

  .main-title {
    font-size: 2em;
    margin-bottom: 8px;
    line-height: 1.2;
  }

  .subtitle {
    font-size: 1em;
    margin-bottom: 0;
  }

  .features-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    margin-bottom: 24px;
  }

  .feature-card {
    padding: 16px 12px;
    min-height: 120px;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    justify-content: center;
  }

  .card-icon {
    font-size: 1.8em;
    margin-bottom: 8px;
  }

  .card-title {
    font-size: 14px;
    margin-bottom: 4px;
  }

  .card-description {
    font-size: 11px;
    line-height: 1.3;
  }

  .control-panel {
    margin: 16px 0;
    padding: 16px;
    border-radius: 16px;
  }

  .section-header {
    margin-bottom: 10px;
  }

  .section-title {
    font-size: 13px;
  }

  .modern-selector {
    padding: 12px 14px;
    padding-right: 40px;
    font-size: 14px;
    border-radius: 12px;
  }

  .tools-grid {
    gap: 6px;
    justify-content: flex-start;
  }

  .tool-chip {
    font-size: 11px;
    padding: 4px 8px;
  }

  .input-section {
    margin-top: 20px;
    margin-bottom: 20px;
  }

  .input-card {
    padding: 16px;
    gap: 12px;
    border-radius: 16px;
  }

  .main-input {
    font-size: 16px;
    padding: 14px 0;
    line-height: 1.4;
    min-height: 22px;
  }

  .send-button {
    padding: 12px 16px;
    font-size: 14px;
    border-radius: 12px;
    min-width: 70px;
  }

  /* 聊天界面移动端优化 */
  .messages-container {
    padding-bottom: 20px;
  }

  .messages-list {
    padding: 16px;
  }

  .message-bubble {
    max-width: 85%;
    padding: 12px 16px;
    font-size: 15px;
    border-radius: 16px;
  }

  .chat-input-container {
    padding: 16px;
    background: var(--surface-color);
    border-top: 1px solid var(--border-color);
  }

  .chat-input-card {
    padding: 12px 16px;
    gap: 12px;
    border-radius: 16px;
  }

  .chat-input {
    font-size: 16px;
    padding: 12px 0;
    line-height: 1.4;
  }

  .chat-send-btn {
    width: 40px;
    height: 40px;
    border-radius: 50%;
  }

  .chat-toolbar {
    flex-direction: column;
    gap: 10px;
    align-items: stretch;
    margin-bottom: 12px;
  }

  .chat-model-selector,
  .chat-tools-status {
    padding: 10px 12px;
    border-radius: 10px;
    font-size: 13px;
  }

  .tools-chips {
    justify-content: flex-start;
    flex-wrap: wrap;
  }

  .tool-chip {
    font-size: 11px;
    padding: 3px 8px;
  }
}

@media (max-width: 480px) {
  .welcome-screen {
    padding: 12px;
  }

  .welcome-content {
    padding: 16px 0;
    min-height: calc(100vh - 32px);
  }

  .hero-section {
    margin-bottom: 20px;
  }

  .logo {
    width: 70px;
    height: 70px;
  }

  .main-title {
    font-size: 1.8em;
    margin-bottom: 6px;
  }

  .subtitle {
    font-size: 0.9em;
  }

  .features-grid {
    grid-template-columns: 1fr;
    gap: 10px;
    margin-bottom: 20px;
  }

  .feature-card {
    padding: 14px 10px;
    min-height: 80px;
    flex-direction: row;
    text-align: left;
    align-items: center;
    justify-content: flex-start;
  }

  .card-icon {
    font-size: 1.6em;
    margin-bottom: 0;
    margin-right: 12px;
    flex-shrink: 0;
  }

  .card-content {
    flex: 1;
  }

  .card-title {
    font-size: 13px;
    margin-bottom: 2px;
  }

  .card-description {
    font-size: 10px;
    line-height: 1.2;
  }

  .control-panel {
    margin: 12px 0;
    padding: 14px;
    border-radius: 14px;
  }

  .control-section {
    margin-bottom: 14px;
  }

  .section-header {
    margin-bottom: 8px;
  }

  .section-title {
    font-size: 12px;
  }

  .modern-selector {
    padding: 11px 13px;
    padding-right: 35px;
    font-size: 13px;
    border-radius: 10px;
  }

  .tools-grid {
    gap: 4px;
  }

  .tool-chip {
    font-size: 10px;
    padding: 3px 6px;
    border-radius: 8px;
  }

  /* 推荐例子气泡移动端样式 */
  .example-bubbles {
    margin-bottom: 14px;
  }

  .bubbles-label {
    font-size: 13px;
    margin-bottom: 10px;
  }

  .bubbles-container {
    gap: 8px;
  }

  .example-bubble {
    padding: 6px 10px;
    font-size: 12px;
    border-radius: 16px;
  }

  .bubble-icon {
    font-size: 12px;
  }

  .bubble-text {
    font-size: 12px;
  }

  .chat-example-bubbles {
    padding: 0 12px 10px 12px;
  }

  .chat-bubbles-container {
    gap: 6px;
  }

  .chat-example-bubble {
    padding: 5px 8px;
    border-radius: 14px;
  }

  .chat-bubble-icon {
    font-size: 11px;
  }

  .chat-bubble-text {
    font-size: 10px;
  }

  .input-section {
    margin-top: 20px;
    margin-bottom: 20px;
    animation: mobileInputGlow 2.5s ease-in-out infinite alternate;
  }

  @keyframes mobileInputGlow {
    0% {
      filter: drop-shadow(0 0 12px rgba(108, 99, 255, 0.4));
    }
    100% {
      filter: drop-shadow(0 0 20px rgba(108, 99, 255, 0.6));
    }
  }

  .input-card {
    padding: 20px 24px;
    gap: 12px;
    border-radius: 20px;
    border: 2px solid rgba(108, 99, 255, 0.25);
    animation: mobileCardPulse 3.5s ease-in-out infinite;
  }

  @keyframes mobileCardPulse {
    0%, 100% {
      transform: translateY(0px) scale(1);
      box-shadow: 
        0 15px 45px rgba(108, 99, 255, 0.2),
        0 5px 18px rgba(108, 99, 255, 0.15),
        inset 0 1px 0 rgba(255, 255, 255, 0.9);
    }
    50% {
      transform: translateY(-3px) scale(1.015);
      box-shadow: 
        0 20px 55px rgba(108, 99, 255, 0.25),
        0 8px 25px rgba(108, 99, 255, 0.2),
        inset 0 1px 0 rgba(255, 255, 255, 0.95);
    }
  }

  .main-input {
    font-size: 16px;
    padding: 12px 0;
    line-height: 1.3;
    min-height: 20px;
  }

  .send-button {
    padding: 10px 12px;
    font-size: 13px;
    border-radius: 10px;
    min-width: 60px;
  }

  .send-text {
    display: none;
  }

  /* 聊天界面小屏优化 */
  .messages-list {
    padding: 12px;
  }

  .message-bubble {
    max-width: 90%;
    padding: 10px 14px;
    font-size: 14px;
    border-radius: 14px;
  }

  .chat-input-container {
    padding: 12px;
  }

  .chat-input-card {
    padding: 10px 14px;
    gap: 10px;
    border-radius: 14px;
  }

  .chat-input {
    font-size: 16px;
    padding: 10px 0;
    line-height: 1.3;
  }

  .chat-send-btn {
    width: 36px;
    height: 36px;
  }

  .chat-toolbar {
    gap: 8px;
    margin-bottom: 10px;
  }

  .chat-model-selector,
  .chat-tools-status {
    padding: 8px 10px;
    border-radius: 8px;
    font-size: 12px;
  }

  .tool-chip {
    font-size: 10px;
    padding: 2px 6px;
  }
}

/* 超小屏幕优化 */
@media (max-width: 320px) {
  .welcome-screen {
    padding: 8px;
  }

  .welcome-content {
    padding: 12px 0;
    min-height: calc(100vh - 20px);
  }

  .hero-section {
    margin-bottom: 16px;
  }

  .logo {
    width: 60px;
    height: 60px;
  }

  .main-title {
    font-size: 1.6em;
    margin-bottom: 4px;
  }

  .subtitle {
    font-size: 0.85em;
  }

  .features-grid {
    gap: 8px;
    margin-bottom: 16px;
  }

  .feature-card {
    padding: 10px 8px;
    min-height: 70px;
  }

  .card-icon {
    font-size: 1.4em;
    margin-right: 10px;
  }

  .card-title {
    font-size: 12px;
    margin-bottom: 1px;
  }

  .card-description {
    font-size: 9px;
  }

  .control-panel {
    margin: 10px 0;
    padding: 12px;
    border-radius: 12px;
  }

  .control-section {
    margin-bottom: 12px;
  }

  .section-header {
    margin-bottom: 6px;
  }

  .section-title {
    font-size: 11px;
  }

  .modern-selector {
    padding: 10px 12px;
    padding-right: 32px;
    font-size: 12px;
    border-radius: 8px;
  }

  .tools-grid {
    gap: 3px;
  }

  .tool-chip {
    font-size: 9px;
    padding: 2px 5px;
    border-radius: 6px;
  }

  /* 推荐例子气泡超小屏样式 */
  .example-bubbles {
    margin-bottom: 12px;
  }

  .bubbles-label {
    font-size: 12px;
    margin-bottom: 8px;
  }

  .bubbles-container {
    gap: 6px;
  }

  .example-bubble {
    padding: 5px 8px;
    font-size: 11px;
    border-radius: 14px;
  }

  .bubble-icon {
    font-size: 11px;
  }

  .bubble-text {
    font-size: 11px;
  }

  .chat-example-bubbles {
    padding: 0 8px 8px 8px;
  }

  .chat-bubbles-container {
    gap: 4px;
  }

  .chat-example-bubble {
    padding: 4px 6px;
    border-radius: 12px;
  }

  .chat-bubble-icon {
    font-size: 10px;
  }

  .chat-bubble-text {
    font-size: 9px;
  }

  .input-section {
    margin-top: 12px;
    margin-bottom: 12px;
  }

  .input-card {
    padding: 10px;
    gap: 8px;
    border-radius: 12px;
  }

  .main-input {
    font-size: 16px;
    padding: 10px 0;
    line-height: 1.2;
  }

  .send-button {
    padding: 8px 10px;
    font-size: 12px;
    border-radius: 8px;
    min-width: 50px;
  }

  /* 聊天界面超小屏优化 */
  .messages-list {
    padding: 8px;
  }

  .message-bubble {
    max-width: 95%;
    padding: 8px 12px;
    font-size: 13px;
    border-radius: 12px;
  }

  .chat-input-container {
    padding: 8px;
  }

  .chat-input-card {
    padding: 8px 12px;
    gap: 8px;
    border-radius: 12px;
  }

  .chat-input {
    font-size: 16px;
    padding: 8px 0;
  }

  .chat-send-btn {
    width: 32px;
    height: 32px;
  }

  .chat-toolbar {
    gap: 6px;
    margin-bottom: 8px;
  }

  .chat-model-selector,
  .chat-tools-status {
    padding: 6px 8px;
    border-radius: 6px;
    font-size: 11px;
  }
}

/* 高分辨率屏幕优化 */
@media (min-width: 1200px) {
  .welcome-content {
    max-width: 900px;
  }

  .features-grid {
    grid-template-columns: repeat(4, 1fr);
    gap: 24px;
  }

  .feature-card {
    flex-direction: column;
    text-align: center;
    padding: 30px 20px;
  }

  .card-icon-wrapper {
    margin-bottom: 16px;
  }

  .card-icon {
    font-size: 3em;
  }
}

/* 暗色主题适配 */
@media (prefers-color-scheme: dark) {
  .tech-background .gradient-orb {
    opacity: 0.05;
  }

  .feature-card {
    background: rgba(255, 255, 255, 0.03);
    border-color: rgba(255, 255, 255, 0.1);
  }

  .feature-card:hover {
    background: rgba(255, 255, 255, 0.05);
    border-color: rgba(108, 99, 255, 0.3);
  }

  .control-panel,
  .input-card {
    background: rgba(255, 255, 255, 0.03);
    border-color: rgba(255, 255, 255, 0.1);
  }

  .main-input::placeholder,
.chat-input::placeholder {
  color: #bbb !important;
}
}

/* 动画性能优化 */
@media (prefers-reduced-motion: reduce) {
  .gradient-orb,
  .tech-grid,
  .hero-section,
  .feature-card {
    animation: none;
  }

  .feature-card {
    animation-delay: 0s;
  }

  .title-gradient {
    animation: none;
    background: linear-gradient(135deg, #6C63FF 0%, #86A8E7 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
}

/* 无障碍访问优化 */
@media (prefers-contrast: high) {
  .feature-card {
    border-width: 2px;
    border-color: var(--text-primary);
  }

  .card-title,
  .card-description {
    color: var(--text-primary);
  }

  .tool-chip {
    border: 2px solid var(--primary-color);
  }
}

/* iOS和Android安全区域适配 */
@supports (padding: max(0px)) {
  @media (max-width: 768px) {
    .chat-interface {
      height: 100vh;
      height: 100dvh; /* 动态视口高度 */
      padding-top: env(safe-area-inset-top);
      padding-bottom: env(safe-area-inset-bottom);
    }
    
    .welcome-screen {
      padding-top: max(16px, env(safe-area-inset-top));
      padding-bottom: max(16px, env(safe-area-inset-bottom));
      min-height: calc(100vh - env(safe-area-inset-top) - env(safe-area-inset-bottom));
      min-height: calc(100dvh - env(safe-area-inset-top) - env(safe-area-inset-bottom));
    }
    
    .chat-input-container {
      padding-bottom: max(16px, env(safe-area-inset-bottom));
    }
    
    /* 键盘弹起时的适配 */
    .chat-interface.keyboard-open {
      height: 100vh;
      height: 100svh; /* 小视口高度，键盘弹起时使用 */
    }
  }
  
  @media (max-width: 480px) {
    .welcome-screen {
      padding-top: max(12px, env(safe-area-inset-top));
      padding-bottom: max(12px, env(safe-area-inset-bottom));
    }
    
    .chat-input-container {
      padding-bottom: max(12px, env(safe-area-inset-bottom));
    }
    
    .input-section {
      margin-bottom: max(16px, env(safe-area-inset-bottom));
    }
  }
  
  @media (max-width: 320px) {
    .welcome-screen {
      padding-top: max(8px, env(safe-area-inset-top));
      padding-bottom: max(8px, env(safe-area-inset-bottom));
    }
    
    .chat-input-container {
      padding-bottom: max(8px, env(safe-area-inset-bottom));
    }
    
    .input-section {
      margin-bottom: max(12px, env(safe-area-inset-bottom));
    }
  }
}

/* 触摸设备优化 */
@media (hover: none) and (pointer: coarse) {
  .feature-card,
  .control-panel,
  .input-card,
  .send-button,
  .modern-selector,
  .example-bubble,
  .chat-example-bubble {
    -webkit-tap-highlight-color: transparent;
    touch-action: manipulation;
  }
  
  .feature-card:active {
    transform: scale(0.98);
    transition: transform 0.1s ease;
  }

  .example-bubble:active,
  .chat-example-bubble:active {
    transform: scale(0.95);
    transition: transform 0.1s ease;
  }
  
  .send-button:active,
  .chat-send-btn:active {
    transform: scale(0.95);
    transition: transform 0.1s ease;
  }
  
  /* 确保输入框在iOS上正确显示 */
  .main-input,
  .chat-input {
    -webkit-appearance: none;
    border-radius: 0;
  }
}
/* 集成输入框样式 - 欢迎界面 */
.input-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  max-width: 900px;
  width: 100%;
  margin: 30px auto 0;
}

.integrated-input-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(108, 99, 255, 0.15);
  border-radius: 24px;
  box-shadow: 
    0 20px 40px rgba(108, 99, 255, 0.1),
    0 8px 32px rgba(0, 0, 0, 0.05);
  padding: 24px;
  width: 100%;
  max-width: 700px;
  margin: 0 auto;
  transition: all 0.3s ease;
}

.integrated-input-card:hover {
  border-color: rgba(108, 99, 255, 0.25);
  box-shadow: 
    0 25px 50px rgba(108, 99, 255, 0.15),
    0 12px 40px rgba(0, 0, 0, 0.08);
}

/* AI模型选择区域 */
.input-model-section {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
  padding: 16px 20px;
  background: linear-gradient(135deg, rgba(108, 99, 255, 0.05) 0%, rgba(134, 168, 231, 0.05) 100%);
  border: 1px solid rgba(108, 99, 255, 0.1);
  border-radius: 16px;
}

.model-header {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 100px;
}

.model-icon {
  font-size: 20px;
  color: var(--primary-color);
}

.model-label {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 14px;
}

.model-selector-wrapper {
  position: relative;
  flex: 1;
}

.integrated-model-selector {
  width: 100%;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(108, 99, 255, 0.2);
  border-radius: 12px;
  padding: 12px 40px 12px 16px;
  font-size: 14px;
  color: var(--text-primary);
  cursor: pointer;
  outline: none;
  transition: all 0.3s ease;
  appearance: none;
}

.integrated-model-selector:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(108, 99, 255, 0.1);
}

.selector-chevron {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-secondary);
  pointer-events: none;
}

/* 智能工具区域 */
.input-tools-section {
  margin-bottom: 20px;
  padding: 16px 20px;
  background: linear-gradient(135deg, rgba(134, 168, 231, 0.05) 0%, rgba(108, 99, 255, 0.05) 100%);
  border: 1px solid rgba(134, 168, 231, 0.1);
  border-radius: 16px;
}

.tools-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.tools-icon {
  font-size: 18px;
  color: var(--secondary-color);
}

.tools-label {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 14px;
}

.tools-count {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
  color: white;
  font-size: 12px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 10px;
  margin-left: auto;
}

.input-tools-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.input-tool-chip {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(134, 168, 231, 0.2);
  color: var(--text-primary);
  padding: 6px 12px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.input-tool-chip:hover {
  background: rgba(134, 168, 231, 0.1);
  border-color: var(--secondary-color);
}

.more-tools-chip {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
  color: white;
  border: none;
}

/* 对话界面集成输入框样式 */
.chat-input-container {
  padding: 16px 20px 20px;
  background: linear-gradient(135deg, 
    rgba(255, 255, 255, 0.95) 0%, 
    rgba(248, 250, 252, 0.95) 100%);
  backdrop-filter: blur(20px);
  border-top: 1px solid rgba(108, 99, 255, 0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
  position: sticky;
  bottom: 0;
  z-index: 10;
  box-shadow: 0 -4px 20px rgba(108, 99, 255, 0.08);
}

.chat-integrated-input-card {
  background: linear-gradient(135deg, 
    rgba(255, 255, 255, 0.98) 0%, 
    rgba(255, 255, 255, 0.95) 100%);
  backdrop-filter: blur(30px);
  border: 2px solid rgba(108, 99, 255, 0.15);
  border-radius: 24px;
  box-shadow: 
    0 20px 40px rgba(108, 99, 255, 0.1),
    0 8px 32px rgba(0, 0, 0, 0.05),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
  padding: 24px;
  width: 100%;
  max-width: 650px;
  margin: 0 auto;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.chat-integrated-input-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, 
    transparent, 
    rgba(108, 99, 255, 0.05), 
    transparent
  );
  transition: left 0.6s ease;
  pointer-events: none;
}

.chat-integrated-input-card:hover::before {
  left: 100%;
}

.chat-integrated-input-card:hover {
  border-color: rgba(108, 99, 255, 0.3);
  box-shadow: 
    0 25px 50px rgba(108, 99, 255, 0.15),
    0 12px 40px rgba(0, 0, 0, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.9);
  transform: translateY(-2px);
}

/* AI大脑和智能工具水平排列容器 */
.chat-controls-row {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
  align-items: flex-start;
}

/* 对话界面模型选择区域 */
.chat-model-section {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: linear-gradient(135deg, rgba(108, 99, 255, 0.04) 0%, rgba(134, 168, 231, 0.04) 100%);
  border: 1px solid rgba(108, 99, 255, 0.08);
  border-radius: 12px;
  flex: 1;
  min-width: 0;
}

.chat-model-header {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 80px;
}

.chat-model-icon {
  font-size: 16px;
  color: var(--primary-color);
}

.chat-model-label {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 13px;
}

.chat-model-wrapper {
  position: relative;
  flex: 1;
}

.chat-model-selector {
  width: 100%;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(108, 99, 255, 0.15);
  border-radius: 10px;
  padding: 10px 32px 10px 12px;
  font-size: 13px;
  color: var(--text-primary);
  cursor: pointer;
  outline: none;
  transition: all 0.3s ease;
  appearance: none;
}

.chat-model-selector:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(108, 99, 255, 0.08);
}

.chat-selector-chevron {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-secondary);
  pointer-events: none;
}

/* 对话界面工具区域 */
.chat-tools-section {
  padding: 12px 16px;
  background: linear-gradient(135deg, rgba(134, 168, 231, 0.04) 0%, rgba(108, 99, 255, 0.04) 100%);
  border: 1px solid rgba(134, 168, 231, 0.08);
  border-radius: 12px;
  flex: 1;
  min-width: 0;
}

.chat-tools-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
}

.chat-tools-icon {
  font-size: 16px;
  color: var(--secondary-color);
}

.chat-tools-label {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 13px;
}

.chat-tools-count {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
  color: white;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 8px;
  margin-left: auto;
}

.chat-tools-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.chat-tool-chip {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(134, 168, 231, 0.15);
  color: var(--text-primary);
  padding: 4px 10px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.chat-tool-chip:hover {
  background: rgba(134, 168, 231, 0.08);
  border-color: var(--secondary-color);
}

.chat-more-chip {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
  color: white;
  border: none;
}

/* 推荐例子气泡样式调整 */
.chat-example-bubbles {
  margin-bottom: 16px;
  max-width: 600px;
  width: 100%;
}

.chat-bubbles-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
}

.chat-example-bubble {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(108, 99, 255, 0.1);
  color: var(--text-primary);
  padding: 8px 12px;
  border-radius: 12px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.chat-example-bubble:hover {
  background: rgba(108, 99, 255, 0.08);
  border-color: var(--primary-color);
  transform: translateY(-1px);
}

.chat-bubble-icon {
  font-size: 14px;
}

.chat-bubble-text {
  font-weight: 500;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .integrated-input-card,
  .chat-integrated-input-card {
    margin: 0 16px;
    padding: 20px;
    border-radius: 20px;
  }
  
  /* 移动端水平布局改为垂直 */
  .chat-controls-row {
    flex-direction: column;
    gap: 12px;
  }
  
  .input-model-section,
  .chat-model-section {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .model-header,
  .chat-model-header {
    justify-content: center;
    min-width: auto;
  }
  
  .input-tools-section,
  .chat-tools-section {
    padding: 16px;
  }
  
  .input-tools-grid,
  .chat-tools-chips {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .integrated-input-card,
  .chat-integrated-input-card {
    margin: 0 12px;
    padding: 16px;
    border-radius: 16px;
  }
  
  .input-model-section,
  .chat-model-section,
  .input-tools-section,
  .chat-tools-section {
    padding: 12px;
    border-radius: 12px;
  }
  
  .input-tool-chip,
  .chat-tool-chip {
    font-size: 12px;
    padding: 4px 8px;
  }
}

</style> 
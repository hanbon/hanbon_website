<template>
  <div class="floating-buttons" :class="{ 'has-messages': hasMessages }">
    <!-- 背景遮罩 -->
    <div 
      v-if="isMenuOpen" 
      class="fab-overlay"
      @click="closeMenu"
    ></div>
    
    <!-- 主浮动按钮 -->
    <div 
      class="main-fab" 
      @click="toggleMenu" 
      :class="{ active: isMenuOpen }"
    >
      <div class="fab-icon">
        <svg v-if="!isMenuOpen" viewBox="0 0 24 24" width="24" height="24">
          <path fill="currentColor" d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
        </svg>
        <svg v-else viewBox="0 0 24 24" width="24" height="24">
          <path fill="currentColor" d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12 19 6.41z"/>
        </svg>
      </div>
      <div class="fab-ripple"></div>
    </div>
    
    <!-- 子按钮菜单 -->
    <div v-if="isMenuOpen" class="fab-menu">
      <div 
        v-for="(action, index) in fabActions"
        :key="action.id"
        class="fab-item"
        :style="{ 
          animationDelay: `${index * 0.08}s`,
          '--translate-y': `-${(index + 1) * 80}px`
        }"
        @click="handleAction(action)"
      >
        <div class="fab-button" :class="action.type">
          <div class="fab-button-icon">
            {{ action.icon }}
          </div>
          <div class="fab-button-ripple"></div>
        </div>
        <div class="fab-tooltip">
          <span class="fab-label">{{ action.label }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * @description 现代化浮动操作按钮组件
 * 提供新建对话、历史记录、设置等快捷操作
 */
export default {
  name: 'FloatingButtons',
  props: {
    hasMessages: {
      type: Boolean,
      default: false
    }
  },
  emits: ['newChat', 'showHistory', 'showSettings', 'showMemory'],
  data() {
    return {
      isMenuOpen: false,
      
      // 浮动按钮操作列表
      fabActions: [
        {
          id: 'new-chat',
          icon: '💬',
          label: '新建对话',
          type: 'primary',
          action: 'newChat'
        },
        {
          id: 'memory',
          icon: '🧠',
          label: '记忆管理',
          type: 'secondary',
          action: 'showMemory'
        },
        {
          id: 'history',
          icon: '📝',
          label: '聊天记录',
          type: 'secondary',
          action: 'showHistory'
        },
        {
          id: 'settings',
          icon: '⚙️',
          label: '系统设置',
          type: 'secondary',
          action: 'showSettings'
        },
        {
          id: 'help',
          icon: '❓',
          label: '使用帮助',
          type: 'info',
          action: 'showHelp'
        }
      ]
    }
  },
  mounted() {
    // 监听键盘快捷键
    document.addEventListener('keydown', this.handleKeydown)
  },
  beforeUnmount() {
    document.removeEventListener('keydown', this.handleKeydown)
  },
  methods: {
    /**
     * @description 切换菜单显示状态
     */
    toggleMenu() {
      this.isMenuOpen = !this.isMenuOpen
    },
    
    /**
     * @description 关闭菜单
     */
    closeMenu() {
      this.isMenuOpen = false
    },
    
    /**
     * @description 处理浮动按钮操作
     */
    handleAction(action) {
      this.closeMenu()
      
      // 添加延迟确保菜单关闭动画完成
      setTimeout(() => {
        switch (action.action) {
          case 'newChat':
            this.$emit('newChat')
            break
          case 'showMemory':
            this.$emit('showMemory')
            break
          case 'showHistory':
            this.$emit('showHistory')
            break
          case 'showSettings':
            this.$emit('showSettings')
            break
          case 'showHelp':
            this.showHelp()
            break
        }
      }, 150)
    },
    
    /**
     * @description 显示帮助信息
     */
    showHelp() {
      const helpContent = `食慧美食AI助手使用指南：

🍽️ 基本功能：
• 询问美食推荐："推荐一些好吃的菜"
• 查看菜谱："教我做宫保鸡丁"
• 搜索餐厅："附近有什么好吃的"
• 营养咨询："这道菜的营养价值如何"

🛠️ 工具功能：
• 地图搜索：查找附近餐厅和美食地点
• 天气助手：根据天气推荐合适的美食
• 图片搜索：寻找美食相关图片
• 菜谱生成：AI生成详细的制作步骤

⌨️ 快捷键：
• Ctrl + N：新建对话
• Ctrl + H：查看历史记录
• Ctrl + ,：打开设置
• Esc：关闭当前面板

💡 小贴士：
• 描述得越详细，AI的回答越准确
• 可以告诉AI你的口味偏好和饮食限制
• 启用位置服务可以获得更精准的推荐`
      
      alert(helpContent)
    },
    
    /**
     * @description 处理键盘快捷键
     */
    handleKeydown(event) {
      // Ctrl + N: 新建对话
      if (event.ctrlKey && event.key === 'n') {
        event.preventDefault()
        this.$emit('newChat')
      }
      
      // Ctrl + H: 历史记录
      if (event.ctrlKey && event.key === 'h') {
        event.preventDefault()
        this.$emit('showHistory')
      }
      
      // Ctrl + ,: 设置
      if (event.ctrlKey && event.key === ',') {
        event.preventDefault()
        this.$emit('showSettings')
      }
      
      // Esc: 关闭菜单
      if (event.key === 'Escape') {
        this.closeMenu()
      }
    }
  }
}
</script>

<style scoped>
.floating-buttons {
  position: fixed;
  bottom: 30px;
  right: 30px;
  z-index: 1000;
  pointer-events: none;
}

.floating-buttons * {
  pointer-events: auto;
}

.fab-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(15, 23, 42, 0.3);
  z-index: 999;
  backdrop-filter: blur(8px);
  animation: overlayFadeIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes overlayFadeIn {
  from { 
    opacity: 0;
    backdrop-filter: blur(0px);
  }
  to { 
    opacity: 1;
    backdrop-filter: blur(8px);
  }
}

.main-fab {
  width: 64px;
  height: 64px;
  background: linear-gradient(135deg, 
    rgba(108, 99, 255, 0.95) 0%, 
    rgba(134, 168, 231, 0.95) 100%);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 
    0 8px 32px rgba(108, 99, 255, 0.3),
    0 4px 16px rgba(108, 99, 255, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  z-index: 1001;
  border: 1px solid rgba(255, 255, 255, 0.2);
  overflow: hidden;
}

.main-fab:hover {
  transform: translateY(-2px) scale(1.05);
  box-shadow: 
    0 12px 40px rgba(108, 99, 255, 0.4),
    0 8px 24px rgba(108, 99, 255, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.4);
  background: linear-gradient(135deg, 
    rgba(88, 77, 230, 0.95) 0%, 
    rgba(114, 148, 211, 0.95) 100%);
}

.main-fab.active {
  background: linear-gradient(135deg, 
    rgba(239, 68, 68, 0.95) 0%, 
    rgba(245, 101, 101, 0.95) 100%);
  transform: translateY(-2px) scale(1.05) rotate(90deg);
  box-shadow: 
    0 8px 30px rgba(239, 68, 68, 0.5),
    0 16px 60px rgba(239, 68, 68, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

.fab-icon {
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 2;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
}

.fab-ripple {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: inherit;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.3) 0%, transparent 70%);
  opacity: 0;
  transform: scale(0);
  transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.main-fab:active .fab-ripple {
  opacity: 1;
  transform: scale(1);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.fab-menu {
  position: absolute;
  bottom: 0;
  right: 0;
  z-index: 1000;
}

@keyframes fabItemSlideUp {
  0% {
    opacity: 0;
    transform: translateY(20px) scale(0.8);
  }
  100% {
    opacity: 1;
    transform: translateY(var(--translate-y, -80px)) scale(1);
  }
}

.fab-item {
  position: absolute;
  bottom: 0;
  right: 0;
  display: flex;
  align-items: center;
  opacity: 0;
  animation: fabItemSlideUp 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
  transform: translateY(var(--translate-y, -80px)) scale(1);
}

.fab-button {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  box-shadow: 
    0 4px 16px rgba(15, 23, 42, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.fab-button.primary {
  background: linear-gradient(135deg, 
    rgba(34, 197, 94, 0.95) 0%, 
    rgba(108, 99, 255, 0.95) 100%);
}

.fab-button.secondary {
  background: linear-gradient(135deg, 
    rgba(108, 99, 255, 0.95) 0%, 
    rgba(134, 168, 231, 0.95) 100%);
}

.fab-button.info {
  background: linear-gradient(135deg, 
    rgba(108, 99, 255, 0.95) 0%, 
    rgba(134, 168, 231, 0.95) 100%);
}

.fab-button:hover {
  transform: translateY(-2px) scale(1.08);
  box-shadow: 
    0 8px 25px rgba(15, 23, 42, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

.fab-button-icon {
  font-size: 24px;
  z-index: 2;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.fab-button:hover .fab-button-icon {
  transform: scale(1.1);
}

.fab-button-ripple {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: inherit;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.3) 0%, transparent 70%);
  opacity: 0;
  transform: scale(0);
  transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.fab-button:active .fab-button-ripple {
  opacity: 1;
  transform: scale(1);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.fab-tooltip {
  position: absolute;
  right: 70px;
  top: 50%;
  transform: translateY(-50%);
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  pointer-events: none;
}

.fab-item:hover .fab-tooltip {
  opacity: 1;
  visibility: visible;
  transform: translateY(-50%) translateX(-8px);
}

.fab-label {
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(20px);
  color: white;
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
  box-shadow: 
    0 4px 20px rgba(15, 23, 42, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
}

.fab-label::after {
  content: '';
  position: absolute;
  left: 100%;
  top: 50%;
  transform: translateY(-50%);
  width: 0;
  height: 0;
  border-top: 8px solid transparent;
  border-bottom: 8px solid transparent;
  border-left: 8px solid rgba(15, 23, 42, 0.95);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .floating-buttons {
    bottom: 100px; /* 提高位置，避免与输入框重叠 */
    right: 20px;
    z-index: 1001;
  }
  
  .main-fab {
    width: 56px;
    height: 56px;
    border-radius: 16px;
    -webkit-tap-highlight-color: transparent;
    touch-action: manipulation;
    box-shadow: 
      0 6px 24px rgba(108, 99, 255, 0.4),
      0 4px 12px rgba(108, 99, 255, 0.3);
  }
  
  .fab-button {
    width: 48px;
    height: 48px;
    border-radius: 14px;
    -webkit-tap-highlight-color: transparent;
    touch-action: manipulation;
    box-shadow: 
      0 4px 16px rgba(108, 99, 255, 0.3),
      0 2px 8px rgba(108, 99, 255, 0.2);
  }
  
  .fab-button-icon {
    font-size: 18px;
  }
  
  .fab-tooltip {
    display: none;
  }
}

@media (max-width: 480px) {
  .floating-buttons {
    bottom: 80px; /* 进一步调整位置 */
    right: 16px;
  }
  
  .main-fab {
    width: 52px;
    height: 52px;
    border-radius: 14px;
    box-shadow: 
      0 4px 20px rgba(108, 99, 255, 0.4),
      0 3px 10px rgba(108, 99, 255, 0.3);
  }
  
  .fab-icon svg {
    width: 18px;
    height: 18px;
  }
  
  .fab-button {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    box-shadow: 
      0 3px 12px rgba(108, 99, 255, 0.3),
      0 2px 6px rgba(108, 99, 255, 0.2);
  }
  
  .fab-button-icon {
    font-size: 16px;
  }
  
  /* 优化小屏的间距 */
  .fab-item {
    margin-bottom: 8px;
  }
}

/* 超小屏幕优化 */
@media (max-width: 320px) {
  .floating-buttons {
    bottom: 70px;
    right: 12px;
  }
  
  .main-fab {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    box-shadow: 
      0 3px 16px rgba(108, 99, 255, 0.4),
      0 2px 8px rgba(108, 99, 255, 0.3);
  }
  
  .fab-icon svg {
    width: 16px;
    height: 16px;
  }
  
  .fab-button {
    width: 40px;
    height: 40px;
    border-radius: 10px;
    box-shadow: 
      0 2px 10px rgba(108, 99, 255, 0.3),
      0 1px 4px rgba(108, 99, 255, 0.2);
  }
  
  .fab-button-icon {
    font-size: 14px;
  }
  
  .fab-item {
    margin-bottom: 6px;
  }
  
  .floating-buttons.has-messages {
    bottom: 80px;
  }
}

/* 为不同状态添加动画效果 */
.floating-buttons.has-messages {
  bottom: 120px; /* 在聊天界面时更高位置 */
}

@media (max-width: 768px) {
  .floating-buttons.has-messages {
    bottom: 110px; /* 移动端聊天界面位置 */
  }
}

@media (max-width: 480px) {
  .floating-buttons.has-messages {
    bottom: 90px; /* 小屏聊天界面位置 */
  }
}

/* 暗色主题适配 */
@media (prefers-color-scheme: dark) {
  .fab-overlay {
    background: rgba(0, 0, 0, 0.5);
  }
  
  .fab-label {
    background: rgba(30, 30, 30, 0.95);
    color: #f8fafc;
  }
  
  .fab-label::after {
    border-left-color: rgba(30, 30, 30, 0.95);
  }
}

/* 减少动画以节省电池 */
@media (prefers-reduced-motion: reduce) {
  .main-fab,
  .fab-button,
  .fab-tooltip,
  .fab-ripple,
  .fab-button-ripple {
    transition: none !important;
    animation: none !important;
  }
  
  .fab-item {
    animation: none !important;
    opacity: 1 !important;
  }
}
</style> 
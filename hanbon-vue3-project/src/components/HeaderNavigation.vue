<template>
  <header class="header-nav">
    <div class="nav-container">
      <!-- Logo区域 -->
      <div class="logo-section">
        <img src="@/assets/hanbon_logo.png" alt="食慧美食AI" class="logo">
        <div class="brand-info">
          <h1 class="brand-name">食慧美食AI</h1>
          <span class="brand-tagline">智能美食助手</span>
        </div>
      </div>
      
      <!-- 状态指示器 -->
      <div class="status-section">
        <div class="connection-status" :class="{ connected: isConnected }">
          <div class="status-dot"></div>
          <span>{{ isConnected ? '已连接' : '连接中...' }}</span>
        </div>
      </div>
      
      <!-- 操作按钮组 -->
      <div class="actions-section">
        <!-- 工具按钮 -->
        <button 
          class="nav-btn tools-btn"
          @click="$emit('toggleTools')"
          title="工具设置"
        >
          <i class="icon">🔧</i>
          <span>工具</span>
        </button>
        
        <!-- 设置按钮 -->
        <button 
          class="nav-btn settings-btn"
          @click="$emit('toggleSettings')"
          title="系统设置"
        >
          <i class="icon">⚙️</i>
          <span>设置</span>
        </button>
        
        <!-- 用户头像/菜单 -->
        <div class="user-menu" @click="toggleUserMenu">
          <div class="user-avatar">
            <i class="icon">👤</i>
          </div>
          
          <!-- 用户下拉菜单 -->
          <div v-if="showUserMenu" class="user-dropdown">
            <div class="user-info">
              <span class="user-name">美食爱好者</span>
              <span class="user-level">VIP用户</span>
            </div>
            <div class="menu-divider"></div>
            <div class="menu-items">
              <button class="menu-item" @click="handleProfile">
                <i>👤</i> 个人资料
              </button>
              <button class="menu-item" @click="handleHistory">
                <i>📝</i> 聊天记录
              </button>
              <button class="menu-item" @click="handleFeedback">
                <i>💬</i> 意见反馈
              </button>
              <div class="menu-divider"></div>
              <button class="menu-item" @click="handleLogout">
                <i>🚪</i> 退出登录
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<script>
/**
 * @description 顶部导航栏组件
 * 包含Logo、状态显示、操作按钮等功能
 */
export default {
  name: 'HeaderNavigation',
  emits: ['toggleSettings', 'toggleTools'],
  data() {
    return {
      isConnected: false,
      showUserMenu: false
    }
  },
  mounted() {
    this.checkConnection()
    
    // 点击其他地方关闭用户菜单
    document.addEventListener('click', this.handleClickOutside)
  },
  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside)
  },
  methods: {
    /**
     * @description 检查后端连接状态
     */
    async checkConnection() {
      try {
        const response = await fetch(`/api/health`)
        this.isConnected = response.ok
      } catch (error) {
        this.isConnected = false
        console.warn('后端连接检查失败:', error)
      }
      
      // 定期检查连接状态
      setTimeout(() => {
        this.checkConnection()
      }, 30000) // 30秒检查一次
    },
    
    /**
     * @description 切换用户菜单显示状态
     */
    toggleUserMenu() {
      this.showUserMenu = !this.showUserMenu
    },
    
    /**
     * @description 处理点击外部区域
     */
    handleClickOutside(event) {
      if (!event.target.closest('.user-menu')) {
        this.showUserMenu = false
      }
    },
    
    /**
     * @description 处理个人资料
     */
    handleProfile() {
      console.log('打开个人资料')
      this.showUserMenu = false
      // TODO: 实现个人资料功能
    },
    
    /**
     * @description 处理聊天记录
     */
    handleHistory() {
      console.log('打开聊天记录')
      this.showUserMenu = false
      // TODO: 实现聊天记录功能
    },
    
    /**
     * @description 处理意见反馈
     */
    handleFeedback() {
      console.log('打开意见反馈')
      this.showUserMenu = false
      // TODO: 实现意见反馈功能
    },
    
    /**
     * @description 处理退出登录
     */
    handleLogout() {
      console.log('退出登录')
      this.showUserMenu = false
      // TODO: 实现退出登录功能
    }
  }
}
</script>

<style scoped>
.header-nav {
  background: var(--background-color);
  border-bottom: 1px solid var(--border-color);
  backdrop-filter: blur(20px);
  position: sticky;
  top: 0;
  z-index: 100;
  height: 60px;
}

.nav-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 0 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.brand-info {
  display: flex;
  flex-direction: column;
}

.brand-name {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.2;
}

.brand-tagline {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 2px;
}

.status-section {
  flex: 1;
  display: flex;
  justify-content: center;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-radius: 20px;
  background: var(--surface-color);
  font-size: 14px;
  color: var(--text-secondary);
  transition: all 0.3s ease;
}

.connection-status.connected {
  background: rgba(40, 167, 69, 0.1);
  color: var(--success-color);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--error-color);
  animation: pulse 2s infinite;
}

.connection-status.connected .status-dot {
  background: var(--success-color);
  animation: none;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

.actions-section {
  display: flex;
  align-items: center;
  gap: 15px;
}

.nav-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
}

.nav-btn:hover {
  background: var(--primary-color);
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px var(--shadow-color);
}

.nav-btn .icon {
  font-size: 16px;
}

.user-menu {
  position: relative;
  cursor: pointer;
}

.user-avatar {
  width: 40px;
  height: 40px;
  background: var(--primary-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
  transition: all 0.3s ease;
}

.user-avatar:hover {
  background: var(--secondary-color);
  transform: scale(1.05);
}

.user-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 8px;
  width: 200px;
  background: var(--background-color);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  box-shadow: 0 8px 24px var(--shadow-color);
  padding: 12px 0;
  z-index: 1000;
  animation: fadeInDown 0.3s ease;
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.user-info {
  padding: 12px 16px;
  text-align: center;
}

.user-name {
  display: block;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.user-level {
  display: block;
  font-size: 12px;
  color: var(--text-secondary);
  background: var(--primary-color);
  color: white;
  padding: 2px 8px;
  border-radius: 10px;
  display: inline-block;
}

.menu-divider {
  height: 1px;
  background: var(--border-color);
  margin: 8px 0;
}

.menu-items {
  padding: 0 8px;
}

.menu-item {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: none;
  border: none;
  border-radius: 8px;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  text-align: left;
}

.menu-item:hover {
  background: var(--surface-color);
}

.menu-item i {
  font-size: 16px;
  width: 20px;
  text-align: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .nav-container {
    padding: 0 15px;
  }
  
  .brand-info {
    display: none;
  }
  
  .status-section {
    flex: none;
  }
  
  .connection-status {
    padding: 4px 8px;
    font-size: 12px;
  }
  
  .nav-btn span {
    display: none;
  }
  
  .nav-btn {
    padding: 8px;
  }
  
  .user-dropdown {
    width: 180px;
  }
}

@media (max-width: 480px) {
  .header-nav {
    height: 50px;
  }
  
  .logo {
    width: 32px;
    height: 32px;
  }
  
  .brand-name {
    font-size: 16px;
  }
  
  .user-avatar {
    width: 32px;
    height: 32px;
    font-size: 16px;
  }
  
  .actions-section {
    gap: 10px;
  }
}
</style> 
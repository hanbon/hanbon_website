<template>
  <div class="settings-panel-overlay" @click="$emit('close')">
    <div class="settings-panel" @click.stop>
      <!-- 面板头部 -->
      <div class="panel-header">
        <h3 class="panel-title">系统设置</h3>
        <button class="close-btn" @click="$emit('close')">✕</button>
      </div>
      
      <!-- 设置内容 -->
      <div class="settings-content">
        <!-- 外观设置 -->
        <div class="setting-group">
          <h4 class="group-title">外观设置</h4>
          
          <!-- 主题切换 -->
          <div class="setting-item">
            <label class="setting-label">
              <i class="icon">🎨</i>
              主题模式
            </label>
            <div class="setting-control">
              <div class="theme-selector">
                <button 
                  class="theme-option"
                  :class="{ active: localSettings.theme === 'light' }"
                  @click="updateSetting('theme', 'light')"
                >
                  <i>☀️</i>
                  <span>浅色</span>
                </button>
                <button 
                  class="theme-option"
                  :class="{ active: localSettings.theme === 'dark' }"
                  @click="updateSetting('theme', 'dark')"
                >
                  <i>🌙</i>
                  <span>深色</span>
                </button>
              </div>
            </div>
          </div>
          
          <!-- 语言设置 -->
          <div class="setting-item">
            <label class="setting-label">
              <i class="icon">🌍</i>
              语言设置
            </label>
            <div class="setting-control">
              <select 
                v-model="localSettings.language"
                class="setting-select"
                @change="updateSetting('language', $event.target.value)"
              >
                <option value="zh-CN">简体中文</option>
                <option value="zh-TW">繁體中文</option>
                <option value="en-US">English</option>
              </select>
            </div>
          </div>
        </div>
        
        <!-- AI助手设置 -->
        <div class="setting-group">
          <h4 class="group-title">AI助手设置</h4>
          
          <!-- AI个性 -->
          <div class="setting-item">
            <label class="setting-label">
              <i class="icon">🤖</i>
              AI个性
            </label>
            <div class="setting-control">
              <select 
                v-model="localSettings.aiPersonality"
                class="setting-select"
                @change="updateSetting('aiPersonality', $event.target.value)"
              >
                <option value="friendly_food_expert">友好美食专家</option>
                <option value="professional_food_expert">专业美食顾问</option>
              </select>
            </div>
          </div>
          
          <!-- 流式响应 -->
          <div class="setting-item">
            <label class="setting-label">
              <i class="icon">⚡</i>
              流式响应
            </label>
            <div class="setting-control">
              <div class="toggle-switch" 
                   :class="{ active: localSettings.streamResponse }"
                   @click="toggleSetting('streamResponse')">
                <div class="toggle-circle"></div>
              </div>
            </div>
          </div>
          
          <!-- 启用记忆功能 -->
          <div class="setting-item">
            <label class="setting-label">
              <i class="icon">🧠</i>
              启用记忆功能
            </label>
            <div class="setting-control">
              <div class="toggle-switch" 
                   :class="{ active: localSettings.enableMemory }"
                   @click="toggleSetting('enableMemory')">
                <div class="toggle-circle"></div>
              </div>
            </div>
          </div>
          
          <!-- 记忆自动保存 -->
          <div class="setting-item">
            <label class="setting-label">
              <i class="icon">💾</i>
              自动保存记忆
            </label>
            <div class="setting-control">
              <div class="toggle-switch" 
                   :class="{ active: localSettings.autoSaveMemory }"
                   @click="toggleSetting('autoSaveMemory')">
                <div class="toggle-circle"></div>
              </div>
            </div>
          </div>
          
          <!-- 最大记忆条数 -->
          <div class="setting-item">
            <label class="setting-label">
              <i class="icon">📊</i>
              最大记忆条数
            </label>
            <div class="setting-control">
              <input 
                type="number"
                v-model.number="localSettings.maxMemoryCount"
                class="setting-input"
                min="50"
                max="500"
                @change="updateSetting('maxMemoryCount', $event.target.value)"
              >
            </div>
          </div>
          
          <!-- 最大消息历史 -->
          <div class="setting-item">
            <label class="setting-label">
              <i class="icon">📝</i>
              消息历史条数
            </label>
            <div class="setting-control">
              <input 
                type="number"
                v-model.number="localSettings.maxMessageHistory"
                class="setting-input"
                min="10"
                max="100"
                @change="updateSetting('maxMessageHistory', $event.target.value)"
              >
            </div>
          </div>
        </div>
        
        <!-- 通知设置 -->
        <div class="setting-group">
          <h4 class="group-title">通知设置</h4>
          
          <!-- 启用通知 -->
          <div class="setting-item">
            <label class="setting-label">
              <i class="icon">🔔</i>
              启用通知
            </label>
            <div class="setting-control">
              <div class="toggle-switch" 
                   :class="{ active: localSettings.enableNotifications }"
                   @click="toggleSetting('enableNotifications')">
                <div class="toggle-circle"></div>
              </div>
            </div>
          </div>
          
          <!-- 自动保存历史 -->
          <div class="setting-item">
            <label class="setting-label">
              <i class="icon">💾</i>
              自动保存聊天
            </label>
            <div class="setting-control">
              <div class="toggle-switch" 
                   :class="{ active: localSettings.autoSaveHistory }"
                   @click="toggleSetting('autoSaveHistory')">
                <div class="toggle-circle"></div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 数据管理 -->
        <div class="setting-group">
          <h4 class="group-title">数据管理</h4>
          
          <div class="data-actions">
            <button class="action-btn secondary" @click="exportData">
              <i>📤</i>
              导出数据
            </button>
            <button class="action-btn secondary" @click="importData">
              <i>📥</i>
              导入数据
            </button>
            <button class="action-btn danger" @click="clearData">
              <i>🗑️</i>
              清除数据
            </button>
          </div>
        </div>
        
        <!-- 关于信息 -->
        <div class="setting-group">
          <h4 class="group-title">关于</h4>
          
          <div class="about-info">
            <div class="info-item">
              <span class="info-label">版本</span>
              <span class="info-value">2.0.0</span>
            </div>
            <div class="info-item">
              <span class="info-label">开发者</span>
              <span class="info-value">食慧科技</span>
            </div>
            <div class="info-item">
              <span class="info-label">技术栈</span>
              <span class="info-value">Vue3 + FastAPI + DeepSeek</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 面板底部 -->
      <div class="panel-footer">
        <button class="btn btn-secondary" @click="resetSettings">
          重置设置
        </button>
        <button class="btn btn-primary" @click="saveAndClose">
          保存设置
        </button>
      </div>
      
      <!-- 隐藏的文件输入 -->
      <input 
        ref="fileInput" 
        type="file" 
        accept=".json"
        style="display: none"
        @change="handleFileImport"
      >
    </div>
  </div>
</template>

<script>
/**
 * @description 系统设置面板组件
 * 提供主题、语言、AI设置等功能
 */
export default {
  name: 'SettingsPanel',
  props: {
    settings: {
      type: Object,
      required: true
    }
  },
  emits: ['close', 'updateSettings'],
  data() {
    return {
      localSettings: { ...this.settings }
    }
  },
  watch: {
    settings: {
      handler(newSettings) {
        this.localSettings = { ...newSettings }
      },
      deep: true
    }
  },
  methods: {
    /**
     * @description 更新单个设置项
     */
    updateSetting(key, value) {
      this.localSettings[key] = value
      this.$emit('updateSettings', { [key]: value })
    },
    
    /**
     * @description 切换布尔类型设置
     */
    toggleSetting(key) {
      const newValue = !this.localSettings[key]
      this.updateSetting(key, newValue)
    },
    
    /**
     * @description 重置所有设置为默认值
     */
    resetSettings() {
      if (confirm('确定要重置所有设置吗？此操作不可撤销。')) {
        const defaultSettings = {
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
        }
        
        this.localSettings = { ...defaultSettings }
        this.$emit('updateSettings', defaultSettings)
        this.showToast('设置已重置为默认值')
      }
    },
    
    /**
     * @description 导出用户数据
     */
    exportData() {
      try {
        const data = {
          settings: this.localSettings,
          exportTime: new Date().toISOString(),
          version: '2.0.0'
        }
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { 
          type: 'application/json' 
        })
        
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `hanbon-settings-${new Date().toISOString().slice(0, 10)}.json`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        URL.revokeObjectURL(url)
        
        this.showToast('数据导出成功')
      } catch (error) {
        console.error('导出数据失败:', error)
        this.showToast('导出失败，请重试', 'error')
      }
    },
    
    /**
     * @description 导入用户数据
     */
    importData() {
      this.$refs.fileInput.click()
    },
    
    /**
     * @description 处理文件导入
     */
    async handleFileImport(event) {
      const file = event.target.files[0]
      if (!file) return
      
      try {
        const text = await file.text()
        const data = JSON.parse(text)
        
        if (data.settings) {
          this.localSettings = { ...this.localSettings, ...data.settings }
          this.$emit('updateSettings', data.settings)
          this.showToast('数据导入成功')
        } else {
          throw new Error('无效的数据格式')
        }
      } catch (error) {
        console.error('导入数据失败:', error)
        this.showToast('导入失败，请检查文件格式', 'error')
      }
      
      // 重置文件输入
      event.target.value = ''
    },
    
    /**
     * @description 清除所有数据
     */
    clearData() {
      if (confirm('确定要清除所有本地数据吗？包括设置、聊天记录等。此操作不可撤销！')) {
        try {
          localStorage.clear()
          sessionStorage.clear()
          this.showToast('数据清除成功，页面将刷新')
          
          setTimeout(() => {
            window.location.reload()
          }, 1500)
        } catch (error) {
          console.error('清除数据失败:', error)
          this.showToast('清除失败，请重试', 'error')
        }
      }
    },
    
    /**
     * @description 保存并关闭
     */
    saveAndClose() {
      this.showToast('设置已保存')
      this.$emit('close')
    },
    
    /**
     * @description 显示提示消息
     */
    showToast(message, type = 'success') {
      // 简单的提示实现
      console.log(`${type}: ${message}`)
      
      // 这里可以集成更完善的通知组件
      if (type === 'error') {
        alert(`错误: ${message}`)
      }
    }
  }
}
</script>

<style scoped>
.settings-panel-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999999 !important;
  backdrop-filter: blur(4px);
}

.settings-panel {
  background: var(--background-color);
  border-radius: 16px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 12px 40px var(--shadow-color);
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    transform: scale(0.9) translateY(-20px);
    opacity: 0;
  }
  to {
    transform: scale(1) translateY(0);
    opacity: 1;
  }
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);
  background: var(--surface-color);
}

.panel-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 50%;
  background: var(--border-color);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 18px;
}

.close-btn:hover {
  background: var(--error-color);
  color: white;
}

.settings-content {
  padding: 24px;
  max-height: 60vh;
  overflow-y: auto;
}

.setting-group {
  margin-bottom: 32px;
}

.group-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 20px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid var(--primary-color);
}

.setting-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 0;
  border-bottom: 1px solid var(--border-color);
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-label {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.setting-label .icon {
  font-size: 18px;
  width: 24px;
  text-align: center;
}

.setting-control {
  display: flex;
  align-items: center;
}

.theme-selector {
  display: flex;
  gap: 8px;
}

.theme-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 12px 16px;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  background: var(--surface-color);
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 12px;
}

.theme-option.active {
  border-color: var(--primary-color);
  background: rgba(102, 126, 234, 0.1);
}

.theme-option:hover {
  border-color: var(--primary-color);
}

.setting-select {
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--background-color);
  color: var(--text-primary);
  font-size: 14px;
  min-width: 150px;
}

.setting-input {
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--background-color);
  color: var(--text-primary);
  font-size: 14px;
  width: 80px;
  text-align: center;
}

.toggle-switch {
  width: 48px;
  height: 24px;
  border-radius: 12px;
  background: var(--border-color);
  position: relative;
  transition: all 0.3s ease;
  cursor: pointer;
}

.toggle-switch.active {
  background: var(--primary-color);
}

.toggle-circle {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: white;
  position: absolute;
  top: 2px;
  left: 2px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.toggle-switch.active .toggle-circle {
  left: 26px;
}

.data-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.action-btn.secondary {
  background: var(--surface-color);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.action-btn.secondary:hover {
  background: var(--border-color);
}

.action-btn.danger {
  background: var(--error-color);
  color: white;
}

.action-btn.danger:hover {
  background: #c82333;
}

.about-info {
  background: var(--surface-color);
  border-radius: 8px;
  padding: 16px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid var(--border-color);
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  font-weight: 500;
  color: var(--text-secondary);
}

.info-value {
  color: var(--text-primary);
  font-weight: 600;
}

.panel-footer {
  display: flex;
  justify-content: space-between;
  padding: 20px 24px;
  border-top: 1px solid var(--border-color);
  background: var(--surface-color);
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-secondary {
  background: var(--surface-color);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.btn-secondary:hover {
  background: var(--border-color);
}

.btn-primary {
  background: var(--primary-color);
  color: white;
}

.btn-primary:hover {
  background: var(--secondary-color);
  transform: translateY(-1px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .settings-panel {
    width: 95%;
    max-height: 95vh;
  }
  
  .setting-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .setting-control {
    align-self: stretch;
  }
  
  .theme-selector {
    width: 100%;
    justify-content: space-around;
  }
  
  .data-actions {
    flex-direction: column;
  }
  
  .panel-footer {
    flex-direction: column;
    gap: 12px;
  }
}
</style> 
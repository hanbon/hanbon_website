<template>
  <div class="memory-panel-overlay" @click="$emit('close')">
    <div class="memory-panel" @click.stop>
      <!-- 面板头部 -->
      <div class="panel-header">
        <h3 class="panel-title">
          <i class="icon">🧠</i>
          记忆管理
        </h3>
        <div class="header-actions">
          <!-- 记忆开关 -->
          <div class="memory-toggle">
            <span class="toggle-label">启用记忆</span>
            <div 
              class="toggle-switch" 
              :class="{ active: memoryEnabled }"
              @click="toggleMemory"
            >
              <div class="toggle-circle"></div>
            </div>
          </div>
          <button class="close-btn" @click="$emit('close')">✕</button>
        </div>
      </div>
      
      <!-- 记忆状态指示 -->
      <div class="memory-status">
        <div class="status-item">
          <i class="status-icon">📊</i>
          <span>记忆总数: {{ memories.length }}</span>
        </div>
        <div class="status-item">
          <i class="status-icon">💾</i>
          <span>状态: {{ memoryEnabled ? '已启用' : '已禁用' }}</span>
        </div>
        <div class="status-item">
          <i class="status-icon">🔄</i>
          <span>最后更新: {{ lastUpdateTime }}</span>
        </div>
      </div>
      
      <!-- 记忆搜索 -->
      <div class="memory-search">
        <input 
          v-model="searchQuery"
          type="text"
          placeholder="搜索记忆内容..."
          class="search-input"
          @input="searchMemories"
        >
        <button class="refresh-btn" @click="loadMemories" :disabled="loading">
          <i class="icon" :class="{ rotating: loading }">🔄</i>
        </button>
      </div>
      
      <!-- 记忆列表 -->
      <div class="memory-content">
        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <span>加载记忆中...</span>
        </div>
        
        <div v-else-if="!memoryEnabled" class="disabled-state">
          <i class="state-icon">⏸️</i>
          <p>记忆功能已禁用</p>
          <span>启用记忆功能以保存和查看对话历史</span>
        </div>
        
        <div v-else-if="filteredMemories.length === 0" class="empty-state">
          <i class="state-icon">📝</i>
          <p>{{ searchQuery ? '未找到匹配的记忆' : '暂无记忆记录' }}</p>
          <span>{{ searchQuery ? '尝试其他搜索词' : '开始对话以创建记忆' }}</span>
        </div>
        
        <div v-else class="memory-list">
          <div 
            v-for="memory in filteredMemories"
            :key="memory.id"
            class="memory-item"
            @click="viewMemoryDetail(memory)"
          >
            <div class="memory-header">
              <div class="memory-type">
                <i class="type-icon">{{ getTypeIcon(memory.type) }}</i>
                <span>{{ getTypeName(memory.type) }}</span>
              </div>
              <div class="memory-time">
                {{ formatTime(memory.timestamp) }}
              </div>
            </div>
            
            <div class="memory-preview">
              {{ getMemoryPreview(memory.content) }}
            </div>
            
            <div class="memory-actions">
              <button 
                class="action-btn view" 
                @click.stop="viewMemoryDetail(memory)"
                title="查看详情"
              >
                👁️
              </button>
              <button 
                class="action-btn delete" 
                @click.stop="deleteMemory(memory.id)"
                title="删除记忆"
              >
                🗑️
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 记忆操作 -->
      <div class="memory-operations">
        <button class="operation-btn secondary" @click="exportMemories">
          <i>📤</i>
          导出记忆
        </button>
        <button class="operation-btn danger" @click="clearAllMemories">
          <i>🗑️</i>
          清空记忆
        </button>
      </div>
    </div>
    
    <!-- 记忆详情模态框 -->
    <div v-if="selectedMemory" class="memory-detail-overlay" @click="closeMemoryDetail">
      <div class="memory-detail" @click.stop>
        <div class="detail-header">
          <h4>记忆详情</h4>
          <button class="close-btn" @click="closeMemoryDetail">✕</button>
        </div>
        <div class="detail-content">
          <div class="detail-meta">
            <div class="meta-item">
              <span class="meta-label">类型:</span>
              <span class="meta-value">{{ getTypeName(selectedMemory.type) }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">时间:</span>
              <span class="meta-value">{{ formatFullTime(selectedMemory.timestamp) }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">ID:</span>
              <span class="meta-value">{{ selectedMemory.id }}</span>
            </div>
          </div>
          <div class="detail-body">
            <h5>内容:</h5>
            <pre class="memory-content-detail">{{ JSON.stringify(selectedMemory.content, null, 2) }}</pre>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * @description 记忆管理面板组件
 * 提供记忆查看、搜索、删除、开关控制等功能
 */
export default {
  name: 'MemoryPanel',
  props: {
    memoryEnabled: {
      type: Boolean,
      default: true
    },
    userId: {
      type: String,
      default: 'default'
    }
  },
  emits: ['close', 'toggleMemory', 'memoryUpdated'],
  data() {
    return {
      memories: [],
      filteredMemories: [],
      searchQuery: '',
      loading: false,
      selectedMemory: null,
      lastUpdateTime: '暂无',
      
      typeMap: {
        'conversation': '对话',
        'food_recommendation': '美食推荐', 
        'search_history': '搜索历史',
        'preference': '偏好设置',
        'system': '系统'
      }
    }
  },
  mounted() {
    this.loadMemories()
  },
  methods: {
    /**
     * @description 切换记忆功能开关
     */
    toggleMemory() {
      this.$emit('toggleMemory', !this.memoryEnabled)
    },
    
    /**
     * @description 加载用户记忆
     */
    async loadMemories() {
      if (!this.memoryEnabled) {
        console.log('🔒 记忆功能已禁用，跳过加载')
        return
      }
      
      this.loading = true
      try {
        // 添加超时控制
        const controller = new AbortController()
        const timeoutId = setTimeout(() => controller.abort(), 3000) // 3秒超时
        
        const response = await fetch(`/api/memory/user/${this.userId}`, {
          signal: controller.signal,
          method: 'GET',
          headers: {
            'Content-Type': 'application/json'
          }
        })
        
        clearTimeout(timeoutId)
        
        if (response.ok) {
          const data = await response.json()
          this.memories = data.memories || []
          this.filteredMemories = [...this.memories]
          this.lastUpdateTime = new Date().toLocaleTimeString('zh-CN')
          console.log('✅ 记忆加载成功:', this.memories.length, '条记录')
        } else {
          console.warn('⚠️ 记忆服务返回错误状态:', response.status)
          this.memories = []
          this.filteredMemories = []
        }
      } catch (error) {
        if (error.name === 'AbortError') {
          console.warn('⏰ 记忆加载超时')
        } else if (error instanceof TypeError) {
          console.warn('🔌 记忆服务不可用，使用本地模式')
        } else {
          console.warn('❌ 记忆加载异常:', error.message)
        }
        
        // 在无法连接服务器时，尝试从本地存储加载
        this.loadMemoriesFromLocal()
      } finally {
        this.loading = false
      }
    },
    
    /**
     * @description 从本地存储加载记忆
     */
    loadMemoriesFromLocal() {
      try {
        const localMemories = localStorage.getItem(`hanbon_memories_${this.userId}`)
        if (localMemories) {
          this.memories = JSON.parse(localMemories)
          this.filteredMemories = [...this.memories]
          this.lastUpdateTime = new Date().toLocaleTimeString('zh-CN')
          console.log('📱 从本地存储加载记忆:', this.memories.length, '条记录')
        } else {
          this.memories = []
          this.filteredMemories = []
          console.log('📭 本地暂无记忆记录')
        }
      } catch (error) {
        console.error('❌ 本地记忆加载失败:', error)
        this.memories = []
        this.filteredMemories = []
      }
    },
    
    /**
     * @description 搜索记忆
     */
    searchMemories() {
      if (!this.searchQuery.trim()) {
        this.filteredMemories = [...this.memories]
        return
      }
      
      const query = this.searchQuery.toLowerCase()
      this.filteredMemories = this.memories.filter(memory => {
        const contentStr = JSON.stringify(memory.content).toLowerCase()
        const typeStr = this.getTypeName(memory.type).toLowerCase()
        return contentStr.includes(query) || typeStr.includes(query)
      })
    },
    
    /**
     * @description 查看记忆详情
     */
    viewMemoryDetail(memory) {
      this.selectedMemory = memory
    },
    
    /**
     * @description 关闭记忆详情
     */
    closeMemoryDetail() {
      this.selectedMemory = null
    },
    
    /**
     * @description 删除单个记忆
     */
    async deleteMemory(memoryId) {
      if (!confirm('确定要删除这条记忆吗？')) return
      
      try {
        // 尝试从服务器删除
        const response = await fetch(`/api/memory/${memoryId}`, {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json'
          }
        })
        
        if (response.ok) {
          console.log('✅ 服务器记忆删除成功')
        } else {
          console.warn('⚠️ 服务器记忆删除失败，仅删除本地记录')
        }
      } catch (error) {
        console.warn('🔌 无法连接服务器，仅删除本地记录:', error.message)
      }
      
      // 无论服务器操作是否成功，都删除本地记录
      this.memories = this.memories.filter(m => m.id !== memoryId)
      this.searchMemories() // 重新过滤
      this.saveMemoriesToLocal() // 保存到本地
      this.$emit('memoryUpdated')
      
      console.log('📱 本地记忆删除完成')
    },
    
    /**
     * @description 保存记忆到本地存储
     */
    saveMemoriesToLocal() {
      try {
        localStorage.setItem(`hanbon_memories_${this.userId}`, JSON.stringify(this.memories))
        console.log('💾 记忆已保存到本地存储')
      } catch (error) {
        console.error('❌ 本地记忆保存失败:', error)
      }
    },
    
    /**
     * @description 清空所有记忆
     */
    async clearAllMemories() {
      if (!confirm('确定要清空所有记忆吗？此操作不可撤销！')) return
      
      try {
        // 尝试从服务器批量删除
        for (const memory of this.memories) {
          try {
            await fetch(`/api/memory/${memory.id}`, { 
              method: 'DELETE',
              headers: {
                'Content-Type': 'application/json'
              }
            })
          } catch (error) {
            console.warn('⚠️ 记忆项删除失败:', memory.id, error.message)
          }
        }
        console.log('✅ 服务器记忆清空完成')
      } catch (error) {
        console.warn('🔌 无法连接服务器，仅清空本地记录:', error.message)
      }
      
      // 清空本地记录
      this.memories = []
      this.filteredMemories = []
      this.saveMemoriesToLocal()
      this.$emit('memoryUpdated')
      
      console.log('📱 本地记忆清空完成')
      alert('记忆已清空')
    },
    
    /**
     * @description 导出记忆
     */
    exportMemories() {
      if (this.memories.length === 0) {
        alert('没有记忆可以导出')
        return
      }
      
      try {
        const data = {
          memories: this.memories,
          exportTime: new Date().toISOString(),
          userId: this.userId,
          version: '2.0.0'
        }
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { 
          type: 'application/json' 
        })
        
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `hanbon-memories-${new Date().toISOString().slice(0, 10)}.json`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        URL.revokeObjectURL(url)
        
        alert('记忆导出成功')
      } catch (error) {
        console.error('导出记忆失败:', error)
        alert('导出失败，请重试')
      }
    },
    
    /**
     * @description 获取记忆类型图标
     */
    getTypeIcon(type) {
      const iconMap = {
        'conversation': '💬',
        'food_recommendation': '🍽️',
        'search_history': '🔍',
        'preference': '⚙️',
        'system': '🔧'
      }
      return iconMap[type] || '📝'
    },
    
    /**
     * @description 获取记忆类型名称
     */
    getTypeName(type) {
      return this.typeMap[type] || type
    },
    
    /**
     * @description 获取记忆预览文本
     */
    getMemoryPreview(content) {
      if (typeof content === 'string') {
        return content.length > 100 ? content.substring(0, 100) + '...' : content
      }
      
      if (content.conversation) {
        const text = content.conversation
        return text.length > 100 ? text.substring(0, 100) + '...' : text
      }
      
      if (content.message) {
        const text = content.message
        return text.length > 100 ? text.substring(0, 100) + '...' : text
      }
      
      const str = JSON.stringify(content)
      return str.length > 100 ? str.substring(0, 100) + '...' : str
    },
    
    /**
     * @description 格式化时间
     */
    formatTime(timestamp) {
      const date = new Date(timestamp)
      const now = new Date()
      const diff = now - date
      
      if (diff < 60000) return '刚刚'
      if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
      if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
      if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`
      
      return date.toLocaleDateString('zh-CN')
    },
    
    /**
     * @description 格式化完整时间
     */
    formatFullTime(timestamp) {
      return new Date(timestamp).toLocaleString('zh-CN')
    }
  }
}
</script>

<style scoped>
.memory-panel-overlay {
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

.memory-panel {
  background: var(--background-color);
  border-radius: 16px;
  width: 90%;
  max-width: 700px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 12px 40px var(--shadow-color);
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from { transform: scale(0.9) translateY(-20px); opacity: 0; }
  to { transform: scale(1) translateY(0); opacity: 1; }
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
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.memory-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
}

.toggle-label {
  font-size: 14px;
  color: var(--text-secondary);
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

.memory-status {
  display: flex;
  gap: 20px;
  padding: 16px 24px;
  background: var(--surface-color);
  border-bottom: 1px solid var(--border-color);
}

.status-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: var(--text-secondary);
}

.status-icon {
  font-size: 16px;
}

.memory-search {
  display: flex;
  gap: 12px;
  padding: 16px 24px;
  border-bottom: 1px solid var(--border-color);
}

.search-input {
  flex: 1;
  padding: 10px 16px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--background-color);
  color: var(--text-primary);
  font-size: 14px;
}

.search-input::placeholder {
  color: rgba(0, 0, 0, 0.7);
  opacity: 1;
}

.refresh-btn {
  padding: 10px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--surface-color);
  cursor: pointer;
  transition: all 0.3s ease;
}

.refresh-btn:hover {
  background: var(--border-color);
}

.rotating {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.memory-content {
  flex: 1;
  max-height: 50vh;
  overflow-y: auto;
  padding: 24px;
}

.loading-state, .disabled-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  text-align: center;
  color: var(--text-secondary);
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--border-color);
  border-top: 3px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.state-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.memory-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.memory-item {
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.memory-item:hover {
  border-color: var(--primary-color);
  box-shadow: 0 4px 12px var(--shadow-color);
}

.memory-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.memory-type {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.memory-time {
  font-size: 12px;
  color: var(--text-secondary);
}

.memory-preview {
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 12px;
}

.memory-actions {
  display: flex;
  gap: 8px;
  position: absolute;
  top: 16px;
  right: 16px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.memory-item:hover .memory-actions {
  opacity: 1;
}

.action-btn {
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 12px;
}

.action-btn.view {
  background: var(--primary-color);
  color: white;
}

.action-btn.delete {
  background: var(--error-color);
  color: white;
}

.memory-operations {
  display: flex;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid var(--border-color);
  background: var(--surface-color);
}

.operation-btn {
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

.operation-btn.secondary {
  background: var(--surface-color);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.operation-btn.danger {
  background: var(--error-color);
  color: white;
}

/* 记忆详情模态框 */
.memory-detail-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1001;
}

.memory-detail {
  background: var(--background-color);
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow: hidden;
  box-shadow: 0 8px 32px var(--shadow-color);
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
}

.detail-content {
  padding: 20px;
  max-height: 60vh;
  overflow-y: auto;
}

.detail-meta {
  margin-bottom: 20px;
}

.meta-item {
  display: flex;
  padding: 8px 0;
  border-bottom: 1px solid var(--border-color);
}

.meta-label {
  font-weight: 500;
  width: 80px;
  color: var(--text-secondary);
}

.meta-value {
  color: var(--text-primary);
}

.memory-content-detail {
  background: var(--surface-color);
  padding: 16px;
  border-radius: 8px;
  font-size: 13px;
  line-height: 1.4;
  color: var(--text-primary);
  white-space: pre-wrap;
  word-break: break-word;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .memory-panel {
    width: 95%;
    max-height: 95vh;
  }
  
  .memory-status {
    flex-direction: column;
    gap: 8px;
  }
  
  .header-actions {
    flex-direction: column;
    gap: 8px;
  }
  
  .memory-operations {
    flex-direction: column;
  }
}
</style> 
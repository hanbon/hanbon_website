<template>
  <div class="chat-history-overlay" @click="$emit('close')">
    <div class="chat-history-panel" @click.stop>
      <!-- 面板头部 -->
      <div class="panel-header">
        <h3 class="panel-title">聊天记录</h3>
        <div class="header-actions">
          <button class="search-btn" @click="toggleSearch">
            <i>🔍</i>
          </button>
          <button class="close-btn" @click="$emit('close')">✕</button>
        </div>
      </div>
      
      <!-- 搜索栏 -->
      <div v-if="showSearch" class="search-bar">
        <input 
          v-model="searchQuery"
          placeholder="搜索聊天记录..."
          class="search-input"
          @input="handleSearch"
        >
        <button class="clear-search-btn" @click="clearSearch" v-if="searchQuery">
          <i>✖️</i>
        </button>
      </div>
      
      <!-- 统计信息 -->
      <div class="stats-bar">
        <div class="stat-item">
          <span class="stat-value">{{ filteredHistory.length }}</span>
          <span class="stat-label">条记录</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ totalMessages }}</span>
          <span class="stat-label">总消息</span>
        </div>
        <div class="actions-right">
          <button class="action-btn" @click="exportHistory">
            <i>📤</i> 导出
          </button>
          <button class="action-btn danger" @click="clearAllHistory">
            <i>🗑️</i> 清空
          </button>
        </div>
      </div>
      
      <!-- 历史记录列表 -->
      <div class="history-content">
        <div v-if="filteredHistory.length === 0" class="empty-state">
          <div class="empty-icon">📭</div>
          <h4>{{ searchQuery ? '没有找到相关记录' : '暂无聊天记录' }}</h4>
          <p>{{ searchQuery ? '尝试其他关键词搜索' : '开始与AI对话，记录将显示在这里' }}</p>
        </div>
        
        <div v-else class="history-list">
          <div 
            v-for="chat in filteredHistory"
            :key="chat.id"
            class="history-item"
            @click="loadChat(chat)"
          >
            <div class="chat-preview">
              <div class="chat-title">{{ chat.title }}</div>
              <div class="chat-snippet">{{ chat.snippet }}</div>
              <div class="chat-meta">
                <span class="chat-date">{{ formatDate(chat.timestamp) }}</span>
                <span class="message-count">{{ chat.messageCount }} 条消息</span>
                <div class="tools-used" v-if="chat.toolsUsed && chat.toolsUsed.length">
                  <span 
                    v-for="tool in chat.toolsUsed.slice(0, 3)"
                    :key="tool"
                    class="tool-chip"
                  >
                    {{ getToolName(tool) }}
                  </span>
                  <span v-if="chat.toolsUsed.length > 3" class="more-tools">
                    +{{ chat.toolsUsed.length - 3 }}
                  </span>
                </div>
              </div>
            </div>
            <div class="chat-actions">
              <button 
                class="action-icon"
                @click.stop="shareChat(chat)"
                title="分享"
              >
                <i>📤</i>
              </button>
              <button 
                class="action-icon"
                @click.stop="starChat(chat)"
                title="收藏"
                :class="{ starred: chat.starred }"
              >
                <i>{{ chat.starred ? '⭐' : '☆' }}</i>
              </button>
              <button 
                class="action-icon danger"
                @click.stop="deleteChat(chat)"
                title="删除"
              >
                <i>🗑️</i>
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 分页控制 -->
      <div v-if="totalPages > 1" class="pagination">
        <button 
          class="page-btn"
          @click="currentPage = 1"
          :disabled="currentPage === 1"
        >
          ⏪
        </button>
        <button 
          class="page-btn"
          @click="currentPage--"
          :disabled="currentPage === 1"
        >
          ⬅️
        </button>
        <span class="page-info">
          第 {{ currentPage }} 页，共 {{ totalPages }} 页
        </span>
        <button 
          class="page-btn"
          @click="currentPage++"
          :disabled="currentPage === totalPages"
        >
          ➡️
        </button>
        <button 
          class="page-btn"
          @click="currentPage = totalPages"
          :disabled="currentPage === totalPages"
        >
          ⏩
        </button>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * @description 聊天历史记录组件
 * 提供历史对话查看、搜索、管理功能
 */
export default {
  name: 'ChatHistory',
  emits: ['close', 'loadChat'],
  data() {
    return {
      showSearch: false,
      searchQuery: '',
      currentPage: 1,
      pageSize: 10,
      
      // 模拟的聊天历史数据
      chatHistory: [
        {
          id: 'chat_001',
          title: '推荐川菜',
          snippet: '请推荐一些好吃的川菜，我比较喜欢辣的...',
          timestamp: new Date(Date.now() - 86400000).toISOString(),
          messageCount: 8,
          toolsUsed: ['food_recommendation', 'amap_search'],
          starred: true
        },
        {
          id: 'chat_002',
          title: '宫保鸡丁制作方法',
          snippet: '能教我做宫保鸡丁吗？需要什么食材...',
          timestamp: new Date(Date.now() - 172800000).toISOString(),
          messageCount: 12,
          toolsUsed: ['recipe_generator'],
          starred: false
        },
        {
          id: 'chat_003',
          title: '附近餐厅推荐',
          snippet: '帮我找找附近有什么好吃的餐厅...',
          timestamp: new Date(Date.now() - 259200000).toISOString(),
          messageCount: 6,
          toolsUsed: ['amap_search', 'weather_api'],
          starred: false
        },
        {
          id: 'chat_004',
          title: '营养搭配建议',
          snippet: '这道菜的营养价值如何？有什么搭配建议...',
          timestamp: new Date(Date.now() - 345600000).toISOString(),
          messageCount: 10,
          toolsUsed: ['food_recommendation'],
          starred: true
        },
        {
          id: 'chat_005',
          title: '减肥期间饮食',
          snippet: '减肥期间应该吃什么？有什么低卡美食推荐...',
          timestamp: new Date(Date.now() - 432000000).toISOString(),
          messageCount: 15,
          toolsUsed: ['food_recommendation', 'recipe_generator'],
          starred: false
        }
      ],
      
      // 工具名称映射
      toolsMap: {
        'amap_search': '地图',
        'food_recommendation': '推荐',
        'weather_api': '天气',
        'image_search': '图片',
        'bing_search': '搜索',
        'recipe_generator': '菜谱'
      }
    }
  },
  computed: {
    /**
     * @description 过滤后的历史记录
     */
    filteredHistory() {
      let filtered = this.chatHistory
      
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter(chat => 
          chat.title.toLowerCase().includes(query) ||
          chat.snippet.toLowerCase().includes(query)
        )
      }
      
      // 分页
      const start = (this.currentPage - 1) * this.pageSize
      const end = start + this.pageSize
      return filtered.slice(start, end)
    },
    
    /**
     * @description 总页数
     */
    totalPages() {
      const totalItems = this.searchQuery 
        ? this.chatHistory.filter(chat => 
            chat.title.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
            chat.snippet.toLowerCase().includes(this.searchQuery.toLowerCase())
          ).length
        : this.chatHistory.length
      return Math.ceil(totalItems / this.pageSize)
    },
    
    /**
     * @description 总消息数
     */
    totalMessages() {
      return this.chatHistory.reduce((sum, chat) => sum + chat.messageCount, 0)
    }
  },
  mounted() {
    this.loadHistoryFromStorage()
  },
  methods: {
    /**
     * @description 从本地存储加载历史记录
     */
    loadHistoryFromStorage() {
      try {
        const stored = localStorage.getItem('hanbon_chat_history')
        if (stored) {
          this.chatHistory = JSON.parse(stored)
        }
      } catch (error) {
        console.warn('加载聊天历史失败:', error)
      }
    },
    
    /**
     * @description 切换搜索栏显示
     */
    toggleSearch() {
      this.showSearch = !this.showSearch
      if (!this.showSearch) {
        this.searchQuery = ''
      }
    },
    
    /**
     * @description 处理搜索
     */
    handleSearch() {
      this.currentPage = 1 // 重置到第一页
    },
    
    /**
     * @description 清除搜索
     */
    clearSearch() {
      this.searchQuery = ''
      this.currentPage = 1
    },
    
    /**
     * @description 格式化日期
     */
    formatDate(timestamp) {
      const date = new Date(timestamp)
      const now = new Date()
      const diffInDays = Math.floor((now - date) / (1000 * 60 * 60 * 24))
      
      if (diffInDays === 0) {
        return '今天 ' + date.toLocaleTimeString('zh-CN', { 
          hour: '2-digit', 
          minute: '2-digit' 
        })
      } else if (diffInDays === 1) {
        return '昨天 ' + date.toLocaleTimeString('zh-CN', { 
          hour: '2-digit', 
          minute: '2-digit' 
        })
      } else if (diffInDays < 7) {
        return `${diffInDays}天前`
      } else {
        return date.toLocaleDateString('zh-CN')
      }
    },
    
    /**
     * @description 获取工具名称
     */
    getToolName(tool) {
      return this.toolsMap[tool] || tool
    },
    
    /**
     * @description 加载聊天记录
     */
    loadChat(chat) {
      this.$emit('loadChat', chat)
    },
    
    /**
     * @description 收藏/取消收藏聊天
     */
    starChat(chat) {
      chat.starred = !chat.starred
      this.saveHistoryToStorage()
    },
    
    /**
     * @description 分享聊天记录
     */
    shareChat(chat) {
      const shareText = `分享聊天记录：${chat.title}\n${chat.snippet}\n来自食慧美食AI助手`
      
      if (navigator.share) {
        navigator.share({
          title: chat.title,
          text: shareText
        }).catch(console.error)
      } else {
        // 复制到剪贴板
        navigator.clipboard.writeText(shareText).then(() => {
          alert('聊天记录已复制到剪贴板')
        }).catch(() => {
          alert('分享功能暂不可用')
        })
      }
    },
    
    /**
     * @description 删除聊天记录
     */
    deleteChat(chat) {
      if (confirm(`确定要删除聊天记录"${chat.title}"吗？`)) {
        const index = this.chatHistory.findIndex(item => item.id === chat.id)
        if (index > -1) {
          this.chatHistory.splice(index, 1)
          this.saveHistoryToStorage()
        }
      }
    },
    
    /**
     * @description 导出聊天历史
     */
    exportHistory() {
      try {
        const data = {
          history: this.chatHistory,
          exportTime: new Date().toISOString(),
          version: '2.0.0'
        }
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { 
          type: 'application/json' 
        })
        
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `hanbon-chat-history-${new Date().toISOString().slice(0, 10)}.json`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        URL.revokeObjectURL(url)
        
        alert('聊天历史导出成功')
      } catch (error) {
        console.error('导出失败:', error)
        alert('导出失败，请重试')
      }
    },
    
    /**
     * @description 清空所有历史记录
     */
    clearAllHistory() {
      if (confirm('确定要清空所有聊天记录吗？此操作不可撤销！')) {
        this.chatHistory = []
        this.saveHistoryToStorage()
      }
    },
    
    /**
     * @description 保存历史记录到本地存储
     */
    saveHistoryToStorage() {
      try {
        localStorage.setItem('hanbon_chat_history', JSON.stringify(this.chatHistory))
      } catch (error) {
        console.error('保存聊天历史失败:', error)
      }
    }
  }
}
</script>

<style scoped>
.chat-history-overlay {
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

.chat-history-panel {
  background: var(--background-color);
  border-radius: 16px;
  width: 90%;
  max-width: 800px;
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

.header-actions {
  display: flex;
  gap: 8px;
}

.search-btn, .close-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 50%;
  background: var(--border-color);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
}

.search-btn:hover, .close-btn:hover {
  background: var(--primary-color);
  color: white;
}

.close-btn:hover {
  background: var(--error-color);
}

.search-bar {
  padding: 16px 24px;
  border-bottom: 1px solid var(--border-color);
  background: var(--surface-color);
  display: flex;
  align-items: center;
  gap: 12px;
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

.search-input:focus {
  outline: none;
  border-color: var(--primary-color);
}

.search-input::placeholder {
  color: rgba(0, 0, 0, 0.7);
  opacity: 1;
}

.clear-search-btn {
  width: 24px;
  height: 24px;
  border: none;
  border-radius: 50%;
  background: var(--error-color);
  color: white;
  cursor: pointer;
  font-size: 12px;
}

.stats-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 24px;
  background: var(--surface-color);
  border-bottom: 1px solid var(--border-color);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.stat-value {
  font-size: 16px;
  font-weight: 600;
  color: var(--primary-color);
}

.stat-label {
  font-size: 12px;
  color: var(--text-secondary);
}

.actions-right {
  display: flex;
  gap: 8px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--background-color);
  color: var(--text-primary);
  cursor: pointer;
  font-size: 12px;
  transition: all 0.3s ease;
}

.action-btn:hover {
  background: var(--border-color);
}

.action-btn.danger {
  border-color: var(--error-color);
  color: var(--error-color);
}

.action-btn.danger:hover {
  background: var(--error-color);
  color: white;
}

.history-content {
  max-height: 50vh;
  overflow-y: auto;
  padding: 24px;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-secondary);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-state h4 {
  margin: 0 0 8px 0;
  color: var(--text-primary);
}

.empty-state p {
  margin: 0;
  font-size: 14px;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.history-item {
  display: flex;
  align-items: center;
  padding: 16px;
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.history-item:hover {
  background: var(--background-color);
  border-color: var(--primary-color);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px var(--shadow-color);
}

.chat-preview {
  flex: 1;
}

.chat-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.chat-snippet {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chat-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: var(--text-secondary);
}

.tools-used {
  display: flex;
  gap: 4px;
}

.tool-chip {
  background: var(--primary-color);
  color: white;
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 10px;
}

.more-tools {
  color: var(--text-secondary);
}

.chat-actions {
  display: flex;
  gap: 8px;
}

.action-icon {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 50%;
  background: var(--border-color);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
}

.action-icon:hover {
  background: var(--primary-color);
  color: white;
}

.action-icon.danger:hover {
  background: var(--error-color);
}

.action-icon.starred {
  background: #ffc107;
  color: white;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--border-color);
  background: var(--surface-color);
}

.page-btn {
  width: 32px;
  height: 32px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--background-color);
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.3s ease;
}

.page-btn:hover:not(:disabled) {
  background: var(--primary-color);
  color: white;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: var(--text-secondary);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-history-panel {
    width: 95%;
    max-height: 95vh;
  }
  
  .stats-bar {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .chat-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
  
  .history-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .chat-actions {
    align-self: stretch;
    justify-content: flex-end;
  }
  
  .pagination {
    flex-wrap: wrap;
    gap: 8px;
  }
}
</style> 
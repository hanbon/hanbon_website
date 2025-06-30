<template>
  <div class="tool-panel-overlay" @click="$emit('close')">
    <div class="tool-panel" @click.stop>
      <!-- 面板头部 -->
      <div class="panel-header">
        <h3 class="panel-title">AI工具配置</h3>
        <button class="close-btn" @click="$emit('close')">✕</button>
      </div>
      
      <!-- 工具列表 -->
      <div class="tools-content">
        <div class="tools-grid">
          <div 
            v-for="tool in availableTools"
            :key="tool.id"
            class="tool-card"
            :class="{ active: isToolEnabled(tool.id) }"
            @click="toggleTool(tool.id)"
          >
            <div class="tool-icon">{{ tool.icon }}</div>
            <div class="tool-info">
              <h4 class="tool-name">{{ tool.name }}</h4>
              <p class="tool-description">{{ tool.description }}</p>
              <div class="tool-features">
                <span 
                  v-for="feature in tool.features"
                  :key="feature"
                  class="feature-tag"
                >
                  {{ feature }}
                </span>
              </div>
            </div>
            <div class="tool-toggle">
              <div class="toggle-switch" :class="{ active: isToolEnabled(tool.id) }">
                <div class="toggle-circle"></div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 工具使用统计 -->
        <div class="tool-stats">
          <h4>工具使用统计</h4>
          <div class="stats-grid">
            <div class="stat-item">
              <span class="stat-value">{{ enabledTools.length }}</span>
              <span class="stat-label">已启用工具</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ totalUsage }}</span>
              <span class="stat-label">总使用次数</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ todayUsage }}</span>
              <span class="stat-label">今日使用</span>
            </div>
          </div>
        </div>
        
        <!-- 推荐配置 -->
        <div class="recommended-configs">
          <h4>推荐配置</h4>
          <div class="config-presets">
            <button 
              v-for="preset in presets"
              :key="preset.id"
              class="preset-btn"
              @click="applyPreset(preset)"
            >
              <i>{{ preset.icon }}</i>
              <div>
                <div class="preset-name">{{ preset.name }}</div>
                <div class="preset-desc">{{ preset.description }}</div>
              </div>
            </button>
          </div>
        </div>
      </div>
      
      <!-- 面板底部 -->
      <div class="panel-footer">
        <button class="btn btn-secondary" @click="resetToDefault">
          重置默认
        </button>
        <button class="btn btn-primary" @click="saveAndClose">
          保存设置
        </button>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * @description 工具选择面板组件
 * 允许用户启用/禁用不同的AI工具
 */
export default {
  name: 'ToolPanel',
  props: {
    enabledTools: {
      type: Array,
      default: () => []
    }
  },
  emits: ['close', 'toggleTool'],
  data() {
    return {
      // 可用工具列表
      availableTools: [
        {
          id: 'amap_search',
          name: '高德地图搜索',
          icon: '🗺️',
          description: '搜索附近餐厅、美食地点，获取详细位置信息',
          features: ['位置搜索', '餐厅推荐', '路线规划'],
          category: 'location'
        },
        {
          id: 'food_recommendation',
          name: '智能美食推荐',
          icon: '⭐',
          description: '基于您的偏好和当前情况推荐合适的美食',
          features: ['个性化推荐', '营养分析', '季节搭配'],
          category: 'recommendation'
        },
        {
          id: 'weather_api',
          name: '天气美食助手',
          icon: '🌤️',
          description: '根据天气情况推荐适合的美食和饮品',
          features: ['天气感知', '季节适配', '健康建议'],
          category: 'contextual'
        },
        {
          id: 'recipe_generator',
          name: 'AI菜谱生成',
          icon: '👩‍🍳',
          description: '生成详细的烹饪菜谱和制作步骤',
          features: ['步骤详解', '食材清单', '营养成分'],
          category: 'cooking'
        },
        {
          id: 'image_search',
          name: '美食图片搜索',
          icon: '🖼️',
          description: '搜索美食相关图片，提供视觉参考',
          features: ['图片搜索', '视觉识别', '美食展示'],
          category: 'visual'
        },
        {
          id: 'bing_search',
          name: '网络信息搜索',
          icon: '🔍',
          description: '搜索最新的美食资讯和相关信息',
          features: ['实时信息', '新闻资讯', '趋势分析'],
          category: 'information'
        }
      ],
      
      // 预设配置
      presets: [
        {
          id: 'basic',
          name: '基础配置',
          icon: '🌟',
          description: '适合日常使用的基本工具组合',
          tools: ['food_recommendation', 'recipe_generator']
        },
        {
          id: 'explorer',
          name: '探索配置',
          icon: '🧭',
          description: '发现新美食的完整工具套装',
          tools: ['amap_search', 'food_recommendation', 'image_search', 'bing_search']
        },
        {
          id: 'chef',
          name: '厨师配置',
          icon: '👨‍🍳',
          description: '专注烹饪和制作的工具组合',
          tools: ['recipe_generator', 'food_recommendation', 'weather_api']
        },
        {
          id: 'health',
          name: '健康配置',
          icon: '💚',
          description: '注重营养和健康的工具选择',
          tools: ['food_recommendation', 'weather_api']
        }
      ],
      
      // 模拟使用统计
      totalUsage: 156,
      todayUsage: 12
    }
  },
  methods: {
    /**
     * @description 检查工具是否已启用
     */
    isToolEnabled(toolId) {
      return this.enabledTools.includes(toolId)
    },
    
    /**
     * @description 切换工具状态
     */
    toggleTool(toolId) {
      this.$emit('toggleTool', toolId)
    },
    
    /**
     * @description 应用预设配置
     */
    applyPreset(preset) {
      // 先禁用所有工具
      this.availableTools.forEach(tool => {
        if (this.isToolEnabled(tool.id) && !preset.tools.includes(tool.id)) {
          this.$emit('toggleTool', tool.id)
        }
      })
      
      // 然后启用预设中的工具
      preset.tools.forEach(toolId => {
        if (!this.isToolEnabled(toolId)) {
          this.$emit('toggleTool', toolId)
        }
      })
      
      this.showToast(`已应用 ${preset.name} 配置`)
    },
    
    /**
     * @description 重置为默认配置
     */
    resetToDefault() {
      const defaultTools = ['food_recommendation', 'weather_api']
      
      // 禁用所有非默认工具
      this.availableTools.forEach(tool => {
        const shouldEnable = defaultTools.includes(tool.id)
        const isCurrentlyEnabled = this.isToolEnabled(tool.id)
        
        if (shouldEnable !== isCurrentlyEnabled) {
          this.$emit('toggleTool', tool.id)
        }
      })
      
      this.showToast('已重置为默认配置')
    },
    
    /**
     * @description 保存并关闭
     */
    saveAndClose() {
      this.showToast('工具配置已保存')
      this.$emit('close')
    },
    
    /**
     * @description 显示提示消息
     */
    showToast(message) {
      // 简单的提示实现，实际项目中可以使用更完善的提示组件
      console.log(message)
    }
  }
}
</script>

<style scoped>
.tool-panel-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.tool-panel {
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

.tools-content {
  padding: 24px;
  max-height: 60vh;
  overflow-y: auto;
}

.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}

.tool-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  border: 2px solid var(--border-color);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: var(--surface-color);
}

.tool-card:hover {
  border-color: var(--primary-color);
  transform: translateY(-2px);
  box-shadow: 0 4px 16px var(--shadow-color);
}

.tool-card.active {
  border-color: var(--primary-color);
  background: rgba(102, 126, 234, 0.05);
}

.tool-icon {
  font-size: 32px;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--background-color);
  border-radius: 12px;
  box-shadow: 0 2px 8px var(--shadow-color);
}

.tool-info {
  flex: 1;
}

.tool-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.tool-description {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0 0 12px 0;
  line-height: 1.4;
}

.tool-features {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.feature-tag {
  font-size: 11px;
  padding: 3px 8px;
  background: var(--primary-color);
  color: white;
  border-radius: 10px;
}

.tool-toggle {
  display: flex;
  align-items: center;
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

.tool-stats {
  margin-bottom: 32px;
}

.tool-stats h4 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 16px 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 16px;
}

.stat-item {
  text-align: center;
  padding: 16px;
  background: var(--surface-color);
  border-radius: 12px;
}

.stat-value {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: var(--text-secondary);
}

.recommended-configs h4 {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 16px 0;
}

.config-presets {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.preset-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: left;
}

.preset-btn:hover {
  border-color: var(--primary-color);
  transform: translateY(-1px);
}

.preset-btn i {
  font-size: 20px;
}

.preset-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.preset-desc {
  font-size: 12px;
  color: var(--text-secondary);
}

.panel-footer {
  display: flex;
  justify-content: space-between;
  padding: 20px 24px;
  border-top: 1px solid var(--border-color);
  background: var(--surface-color);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .tool-panel {
    width: 95%;
    max-height: 95vh;
  }
  
  .tools-grid {
    grid-template-columns: 1fr;
  }
  
  .tool-card {
    padding: 16px;
  }
  
  .stats-grid {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .config-presets {
    grid-template-columns: 1fr;
  }
  
  .panel-footer {
    flex-direction: column;
    gap: 12px;
  }
}
</style> 
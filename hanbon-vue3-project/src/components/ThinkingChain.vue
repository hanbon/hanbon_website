<template>
  <div class="thinking-chain" v-if="steps.length > 0" ref="thinkingChain">
    <div class="thinking-header">
      <span class="thinking-icon">🧠</span>
      <span class="thinking-title">AI思维过程</span>
      <button 
        class="collapse-btn"
        @click="toggleCollapse"
        :class="{ collapsed: isCollapsed }"
      >
        {{ isCollapsed ? '展开' : '收起' }}
      </button>
    </div>
    
    <transition name="expand">
      <div v-show="!isCollapsed" class="thinking-content" ref="thinkingContent">
        <div 
          v-for="(step, index) in steps"
          :key="step.step"
          :ref="`step-${step.step}`"
          class="thinking-step"
          :class="[step.status, { 'is-current': index === currentStepIndex }]"
        >
          <div class="step-header">
            <div class="step-number">{{ step.step }}</div>
            <div class="step-info">
              <h4 class="step-title">{{ step.title }}</h4>
              <div class="step-status">
                <span 
                  class="status-indicator"
                  :class="step.status"
                ></span>
                <span class="status-text">{{ getStatusText(step.status) }}</span>
              </div>
            </div>
            <div class="step-icon">
              <span v-if="step.status === 'completed'">✅</span>
              <span v-else-if="step.status === 'processing'" class="spinner">⟳</span>
              <span v-else>⏳</span>
            </div>
          </div>
          
          <div class="step-content" v-if="step.content">
            <div class="content-text" v-html="formatStepContent(step.content)"></div>
          </div>
          
          <!-- 连接线 -->
          <div 
            v-if="index < steps.length - 1" 
            class="step-connector"
            :class="{ active: step.status === 'completed' }"
          ></div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
/**
 * @description 思维链展示组件
 * 显示AI的思考过程和推理步骤
 */
export default {
  name: 'ThinkingChain',
  props: {
    steps: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      isCollapsed: false,
      autoCollapseTimer: null,
      hasShownComplete: false // 追踪是否已显示完成状态
    }
  },
  computed: {
    currentStepIndex() {
      // 找到当前正在处理的步骤索引
      for (let i = this.steps.length - 1; i >= 0; i--) {
        if (this.steps[i].status === 'processing') {
          return i
        }
      }
      // 如果没有processing的步骤，返回最后一个completed的步骤
      for (let i = this.steps.length - 1; i >= 0; i--) {
        if (this.steps[i].status === 'completed') {
          return i
        }
      }
      return -1
    },
    
    /**
     * @description 检查是否所有步骤都已完成
     */
    allStepsCompleted() {
      return this.steps.length > 0 && this.steps.every(step => step.status === 'completed')
    }
  },
  methods: {
    /**
     * @description 切换展开/收起状态
     */
    toggleCollapse() {
      this.isCollapsed = !this.isCollapsed
      // 如果用户手动展开，清除自动收起定时器
      if (!this.isCollapsed && this.autoCollapseTimer) {
        clearTimeout(this.autoCollapseTimer)
        this.autoCollapseTimer = null
      }
    },
    
    /**
     * @description 自动收起思维链（在完成后）
     */
    autoCollapse() {
      if (this.autoCollapseTimer) {
        clearTimeout(this.autoCollapseTimer)
      }
      
      console.log('🕐 设置思维链自动收起定时器')
      
      // 延迟4秒后自动收起，让用户有时间查看完成状态
      this.autoCollapseTimer = setTimeout(() => {
        if (this.allStepsCompleted && !this.hasProcessingStep()) {
          console.log('✅ 自动收起思维链')
          this.isCollapsed = true
        } else {
          console.log('⚠️ 思维链状态已变化，取消自动收起')
        }
        this.autoCollapseTimer = null
      }, 4000)
    },
    
    /**
     * @description 重置收起状态（开始新对话时）
     */
    resetCollapse() {
      this.isCollapsed = false
      this.hasShownComplete = false
      if (this.autoCollapseTimer) {
        clearTimeout(this.autoCollapseTimer)
        this.autoCollapseTimer = null
      }
    },
    
    /**
     * @description 获取状态文本
     */
    getStatusText(status) {
      const statusMap = {
        'pending': '等待中',
        'processing': '思考中',
        'completed': '已完成',
        'error': '出错了'
      }
      return statusMap[status] || '未知状态'
    },
    
    /**
     * @description 格式化步骤内容
     */
    formatStepContent(content) {
      if (!content) return ''
      
      // 处理换行
      let formatted = content.replace(/\n/g, '<br>')
      
      // 处理列表项
      formatted = formatted.replace(/^•\s/gm, '<span class="bullet">•</span> ')
      
      // 处理粗体文本
      formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      
      // 处理斜体文本
      formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>')
      
      return formatted
    },

    /**
     * @description 滚动到当前步骤
     */
    scrollToCurrentStep() {
      if (this.isCollapsed) return
      
      this.$nextTick(() => {
        const currentIndex = this.currentStepIndex
        if (currentIndex >= 0) {
          const stepRef = this.$refs[`step-${this.steps[currentIndex].step}`]
          if (stepRef && stepRef[0]) {
            stepRef[0].scrollIntoView({
              behavior: 'smooth',
              block: 'center'
            })
          }
        } else if (this.steps.length > 0) {
          // 如果没有当前步骤，滚动到最后一个步骤
          const lastStep = this.steps[this.steps.length - 1]
          const stepRef = this.$refs[`step-${lastStep.step}`]
          if (stepRef && stepRef[0]) {
            stepRef[0].scrollIntoView({
              behavior: 'smooth',
              block: 'center'
            })
          }
        }
      })
    },

    /**
     * @description 滚动到思维链组件
     */
    scrollToThinkingChain() {
      if (this.$refs.thinkingChain) {
        this.$refs.thinkingChain.scrollIntoView({
          behavior: 'smooth',
          block: 'nearest'
        })
      }
    },

    /**
     * @description 检查是否有步骤正在处理
     */
    hasProcessingStep() {
      return this.steps.some(step => step.status === 'processing')
    },

    /**
     * @description 检查步骤是否有更新
     */
    hasStepUpdated(newSteps, oldSteps) {
      if (!oldSteps || newSteps.length !== oldSteps.length) {
        return false
      }
      
      for (let i = 0; i < newSteps.length; i++) {
        const newStep = newSteps[i]
        const oldStep = oldSteps[i]
        
        if (!oldStep) continue
        
        // 检查状态、标题或内容是否发生变化
        if (newStep.status !== oldStep.status || 
            newStep.title !== oldStep.title || 
            newStep.content !== oldStep.content) {
          return true
        }
      }
      
      return false
    }
  },
  watch: {
    steps: {
      handler(newSteps, oldSteps) {
        // 当步骤数量从0变为有值时，重置状态并展开
        if (oldSteps && oldSteps.length === 0 && newSteps.length > 0) {
          this.resetCollapse()
          // 新对话开始时滚动到思维链
          this.$nextTick(() => {
            this.scrollToThinkingChain()
          })
        }
        
        // 当有新步骤时，自动展开
        if (newSteps.length > 0 && this.isCollapsed) {
          this.isCollapsed = false
        }
        
        // 检测步骤变化并滚动到当前步骤
        if (newSteps.length > 0) {
          const hasNewStep = !oldSteps || newSteps.length > oldSteps.length
          const hasUpdatedStep = oldSteps && this.hasStepUpdated(newSteps, oldSteps)
          
          if (hasNewStep || hasUpdatedStep) {
            // 延迟滚动，确保DOM更新完成
            this.$nextTick(() => {
              setTimeout(() => {
                this.scrollToCurrentStep()
              }, 100)
            })
          }
        }
        
        // 检查是否所有步骤都完成了且没有处理中的步骤
        if (this.allStepsCompleted && !this.hasProcessingStep() && !this.hasShownComplete) {
          this.hasShownComplete = true
          console.log('🎯 思维链完成，准备自动收起')
          // 触发自动收起
          this.autoCollapse()
        }
        
        // 如果还有处理中的步骤，重置完成状态
        if (this.hasProcessingStep() && this.hasShownComplete) {
          this.hasShownComplete = false
          // 清除自动收起定时器
          if (this.autoCollapseTimer) {
            clearTimeout(this.autoCollapseTimer)
            this.autoCollapseTimer = null
          }
        }
      },
      deep: true
    }
  },
  
  beforeUnmount() {
    // 清理定时器
    if (this.autoCollapseTimer) {
      clearTimeout(this.autoCollapseTimer)
    }
  }
}
</script>

<style scoped>
.thinking-chain {
  margin: 16px 0;
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.thinking-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  cursor: pointer;
}

.thinking-icon {
  font-size: 18px;
}

.thinking-title {
  flex: 1;
  font-weight: 600;
  font-size: 16px;
}

.collapse-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.3s ease;
}

.collapse-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.collapse-btn.collapsed {
  background: rgba(255, 255, 255, 0.3);
}

.thinking-content {
  padding: 20px;
}

.thinking-step {
  position: relative;
  margin-bottom: 24px;
}

.thinking-step:last-child {
  margin-bottom: 0;
}

.thinking-step.is-current {
  animation: pulse 2s infinite;
}

.step-header {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 12px;
}

.step-number {
  width: 32px;
  height: 32px;
  background: var(--primary-color);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
  flex-shrink: 0;
}

.thinking-step.completed .step-number {
  background: #10b981;
}

.thinking-step.processing .step-number {
  background: #f59e0b;
  animation: glow 2s infinite;
}

.thinking-step.error .step-number {
  background: #ef4444;
}

.step-info {
  flex: 1;
}

.step-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 6px 0;
}

.step-status {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #e5e7eb;
}

.status-indicator.pending {
  background: #e5e7eb;
}

.status-indicator.processing {
  background: #f59e0b;
  animation: blink 1.5s infinite;
}

.status-indicator.completed {
  background: #10b981;
}

.status-indicator.error {
  background: #ef4444;
}

.status-text {
  font-size: 12px;
  color: var(--text-secondary);
}

.step-icon {
  font-size: 20px;
  width: 24px;
  text-align: center;
}

.spinner {
  display: inline-block;
  animation: spin 1s linear infinite;
}

.step-content {
  margin-left: 48px;
  padding: 16px;
  background: var(--background-color);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  border-left: 3px solid var(--primary-color);
}

.thinking-step.completed .step-content {
  border-left-color: #10b981;
}

.thinking-step.processing .step-content {
  border-left-color: #f59e0b;
}

.thinking-step.error .step-content {
  border-left-color: #ef4444;
}

.content-text {
  color: var(--text-primary);
  line-height: 1.6;
  font-size: 14px;
}

.content-text .bullet {
  color: var(--primary-color);
  font-weight: bold;
  margin-right: 4px;
}

.step-connector {
  position: absolute;
  left: 15px;
  top: 48px;
  width: 2px;
  height: 24px;
  background: #e5e7eb;
  transition: all 0.3s ease;
}

.step-connector.active {
  background: #10b981;
}

/* 动画效果 */
.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  max-height: 0;
  opacity: 0;
}

.expand-enter-to,
.expand-leave-from {
  max-height: 1000px;
  opacity: 1;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.02);
  }
}

@keyframes glow {
  0%, 100% {
    box-shadow: 0 0 5px rgba(245, 158, 11, 0.5);
  }
  50% {
    box-shadow: 0 0 20px rgba(245, 158, 11, 0.8);
  }
}

@keyframes blink {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.3;
  }
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .thinking-content {
    padding: 16px;
  }
  
  .step-header {
    gap: 12px;
  }
  
  .step-content {
    margin-left: 40px;
    padding: 12px;
  }
  
  .step-connector {
    left: 19px;
  }
}
</style> 
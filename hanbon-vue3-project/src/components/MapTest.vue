<template>
  <div class="map-test-container">
    <!-- 地图测试头部 -->
    <div class="test-header">
      <h2 class="test-title">
        <span class="title-icon">🗺️</span>
        地图功能测试
      </h2>
      <p class="test-description">测试高德地图组件的基本功能</p>
    </div>

    <!-- 控制面板 -->
    <div class="control-panel">
      <button @click="testBasicMap" class="test-btn primary">
        📍 基础地图
      </button>
      <button @click="testWithLocations" class="test-btn secondary">
        🍽️ 带餐厅数据
      </button>
      <button @click="testEmptyMap" class="test-btn secondary">
        🔄 清空数据
      </button>
      <button @click="checkApiKey" class="test-btn info">
        🔑 检查API密钥
      </button>
    </div>

    <!-- 状态显示 -->
    <div class="status-panel">
      <div class="status-item">
        <span class="status-label">API密钥状态:</span>
        <span class="status-value" :class="apiKeyStatus.class">
          {{ apiKeyStatus.text }}
        </span>
      </div>
      <div class="status-item">
        <span class="status-label">地图状态:</span>
        <span class="status-value" :class="mapStatus.class">
          {{ mapStatus.text }}
        </span>
      </div>
    </div>

    <!-- 地图容器 -->
    <div class="map-container">
      <AmapDisplay 
        :locations="testLocations"
        :title="mapTitle"
        @locationChange="handleLocationChange"
        @markerClick="handleMarkerClick"
        style="height: 500px;"
        class="test-map"
        ref="testMap"
      />
    </div>

    <!-- 调试信息 -->
    <div class="debug-panel" v-if="debugMode">
      <h3 class="debug-title">调试信息</h3>
      <div class="debug-content">
        <div class="debug-item">
          <strong>测试位置数据:</strong>
          <pre>{{ JSON.stringify(testLocations, null, 2) }}</pre>
        </div>
        <div class="debug-item" v-if="lastLocationChange">
          <strong>最后位置变化:</strong>
          <pre>{{ JSON.stringify(lastLocationChange, null, 2) }}</pre>
        </div>
      </div>
    </div>

    <!-- 切换调试模式 -->
    <div class="debug-toggle">
      <button @click="debugMode = !debugMode" class="debug-btn">
        {{ debugMode ? '🙈 隐藏调试' : '🐛 显示调试' }}
      </button>
    </div>
  </div>
</template>

<script>
import AmapDisplay from './AmapDisplay.vue'

/**
 * @description 地图测试组件
 * 用于测试AmapDisplay组件的各种功能
 */
export default {
  name: 'MapTest',
  components: {
    AmapDisplay
  },
  data() {
    return {
      debugMode: false,
      mapTitle: '地图测试',
      testLocations: [],
      lastLocationChange: null,
      apiKeyStatus: {
        text: '检查中...',
        class: 'checking'
      },
      mapStatus: {
        text: '初始化中...',
        class: 'loading'
      }
    }
  },
  mounted() {
    this.checkApiKey()
    this.testBasicMap()
  },
  methods: {
    /**
     * @description 测试基础地图（无餐厅数据）
     */
    testBasicMap() {
      this.testLocations = []
      this.mapTitle = '基础地图测试'
      this.mapStatus = {
        text: '显示基础地图',
        class: 'success'
      }
      console.log('🗺️ 测试基础地图')
    },

    /**
     * @description 测试带餐厅数据的地图
     */
    testWithLocations() {
      this.testLocations = [
        {
          id: 1,
          name: '湘菜馆',
          address: '湖南省长沙市天心区解放西路123号',
          coordinates: [112.982279, 28.194090],
          rating: '4.5',
          distance: '500m',
          tel: '0731-12345678',
          tags: ['湘菜', '辣味', '招牌菜']
        },
        {
          id: 2,
          name: '川菜小馆',
          address: '湖南省长沙市岳麓区桐梓坡路456号',
          coordinates: [112.975000, 28.200000],
          rating: '4.3',
          distance: '1.2km',
          tel: '0731-87654321',
          tags: ['川菜', '麻辣', '火锅']
        },
        {
          id: 3,
          name: '粤菜酒楼',
          address: '湖南省长沙市雨花区劳动中路789号',
          coordinates: [112.990000, 28.180000],
          rating: '4.7',
          distance: '800m',
          tel: '0731-11223344',
          tags: ['粤菜', '茶点', '海鲜']
        }
      ]
      this.mapTitle = '附近餐厅（测试数据）'
      this.mapStatus = {
        text: '显示餐厅数据',
        class: 'success'
      }
      console.log('🍽️ 测试餐厅数据地图')
    },

    /**
     * @description 清空测试数据
     */
    testEmptyMap() {
      this.testLocations = []
      this.mapTitle = '空数据测试'
      this.mapStatus = {
        text: '无餐厅数据',
        class: 'warning'
      }
      console.log('🔄 清空测试数据')
    },

    /**
     * @description 检查API密钥状态
     */
    checkApiKey() {
      try {
        // 检查全局配置
        if (window.APP_CONFIG && window.APP_CONFIG.AMAP_KEY) {
          const key = window.APP_CONFIG.AMAP_KEY
          if (key && key !== '请在这里输入您的高德地图API密钥' && key.length > 10) {
            this.apiKeyStatus = {
              text: `已配置 (${key.substring(0, 8)}...)`,
              class: 'success'
            }
          } else {
            this.apiKeyStatus = {
              text: '密钥无效',
              class: 'error'
            }
          }
        } else {
          this.apiKeyStatus = {
            text: '未找到配置',
            class: 'error'
          }
        }
      } catch (error) {
        this.apiKeyStatus = {
          text: '检查失败',
          class: 'error'
        }
      }
    },

    /**
     * @description 处理位置变化
     */
    handleLocationChange(locationData) {
      this.lastLocationChange = locationData
      console.log('📍 位置变化:', locationData)
    },

    /**
     * @description 处理标记点击
     */
    handleMarkerClick(markerData) {
      console.log('🎯 标记点击:', markerData)
      alert(`点击了: ${markerData.name || '标记'}`)
    }
  }
}
</script>

<style scoped>
.map-test-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.test-header {
  text-align: center;
  margin-bottom: 30px;
}

.test-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.title-icon {
  font-size: 32px;
}

.test-description {
  font-size: 16px;
  color: var(--text-secondary);
  margin: 0;
}

.control-panel {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.test-btn {
  padding: 12px 20px;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.test-btn.primary {
  background: linear-gradient(135deg, #6C63FF 0%, #86A8E7 100%);
  color: white;
}

.test-btn.secondary {
  background: rgba(108, 99, 255, 0.1);
  color: var(--primary-color);
  border: 1px solid rgba(108, 99, 255, 0.2);
}

.test-btn.info {
  background: rgba(52, 152, 219, 0.1);
  color: #3498db;
  border: 1px solid rgba(52, 152, 219, 0.2);
}

.test-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.status-panel {
  display: flex;
  gap: 20px;
  justify-content: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid var(--border-color);
  border-radius: 20px;
}

.status-label {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
}

.status-value {
  font-size: 14px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 8px;
}

.status-value.success {
  background: rgba(76, 175, 80, 0.1);
  color: #4caf50;
}

.status-value.error {
  background: rgba(244, 67, 54, 0.1);
  color: #f44336;
}

.status-value.warning {
  background: rgba(255, 152, 0, 0.1);
  color: #ff9800;
}

.status-value.checking,
.status-value.loading {
  background: rgba(108, 99, 255, 0.1);
  color: var(--primary-color);
}

.map-container {
  margin: 20px 0;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(108, 99, 255, 0.1);
  border: 1px solid var(--border-color);
}

.test-map {
  width: 100%;
}

.debug-panel {
  margin-top: 20px;
  padding: 20px;
  background: rgba(248, 249, 250, 0.8);
  border: 1px solid var(--border-color);
  border-radius: 12px;
}

.debug-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 16px 0;
}

.debug-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.debug-item {
  background: white;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.debug-item strong {
  display: block;
  margin-bottom: 8px;
  color: var(--text-primary);
}

.debug-item pre {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 6px;
  font-size: 12px;
  overflow-x: auto;
  margin: 0;
}

.debug-toggle {
  text-align: center;
  margin-top: 20px;
}

.debug-btn {
  padding: 8px 16px;
  border: 1px solid var(--border-color);
  background: white;
  color: var(--text-secondary);
  border-radius: 20px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.3s ease;
}

.debug-btn:hover {
  background: var(--background-color);
  color: var(--text-primary);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .map-test-container {
    padding: 16px;
  }
  
  .test-title {
    font-size: 24px;
  }
  
  .control-panel {
    gap: 8px;
  }
  
  .test-btn {
    padding: 10px 16px;
    font-size: 13px;
  }
  
  .status-panel {
    flex-direction: column;
    align-items: center;
  }
  
  .debug-item pre {
    font-size: 11px;
  }
}
</style> 
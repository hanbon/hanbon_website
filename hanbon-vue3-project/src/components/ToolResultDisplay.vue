<template>
  <div class="tool-result-display">
    <!-- 图片画廊展示 -->
    <div v-if="displayType === 'image_gallery'" class="result-container image-gallery">
      <div class="result-header">
        <span class="tool-icon">📷</span>
        <span class="tool-title">图片搜索结果</span>
        <span class="result-count">{{ loadedImagesCount }} 张图片</span>
      </div>
      
      <div class="image-grid" :class="`columns-${displayConfig.columns || 3}`">
        <div 
          v-for="(image, index) in visibleImages"
          :key="index"
          class="image-item"
          :class="{ 'loading': imageLoadingStates[index] === 'loading', 'error': imageLoadingStates[index] === 'error' }"
          @click="showImageModal(image, index)"
          v-show="imageLoadingStates[index] !== 'error'"
        >
          <img 
            :src="image.thumbnailUrl || image.url" 
            :alt="`美食图片 ${index + 1}`"
            :loading="displayConfig.lazy_load ? 'lazy' : 'eager'"
            @load="handleImageLoad(index)"
            @error="handleImageError(index)"
            :data-index="index"
          />
          <div class="image-overlay" v-show="imageLoadingStates[index] === 'loaded'">
            <span class="view-icon">🔍</span>
          </div>
          <div class="image-loading" v-show="imageLoadingStates[index] === 'loading'">
            <div class="loading-spinner"></div>
          </div>
        </div>
      </div>
      
      <div v-if="hasMoreImages" class="show-more">
        <button @click="showMoreImages" class="show-more-btn">
          查看更多图片 ({{ remainingImagesCount }})
        </button>
      </div>
      
      <!-- 显示加载统计信息 -->
      <div v-if="showLoadingStats" class="loading-stats">
        <span class="stats-text">
          {{ loadedImagesCount }} 张成功加载，{{ failedImagesCount }} 张加载失败
        </span>
      </div>
    </div>

    <!-- 美食推荐卡片 -->
    <div v-else-if="displayType === 'recommendation_cards'" class="result-container recommendation-cards">
      <div class="result-header">
        <span class="tool-icon">⭐</span>
        <span class="tool-title">美食推荐</span>
        <span class="result-count">{{ displayData.total_count || 0 }} 个推荐</span>
      </div>
      
      <!-- 分类筛选 -->
      <div v-if="displayData.categories && displayData.categories.length > 1" class="category-filter">
        <button 
          v-for="category in ['全部', ...(displayData.categories || [])]"
          :key="category"
          class="category-btn"
          :class="{ active: selectedCategory === category }"
          @click="filterByCategory(category)"
        >
          {{ category }}
        </button>
      </div>
      
      <div class="recommendation-grid">
        <div 
          v-for="recommendation in filteredRecommendations"
          :key="recommendation.dish_name"
          class="recommendation-card"
          @click="selectRecommendation(recommendation)"
        >
          <div class="card-header">
            <h4 class="dish-name">{{ recommendation.dish_name }}</h4>
            <span class="category-tag">{{ recommendation.category }}</span>
          </div>
          
          <div class="card-content">
            <p class="reason">{{ recommendation.reason }}</p>
            
            <div class="card-stats">
              <div class="stat-item">
                <span class="stat-icon">⏱️</span>
                <span class="stat-text">{{ recommendation.cooking_time }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-icon">📊</span>
                <span class="stat-text">{{ recommendation.difficulty }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-icon">💯</span>
                <span class="stat-text">{{ recommendation.nutrition_score }}分</span>
              </div>
            </div>
            
            <div class="ingredients-preview">
              <span class="ingredients-label">主要食材：</span>
              <span class="ingredients-text">
                {{ (recommendation.ingredients || []).slice(0, 3).join('、') }}
                <span v-if="(recommendation.ingredients || []).length > 3">等</span>
              </span>
            </div>
          </div>
          
          <div class="card-actions">
            <button @click.stop="getRecipe(recommendation.dish_name)" class="action-btn primary">
              📖 查看菜谱
            </button>
            <button @click.stop="searchImages(recommendation.dish_name)" class="action-btn secondary">
              📷 看图片
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 详细菜谱展示 -->
    <div v-else-if="displayType === 'recipe_detailed'" class="result-container recipe-detailed">
      <div class="result-header">
        <span class="tool-icon">👨‍🍳</span>
        <span class="tool-title">{{ (displayData.recipe || {}).dish_name || '菜谱详情' }}</span>
        <div class="header-actions">
          <button @click="printRecipe" class="action-btn">🖨️ 打印</button>
          <button @click="saveRecipe" class="action-btn">💾 保存</button>
        </div>
      </div>
      
      <!-- 菜谱基本信息 -->
      <div class="recipe-metadata">
        <div class="meta-item">
          <span class="meta-label">准备时间</span>
          <span class="meta-value">{{ (displayData.metadata || {}).prep_time || '未知' }}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">烹饪时间</span>
          <span class="meta-value">{{ (displayData.metadata || {}).cook_time || '未知' }}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">难度等级</span>
          <span class="meta-value">{{ (displayData.metadata || {}).difficulty || '未知' }}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">份数</span>
          <span class="meta-value">{{ (displayData.metadata || {}).serving_size || '未知' }}</span>
        </div>
      </div>
      
      <!-- 食材清单 -->
      <div class="recipe-section">
        <h4 class="section-title">🥘 食材清单</h4>
        <div class="ingredients-grid">
          <div 
            v-for="ingredient in ((displayData.recipe || {}).ingredients || [])"
            :key="ingredient.name"
            class="ingredient-item"
          >
            <span class="ingredient-name">{{ ingredient.name }}</span>
            <span class="ingredient-amount">{{ ingredient.amount }} {{ ingredient.unit }}</span>
          </div>
        </div>
      </div>
      
      <!-- 制作步骤 -->
      <div class="recipe-section">
        <h4 class="section-title">📝 制作步骤</h4>
        <div class="steps-list">
          <div 
            v-for="step in ((displayData.recipe || {}).steps || [])"
            :key="step.step_number"
            class="step-item"
          >
            <div class="step-number">{{ step.step_number }}</div>
            <div class="step-content">
              <p class="step-instruction">{{ step.instruction }}</p>
              <div v-if="step.time" class="step-time">⏱️ {{ step.time }}</div>
              <div v-if="step.tips" class="step-tips">💡 {{ step.tips }}</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 营养信息 -->
      <div v-if="(displayData.recipe || {}).nutrition" class="recipe-section">
        <h4 class="section-title">🍃 营养信息</h4>
        <div class="nutrition-grid">
          <div 
            v-for="(value, key) in (((displayData.recipe || {}).nutrition || {}).per_serving || {})"
            :key="key"
            class="nutrition-item"
          >
            <span class="nutrition-label">{{ getNutritionLabel(key) }}</span>
            <span class="nutrition-value">{{ value }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 位置搜索结果 -->
    <div v-else-if="displayType === 'location_list'" class="result-container location-list">
      <div class="result-header">
        <span class="tool-icon">📍</span>
        <span class="tool-title">附近餐厅</span>
        <span class="result-count">找到 {{ displayData.total_found || displayData.locations?.length || 0 }} 家</span>
        
        <!-- 视图切换按钮 -->
        <div class="view-toggle">
          <button 
            @click="mapViewMode = 'map'" 
            :class="{ active: mapViewMode === 'map' }"
            class="view-btn"
            title="地图视图"
          >
            🗺️
          </button>
          <button 
            @click="mapViewMode = 'list'" 
            :class="{ active: mapViewMode === 'list' }"
            class="view-btn"
            title="列表视图"
          >
            📋
          </button>
        </div>
      </div>
      
      <!-- 地图视图 -->
      <div v-if="mapViewMode === 'map'">
        <AmapDisplay 
          :locations="displayData.locations || []"
          :title="getMapTitle()"
          @locationChange="handleLocationChange"
          @markerClick="handleMarkerClick"
          style="min-height: 400px;"
          class="map-display-container"
          ref="amapDisplay"
        />
        
        <!-- 地图下方的简要信息 -->
        <div class="map-summary">
          <div class="summary-info">
            <span class="info-item">
              📍 {{ getLocationSummary() }}
            </span>
            <span class="info-item" v-if="displayData.search_query">
              🔍 搜索: {{ displayData.search_query }}
            </span>
            <span class="info-item" v-if="!hasLocations()">
              🎯 点击"我的位置"开始探索
            </span>
          </div>
          <div class="map-actions">
            <button @click="refreshMap" class="action-btn small">
              🔄 刷新地图
            </button>
            <button @click="showAllMarkers" class="action-btn small" v-if="hasLocations()">
              🗺️ 显示全部
            </button>
            <button @click="searchNearbyRestaurants" class="action-btn small" v-if="!hasLocations()">
              🍽️ 搜索附近餐厅
            </button>
          </div>
        </div>
      </div>
      
      <!-- 列表视图 -->
      <div v-else-if="mapViewMode === 'list' && displayData.locations && displayData.locations.length > 0" class="location-items">
        <div 
          v-for="(location, index) in displayData.locations"
          :key="location.id || index"
          class="location-item"
        >
          <div class="location-info">
            <h4 class="location-name">{{ location.name }}</h4>
            <p class="location-address">{{ location.address }}</p>
            <div class="location-meta">
              <span v-if="location.distance" class="meta-item distance">
                📏 {{ location.distance }}
              </span>
              <span v-if="location.rating && location.rating !== '暂无评分'" class="meta-item rating">
                ⭐ {{ location.rating }}
              </span>
              <span v-if="location.price_level" class="meta-item price">
                💰 {{ location.price_level }}
              </span>
              <span v-if="location.tel" class="meta-item phone">
                📞 {{ location.tel }}
              </span>
            </div>
            
            <!-- 标签显示 -->
            <div v-if="location.tags && location.tags.length > 0" class="location-tags">
              <span 
                v-for="tag in location.tags.slice(0, 3)" 
                :key="tag" 
                class="tag"
              >
                {{ tag }}
              </span>
            </div>
          </div>
          
          <div class="location-actions">
            <a 
              v-if="location.map_url" 
              :href="location.map_url" 
              target="_blank" 
              class="action-btn map-btn"
              title="在高德地图中查看"
            >
              🗺️ 导航
            </a>
            <a 
              v-if="location.tel" 
              :href="`tel:${location.tel}`" 
              class="action-btn call-btn"
              title="拨打电话"
            >
              📞 电话
            </a>
            <button 
              @click="searchNearbyImages(location.name)"
              class="action-btn image-btn"
              title="查看图片"
            >
              📷 图片
            </button>
          </div>
        </div>
      </div>
      
      <!-- 空状态显示 -->
      <div v-else class="empty-state">
        <div class="empty-icon">🔍</div>
        <p class="empty-message">未找到相关餐厅</p>
        <p class="empty-suggestion">请尝试其他关键词或地点</p>
      </div>
    </div>

    <!-- 天气卡片 -->
    <div v-else-if="displayType === 'weather_card'" class="result-container weather-card">
      <!-- 天气卡片头部 -->
      <div class="weather-header">
        <div class="header-left">
          <div class="weather-icon-large">
            {{ getWeatherIcon((displayData.weather || {}).description) }}
          </div>
          <div class="location-info">
            <h3 class="city-name">{{ formatCityName(displayData.city) || '未知城市' }}</h3>
            <p class="update-time">{{ (displayData.weather || {}).report_time || '当前' }}</p>
          </div>
        </div>
        <div class="header-right">
          <div class="temperature-display">
            <span class="temperature-value">{{ extractTemperature((displayData.weather || {}).temperature) }}</span>
            <span class="temperature-unit">°C</span>
          </div>
        </div>
      </div>
      
      <!-- 天气详细信息 -->
      <div class="weather-details-grid">
        <div class="weather-detail-card">
          <div class="detail-icon">🌡️</div>
          <div class="detail-content">
            <span class="detail-label">体感温度</span>
            <span class="detail-value">{{ (displayData.weather || {}).feels_like || '--' }}</span>
          </div>
        </div>
        
        <div class="weather-detail-card">
          <div class="detail-icon">💧</div>
          <div class="detail-content">
            <span class="detail-label">湿度</span>
            <span class="detail-value">{{ (displayData.weather || {}).humidity || '--' }}</span>
          </div>
        </div>
        
        <div class="weather-detail-card">
          <div class="detail-icon">💨</div>
          <div class="detail-content">
            <span class="detail-label">风力</span>
            <span class="detail-value">{{ (displayData.weather || {}).wind_power || '--' }}</span>
          </div>
        </div>
        
        <div class="weather-detail-card">
          <div class="detail-icon">🧭</div>
          <div class="detail-content">
            <span class="detail-label">风向</span>
            <span class="detail-value">{{ (displayData.weather || {}).wind_direction || '--' }}</span>
          </div>
        </div>
        
        <div class="weather-detail-card" v-if="(displayData.weather || {}).pressure">
          <div class="detail-icon">🌪️</div>
          <div class="detail-content">
            <span class="detail-label">气压</span>
            <span class="detail-value">{{ (displayData.weather || {}).pressure || '--' }}</span>
          </div>
        </div>
        
        <div class="weather-detail-card" v-if="(displayData.weather || {}).visibility">
          <div class="detail-icon">👁️</div>
          <div class="detail-content">
            <span class="detail-label">能见度</span>
            <span class="detail-value">{{ (displayData.weather || {}).visibility || '--' }}</span>
          </div>
        </div>
      </div>
      
      <!-- 天气描述 -->
      <div class="weather-description">
        <p class="description-text">
          <span class="description-icon">📝</span>
          {{ (displayData.weather || {}).description || '暂无天气描述' }}
        </p>
      </div>
      
      <!-- 美食建议卡片 -->
      <div class="food-suggestions-section">
        <div class="suggestions-header">
          <h4 class="suggestions-title">
            <span class="title-icon">🍽️</span>
            今日美食推荐
          </h4>
          <p class="suggestions-subtitle">根据当前天气为您精选</p>
        </div>
        
        <div class="suggestions-grid">
          <div 
            v-for="(suggestion, index) in (displayData.food_suggestions || [])"
            :key="suggestion"
            class="suggestion-card"
            :style="{ animationDelay: `${index * 0.1}s` }"
          >
            <div class="suggestion-icon">{{ getFoodIcon(suggestion) }}</div>
            <div class="suggestion-text">{{ suggestion }}</div>
            <div class="suggestion-action">
              <button 
                @click="searchFoodImages(suggestion)"
                class="suggestion-btn"
                title="查看图片"
              >
                📷
              </button>
              <button 
                @click="getFoodRecipe(suggestion)"
                class="suggestion-btn"
                title="获取菜谱"
              >
                📖
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 搜索结果 -->
    <div v-else-if="displayType === 'search_results'" class="result-container search-results">
      <div class="result-header">
        <span class="tool-icon">🔍</span>
        <span class="tool-title">搜索结果</span>
        <span class="result-count">{{ displayData.total_results || 0 }} 条结果</span>
      </div>
      
      <div class="search-items">
        <div 
          v-for="result in (displayData.results || []).slice(0, displayConfig.max_results || 10)"
          :key="result.url"
          class="search-item"
        >
          <a :href="result.url" target="_blank" class="result-link">
            <h4 class="result-title">{{ result.title }}</h4>
            <p class="result-snippet">{{ result.snippet }}</p>
            <span class="result-url">{{ result.display_url }}</span>
          </a>
        </div>
      </div>
    </div>

    <!-- 错误显示 -->
    <div v-else-if="displayType === 'error'" class="result-container error-display">
      <div class="result-header">
        <span class="tool-icon">❌</span>
        <span class="tool-title">工具执行失败</span>
      </div>
      <div class="error-content">
        <p class="error-message">{{ data.error }}</p>
        <button @click="retryTool" class="retry-btn">🔄 重试</button>
      </div>
    </div>

    <!-- 默认简单展示 -->
    <div v-else class="result-container simple-display">
      <div class="result-header">
        <span class="tool-icon">🔧</span>
        <span class="tool-title">工具结果</span>
      </div>
      <pre class="simple-content">{{ JSON.stringify(data, null, 2) }}</pre>
    </div>
  </div>
</template>

<script>
import AmapDisplay from './AmapDisplay.vue'

/**
 * @description 工具结果统一展示组件
 * 根据不同的工具类型展示相应的界面
 */
export default {
  name: 'ToolResultDisplay',
  components: {
    AmapDisplay
  },
  props: {
    data: {
      type: Object,
      required: true
    }
  },
  emits: ['requestRecipe', 'requestImages', 'retryTool'],
  data() {
    return {
      selectedCategory: '全部',
      nutritionLabels: {
        calories: '热量',
        protein: '蛋白质',
        carbohydrates: '碳水化合物',
        fat: '脂肪',
        fiber: '膳食纤维',
        sodium: '钠'
      },
      imageLoadingStates: [],
      maxVisibleImages: 12,
      showLoadingStats: false,
      mapViewMode: 'map'
    }
  },
  computed: {
    displayType() {
      // 处理MCP工具返回的嵌套结构
      if (this.data?.result?.display_type) {
        return this.data.result.display_type
      }
      return this.data?.display_type || 'simple_text'
    },
    displayConfig() {
      // 处理MCP工具返回的嵌套结构
      if (this.data?.result?.display_config) {
        return this.data.result.display_config
      }
      return this.data?.display_config || {}
    },
    displayData() {
      // 处理MCP工具返回的嵌套结构
      if (this.data?.result) {
        // 如果是MCP工具的返回格式，使用result中的数据
        return this.data.result
      }
      // 兜底逻辑：使用原来的逻辑
      return this.data?.display_data || this.data || {}
    },
    filteredRecommendations() {
      const recommendations = this.displayData.recommendations || []
      
      if (this.selectedCategory === '全部') {
        return recommendations
      }
      
      return recommendations.filter(
        rec => rec && rec.category === this.selectedCategory
      )
    },
    visibleImages() {
      const images = this.displayData.images || []
      return images.slice(0, this.maxVisibleImages)
    },
    loadedImagesCount() {
      return this.imageLoadingStates.filter(state => state === 'loaded').length
    },
    failedImagesCount() {
      return this.imageLoadingStates.filter(state => state === 'error').length
    },
    hasMoreImages() {
      const totalImages = (this.displayData.images || []).length
      return totalImages > this.maxVisibleImages
    },
    remainingImagesCount() {
      const totalImages = (this.displayData.images || []).length
      return Math.max(0, totalImages - this.maxVisibleImages)
    }
  },
  mounted() {
    if (this.displayType === 'image_gallery') {
      this.initializeImageStates()
    }
    
    // 调试：打印天气卡片的数据
    if (this.displayType === 'weather_card') {
      console.log('🌤️ 天气卡片数据调试:')
      console.log('原始数据:', this.data)
      console.log('显示类型:', this.displayType)
      console.log('显示数据:', this.displayData)
      console.log('城市名称:', this.displayData.city)
    }
  },
  watch: {
    'displayData.images': {
      handler(newImages) {
        if (this.displayType === 'image_gallery' && newImages && Array.isArray(newImages)) {
          this.initializeImageStates()
        }
      },
      immediate: true
    },
    'data': {
      handler(newData) {
        if (newData && this.displayType === 'image_gallery') {
          this.$nextTick(() => {
            this.initializeImageStates()
          })
        }
      },
      immediate: true
    }
  },
  methods: {
    /**
     * @description 显示图片模态框
     */
    showImageModal(image, index) {
      // 实现图片模态框
      console.log('显示图片:', image, index)
    },
    
    /**
     * @description 处理图片加载错误
     */
    handleImageError(index) {
      // 使用splice确保响应式更新
      this.imageLoadingStates.splice(index, 1, 'error')
      this.updateLoadingStats()
    },
    
    /**
     * @description 处理图片加载成功
     */
    handleImageLoad(index) {
      // 使用splice确保响应式更新
      this.imageLoadingStates.splice(index, 1, 'loaded')
      this.updateLoadingStats()
    },
    
    /**
     * @description 更新加载统计信息
     */
    updateLoadingStats() {
      const totalImages = this.visibleImages.length
      const processedImages = this.loadedImagesCount + this.failedImagesCount
      
      // 当所有图片处理完成且有失败的图片时显示统计信息
      if (processedImages >= totalImages && totalImages > 0) {
        // 显示统计信息，包括成功和失败的数量
        this.showLoadingStats = true
        
        // 在3秒后自动隐藏统计信息（仅当没有失败图片时）
        if (this.failedImagesCount === 0) {
          setTimeout(() => {
            this.showLoadingStats = false
          }, 3000)
        }
      }
    },

    /**
     * @description 显示更多图片
     */
    showMoreImages() {
      const oldMax = this.maxVisibleImages
      this.maxVisibleImages = Math.min(
        this.maxVisibleImages + 6, 
        (this.displayData.images || []).length
      )
      
      // 为新显示的图片初始化状态
      const images = this.displayData.images || []
      const newStates = [...this.imageLoadingStates]
      for (let i = oldMax; i < this.maxVisibleImages && i < images.length; i++) {
        newStates[i] = 'loading'
      }
      this.imageLoadingStates = newStates
    },
    
    /**
     * @description 根据分类筛选推荐
     */
    filterByCategory(category) {
      this.selectedCategory = category
    },
    
    /**
     * @description 选择推荐项
     */
    selectRecommendation(recommendation) {
      console.log('选择推荐:', recommendation)
    },
    
    /**
     * @description 搜索附近餐厅的图片
     */
    searchNearbyImages(restaurantName) {
      this.$emit('requestImages', restaurantName)
    },
    
    /**
     * @description 获取菜谱
     */
    getRecipe(dishName) {
      this.$emit('requestRecipe', dishName)
    },
    
    /**
     * @description 打印菜谱
     */
    printRecipe() {
      window.print()
    },
    
    /**
     * @description 保存菜谱
     */
    saveRecipe() {
      const recipe = this.displayData.recipe || {}
      const dishName = recipe.dish_name || '未知菜谱'
      const blob = new Blob([JSON.stringify(recipe, null, 2)], { 
        type: 'application/json' 
      })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${dishName}_菜谱.json`
      a.click()
      URL.revokeObjectURL(url)
    },
    
    /**
     * @description 获取营养成分标签
     */
    getNutritionLabel(key) {
      return this.nutritionLabels[key] || key
    },
    
    /**
     * @description 重试工具
     */
    retryTool() {
      this.$emit('retryTool', this.data.tool_name)
    },
    
    /**
     * @description 初始化图片加载状态
     */
    initializeImageStates() {
      try {
        const images = this.displayData?.images || []
        
        if (!Array.isArray(images)) {
          console.warn('图片数据不是数组格式')
          this.imageLoadingStates = []
          return
        }
        
        // 重置所有状态
        this.showLoadingStats = false
        
        // 创建新的状态数组，为每张图片初始化加载状态
        this.imageLoadingStates = images.map(() => 'loading')
        
      } catch (error) {
        console.error('初始化图片状态失败:', error)
        this.imageLoadingStates = []
        this.showLoadingStats = false
      }
    },

    /**
     * @description 处理位置变化
     */
    handleLocationChange(newLocation) {
      // 实现位置变化处理逻辑
      console.log('位置变化:', newLocation)
    },

    /**
     * @description 处理标记点击
     */
    handleMarkerClick(marker) {
      // 实现标记点击处理逻辑
      console.log('标记点击:', marker)
    },

    /**
     * @description 刷新地图
     */
    refreshMap() {
      // 触发地图重新初始化
      this.$nextTick(() => {
        const amapComponent = this.$refs.amapDisplay
        if (amapComponent && amapComponent.initializeMap) {
          amapComponent.initializeMap()
        }
      })
      console.log('🔄 刷新地图')
    },

    /**
     * @description 显示所有标记
     */
    showAllMarkers() {
      // 调用地图组件的fitToMarkers方法
      this.$nextTick(() => {
        const amapComponent = this.$refs.amapDisplay
        if (amapComponent && amapComponent.fitToMarkers) {
          amapComponent.fitToMarkers()
        }
      })
      console.log('🗺️ 显示全部标记')
    },

    /**
     * @description 获取地图标题
     */
    getMapTitle() {
      if (this.displayData.search_query) {
        return this.displayData.search_query
      }
      if (this.hasLocations()) {
        return '附近餐厅'
      }
      return '我的位置'
    },

    /**
     * @description 获取位置摘要信息
     */
    getLocationSummary() {
      const locations = this.displayData.locations || []
      if (locations.length > 0) {
        return `共找到 ${locations.length} 家餐厅`
      }
      return '显示当前位置'
    },

    /**
     * @description 检查是否有位置数据
     */
    hasLocations() {
      const locations = this.displayData.locations || []
      return locations.length > 0
    },

    /**
     * @description 搜索附近餐厅
     */
    searchNearbyRestaurants() {
      // 触发搜索附近餐厅的请求
      this.$emit('requestImages', '附近餐厅')
    },

    /**
     * @description 根据天气描述获取天气图标
     * @param {string} description - 天气描述
     * @returns {string} 天气图标
     */
    getWeatherIcon(description) {
      if (!description) return '🌤️'
      
      const desc = description.toLowerCase()
      
      // 晴天
      if (desc.includes('晴') || desc.includes('clear') || desc.includes('sunny')) {
        return '☀️'
      }
      // 多云
      if (desc.includes('云') || desc.includes('cloud')) {
        return '⛅'
      }
      // 雨天
      if (desc.includes('雨') || desc.includes('rain') || desc.includes('drizzle') || desc.includes('shower')) {
        return '🌧️'
      }
      // 雪天
      if (desc.includes('雪') || desc.includes('snow') || desc.includes('sleet')) {
        return '❄️'
      }
      // 雾天
      if (desc.includes('雾') || desc.includes('fog') || desc.includes('mist')) {
        return '🌫️'
      }
      // 风
      if (desc.includes('风') || desc.includes('wind')) {
        return '💨'
      }
      // 阴天
      if (desc.includes('阴') || desc.includes('overcast')) {
        return '☁️'
      }
      
      return '🌤️' // 默认图标
    },

    /**
     * @description 提取温度数值
     * @param {string} temperature - 温度字符串
     * @returns {string} 温度数值
     */
    extractTemperature(temperature) {
      if (!temperature) return '--'
      
      // 如果已经是纯数字，直接返回
      const match = temperature.toString().match(/(-?\d+(?:\.\d+)?)/);
      return match ? match[1] : '--'
    },

    /**
     * @description 根据美食名称获取图标
     * @param {string} food - 美食名称
     * @returns {string} 美食图标
     */
    getFoodIcon(food) {
      if (!food) return '🍽️'
      
      // 热汤类
      if (food.includes('汤') || food.includes('粥')) {
        return '🍲'
      }
      // 火锅
      if (food.includes('火锅')) {
        return '🍲'
      }
      // 面条类
      if (food.includes('面') || food.includes('凉面')) {
        return '🍜'
      }
      // 饮品类
      if (food.includes('茶') || food.includes('饮') || food.includes('汁') || food.includes('啤酒') || food.includes('咖啡')) {
        return '🥤'
      }
      // 冰品类
      if (food.includes('冰') || food.includes('淇淋')) {
        return '🍨'
      }
      // 沙拉类
      if (food.includes('沙拉')) {
        return '🥗'
      }
      // 烧烤类
      if (food.includes('烧烤')) {
        return '🍖'
      }
      // 肉类
      if (food.includes('肉') || food.includes('鸡') || food.includes('鱼') || food.includes('虾')) {
        return '🍖'
      }
      // 蔬菜类
      if (food.includes('菜') || food.includes('蔬')) {
        return '🥬'
      }
      
      return '🍽️' // 默认图标
    },

    /**
     * @description 搜索美食图片
     * @param {string} foodName - 美食名称
     */
    searchFoodImages(foodName) {
      this.$emit('requestImages', foodName)
    },

    /**
     * @description 获取美食菜谱
     * @param {string} foodName - 美食名称
     */
    getFoodRecipe(foodName) {
      this.$emit('requestRecipe', foodName)
    },

    /**
     * @description 格式化城市名称显示
     * @param {string} cityName - 原始城市名称
     * @returns {string} 格式化后的城市名称
     */
    formatCityName(cityName) {
      if (!cityName) return ''
      
      // 城市名称映射表
      const cityMap = {
        'Changsha': '长沙',
        'Beijing': '北京',
        'Shanghai': '上海',
        'Guangzhou': '广州',
        'Shenzhen': '深圳',
        'Chengdu': '成都',
        'Hangzhou': '杭州',
        'Wuhan': '武汉',
        'Xi\'an': '西安',
        'Nanjing': '南京',
        'Tianjin': '天津',
        'Suzhou': '苏州',
        'Qingdao': '青岛',
        'Dalian': '大连',
        'Xiamen': '厦门',
        'Ningbo': '宁波'
      }
      
      // 如果包含逗号，分割处理
      if (cityName.includes(',')) {
        const [city, country] = cityName.split(',').map(s => s.trim())
        
        // 如果是中国城市且有中文映射，使用中文名称
        if (country === 'CN' && cityMap[city]) {
          return cityMap[city]
        }
        
        // 如果是中国城市但没有映射，只显示英文城市名
        if (country === 'CN') {
          return city
        }
        
        // 非中国城市，保持原格式
        return cityName
      }
      
      // 直接查找映射
      return cityMap[cityName] || cityName
    }
  }
}
</script>

<style scoped>
.tool-result-display {
  margin: 16px 0;
}

.result-container {
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(108, 99, 255, 0.1);
  transition: all 0.3s ease;
}

.result-container:hover {
  border-color: var(--primary-color);
  box-shadow: 0 4px 16px rgba(108, 99, 255, 0.2);
}

.result-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
  color: white;
  font-weight: 600;
}

.tool-icon {
  font-size: 18px;
}

.tool-title {
  flex: 1;
  font-size: 16px;
}

.result-count {
  font-size: 14px;
  opacity: 0.9;
}

.header-actions {
  display: flex;
  gap: 8px;
}

/* 图片画廊样式 */
.image-gallery .image-grid {
  display: grid;
  gap: 12px;
  padding: 20px;
}

.image-grid.columns-3 {
  grid-template-columns: repeat(3, 1fr);
}

.image-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.3s ease;
  background: #f5f5f5;
}

.image-item:hover {
  transform: scale(1.05);
}

.image-item.loading {
  background: linear-gradient(
    90deg,
    #f0f0f0 25%,
    #e0e0e0 50%,
    #f0f0f0 75%
  );
  background-size: 200% 100%;
  animation: loading-shimmer 1.5s infinite ease-in-out;
}

.image-item.error {
  background: #ffebee;
  border: 2px dashed #f44336;
}

.image-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: opacity 0.3s ease;
}

.image-loading {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(2px);
}

.loading-spinner {
  width: 30px;
  height: 30px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid var(--primary-color);
  border-radius: 50%;
  animation: spinner-rotate 1s linear infinite;
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.image-item:hover .image-overlay {
  opacity: 1;
}

.view-icon {
  font-size: 24px;
  color: white;
}

.loading-stats {
  padding: 12px 20px;
  background: rgba(255, 152, 0, 0.1);
  border-top: 1px solid var(--border-color);
  text-align: center;
}

.stats-text {
  font-size: 13px;
  color: var(--text-secondary);
}

/* 推荐卡片样式 */
.category-filter {
  display: flex;
  gap: 8px;
  padding: 16px 20px 0;
  overflow-x: auto;
}

.category-btn {
  padding: 6px 16px;
  border: 1px solid var(--border-color);
  border-radius: 20px;
  background: var(--background-color);
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.category-btn.active,
.category-btn:hover {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.recommendation-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
  padding: 20px;
}

.recommendation-card {
  background: var(--background-color);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.recommendation-card:hover {
  border-color: var(--primary-color);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(108, 99, 255, 0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.dish-name {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.category-tag {
  background: var(--primary-color);
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.reason {
  color: var(--text-secondary);
  margin-bottom: 16px;
  font-size: 14px;
}

.card-stats {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--text-secondary);
}

.ingredients-preview {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 16px;
}

.ingredients-label {
  font-weight: 600;
}

.card-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.action-btn.primary {
  background: var(--primary-color);
  color: white;
}

.action-btn.secondary {
  background: var(--background-color);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.action-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 菜谱详细样式 */
.recipe-metadata {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
  padding: 20px;
  background: var(--background-color);
  border-bottom: 1px solid var(--border-color);
}

.meta-item {
  text-align: center;
}

.meta-label {
  display: block;
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.meta-value {
  display: block;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.recipe-section {
  padding: 20px;
  border-bottom: 1px solid var(--border-color);
}

.recipe-section:last-child {
  border-bottom: none;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 16px 0;
}

.ingredients-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.ingredient-item {
  display: flex;
  justify-content: space-between;
  padding: 12px;
  background: var(--background-color);
  border: 1px solid var(--border-color);
  border-radius: 8px;
}

.ingredient-name {
  font-weight: 500;
  color: var(--text-primary);
}

.ingredient-amount {
  color: var(--text-secondary);
}

.steps-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.step-item {
  display: flex;
  gap: 16px;
  align-items: flex-start;
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

.step-content {
  flex: 1;
}

.step-instruction {
  margin: 0 0 8px 0;
  color: var(--text-primary);
  line-height: 1.6;
}

.step-time,
.step-tips {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.nutrition-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 12px;
}

.nutrition-item {
  padding: 12px;
  background: var(--background-color);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  text-align: center;
}

.nutrition-label {
  display: block;
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.nutrition-value {
  display: block;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

/* 其他样式继续... */
.show-more {
  padding: 16px 20px;
  text-align: center;
  border-top: 1px solid var(--border-color);
}

.show-more-btn {
  padding: 10px 20px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.show-more-btn:hover {
  background: var(--secondary-color);
  transform: translateY(-1px);
}

@keyframes loading-shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}

@keyframes spinner-rotate {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .image-grid.columns-3 {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .recommendation-grid {
    grid-template-columns: 1fr;
  }
  
 .recipe-metadata {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .ingredients-grid {
    grid-template-columns: 1fr;
  }
  
  .nutrition-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* 位置搜索结果样式 */
.location-items {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.location-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 20px;
  background: #fafafa;
  border-radius: 12px;
  border: 1px solid #e0e0e0;
  transition: all 0.3s ease;
}

.location-item:hover {
  border-color: var(--primary-color);
  box-shadow: 0 4px 12px rgba(108, 99, 255, 0.15);
  transform: translateY(-2px);
}

.location-info {
  flex: 1;
  min-width: 0;
}

.location-name {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.location-address {
  color: var(--text-secondary);
  font-size: 14px;
  margin: 0 0 12px 0;
  line-height: 1.4;
}

.location-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 12px;
}

.meta-item {
  display: inline-flex;
  align-items: center;
  font-size: 13px;
  color: var(--text-secondary);
  padding: 4px 8px;
  background: white;
  border-radius: 6px;
  border: 1px solid #e0e0e0;
}

.meta-item.distance {
  color: #1976d2;
  border-color: #e3f2fd;
  background: #e3f2fd;
}

.meta-item.rating {
  color: #f57c00;
  border-color: #fff3e0;
  background: #fff3e0;
}

.meta-item.price {
  color: #388e3c;
  border-color: #e8f5e8;
  background: #e8f5e8;
}

.meta-item.phone {
  color: #7b1fa2;
  border-color: #f3e5f5;
  background: #f3e5f5;
}

.location-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag {
  font-size: 12px;
  padding: 2px 8px;
  background: var(--primary-color);
  color: white;
  border-radius: 12px;
  opacity: 0.8;
}

.location-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-left: 16px;
  flex-shrink: 0;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: white;
  color: var(--text-primary);
  text-decoration: none;
  font-size: 13px;
  transition: all 0.3s ease;
  cursor: pointer;
  min-width: 80px;
}

.action-btn:hover {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
  transform: scale(1.05);
}

.map-btn:hover {
  background: #4caf50;
  border-color: #4caf50;
}

.call-btn:hover {
  background: #2196f3;
  border-color: #2196f3;
}

.image-btn:hover {
  background: #ff9800;
  border-color: #ff9800;
}

/* 空状态样式 */
.empty-state {
  padding: 60px 20px;
  text-align: center;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.6;
}

.empty-message {
  font-size: 16px;
  color: #666;
  margin-bottom: 8px;
}

.empty-suggestion {
  font-size: 14px;
  color: #999;
  margin-bottom: 20px;
}

.switch-view-btn {
  padding: 8px 16px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.switch-view-btn:hover {
  background: var(--secondary-color);
}

.view-toggle {
  display: flex;
  gap: 4px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  padding: 4px;
}

.view-btn {
  padding: 6px 8px;
  background: transparent;
  border: none;
  border-radius: 4px;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
}

.view-btn.active {
  background: rgba(255, 255, 255, 0.3);
}

.view-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.map-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f8f9fa;
  border-top: 1px solid #e9ecef;
  border-radius: 0 0 8px 8px;
}

.summary-info {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.info-item {
  font-size: 14px;
  color: #666;
  display: flex;
  align-items: center;
  gap: 4px;
}

.map-actions {
  display: flex;
  gap: 8px;
}

.action-btn.small {
  padding: 6px 12px;
  font-size: 12px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-btn.small:hover {
  background: var(--secondary-color);
  transform: translateY(-1px);
}

/* 响应式优化 */
@media (max-width: 768px) {
  .map-summary {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .summary-info {
    width: 100%;
  }
  
  .map-actions {
    width: 100%;
    justify-content: center;
  }
}
</style> 
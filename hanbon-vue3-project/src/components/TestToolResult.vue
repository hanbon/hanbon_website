<template>
  <div class="test-container">
    <h2>工具结果展示测试</h2>
    
    <div class="test-section">
      <h3>图片搜索结果测试</h3>
      <ToolResultDisplay :data="imageTestData" />
    </div>
    
    <div class="test-section">
      <h3>美食推荐测试</h3>
      <ToolResultDisplay :data="recommendationTestData" />
    </div>
    
    <div class="test-section">
      <h3>简单数据测试</h3>
      <ToolResultDisplay :data="simpleTestData" />
    </div>
  </div>
</template>

<script>
import ToolResultDisplay from './ToolResultDisplay.vue'

export default {
  name: 'TestToolResult',
  components: {
    ToolResultDisplay
  },
  data() {
    return {
      imageTestData: {
        display_type: 'image_gallery',
        display_config: {
          columns: 3,
          lazy_load: true
        },
        display_data: {
          total: 6,
          images: [
            { url: 'https://via.placeholder.com/300x300/ff6b6b/ffffff?text=红烧肉1', thumbnailUrl: 'https://via.placeholder.com/150x150/ff6b6b/ffffff?text=红烧肉1' },
            { url: 'https://via.placeholder.com/300x300/4ecdc4/ffffff?text=红烧肉2', thumbnailUrl: 'https://via.placeholder.com/150x150/4ecdc4/ffffff?text=红烧肉2' },
            { url: 'https://via.placeholder.com/300x300/45b7d1/ffffff?text=红烧肉3', thumbnailUrl: 'https://via.placeholder.com/150x150/45b7d1/ffffff?text=红烧肉3' }
          ]
        }
      },
      
      recommendationTestData: {
        display_type: 'recommendation_cards',
        display_config: {
          layout: 'card_grid',
          show_ratings: true,
          interactive: true
        },
        display_data: {
          total_count: 2,
          categories: ['家常菜', '汤品'],
          recommendations: [
            {
              dish_name: '红烧肉',
              category: '家常菜',
              reason: '经典家常菜，味道浓郁，适合下饭',
              cooking_time: '45分钟',
              difficulty: '简单',
              nutrition_score: 85,
              ingredients: ['五花肉', '冰糖', '生抽', '老抽', '料酒']
            },
            {
              dish_name: '西红柿鸡蛋汤',
              category: '汤品',
              reason: '清淡营养，制作简单，适合搭配米饭',
              cooking_time: '15分钟',
              difficulty: '很简单',
              nutrition_score: 75,
              ingredients: ['西红柿', '鸡蛋', '香菜', '盐']
            }
          ]
        }
      },
      
      simpleTestData: {
        display_type: 'simple_text',
        content: '这是一个简单的测试数据'
      }
    }
  }
}
</script>

<style scoped>
.test-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.test-section {
  margin-bottom: 40px;
  padding: 20px;
  background: #f5f5f5;
  border-radius: 8px;
}

.test-section h3 {
  margin-top: 0;
  color: #333;
}
</style> 
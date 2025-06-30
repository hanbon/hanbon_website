<template>
  <div class="image-gallery-test">
    <h2>图片搜索结果测试</h2>
    
    <div class="test-controls">
      <button @click="loadTestImages" class="test-btn">加载测试图片</button>
      <button @click="loadMixedImages" class="test-btn">加载混合图片(有效/无效)</button>
      <button @click="clearImages" class="test-btn">清空图片</button>
    </div>
    
    <div class="test-info">
      <p>测试说明：</p>
      <ul>
        <li>有效图片会正常显示</li>
        <li>无效图片会自动隐藏</li>
        <li>图片数量会动态更新</li>
        <li>显示加载统计信息</li>
      </ul>
    </div>
    
    <!-- 使用ToolResultDisplay组件 -->
    <ToolResultDisplay :data="testData" />
  </div>
</template>

<script>
import ToolResultDisplay from './ToolResultDisplay.vue'

export default {
  name: 'ImageGalleryTest',
  components: {
    ToolResultDisplay
  },
  data() {
    return {
      testData: {
        display_type: 'image_gallery',
        display_config: {
          columns: 3,
          lazy_load: true
        },
        display_data: {
          total: 0,
          images: []
        }
      }
    }
  },
  methods: {
    loadTestImages() {
      // 加载一些有效的测试图片 - 使用多种可靠的图片源
      this.testData.display_data.images = [
        { 
          url: this.generateDataUrlImage('红烧肉', '#ff6b6b'),
          thumbnailUrl: this.generateDataUrlImage('红烧肉', '#ff6b6b', 150)
        },
        { 
          url: this.generateDataUrlImage('宫保鸡丁', '#4ecdc4'),
          thumbnailUrl: this.generateDataUrlImage('宫保鸡丁', '#4ecdc4', 150)
        },
        { 
          url: this.generateDataUrlImage('麻婆豆腐', '#45b7d1'),
          thumbnailUrl: this.generateDataUrlImage('麻婆豆腐', '#45b7d1', 150)
        },
        { 
          url: this.generateDataUrlImage('糖醋排骨', '#96ceb4'),
          thumbnailUrl: this.generateDataUrlImage('糖醋排骨', '#96ceb4', 150)
        },
        { 
          url: this.generateDataUrlImage('清蒸鱼', '#ffd93d'),
          thumbnailUrl: this.generateDataUrlImage('清蒸鱼', '#ffd93d', 150)
        },
        { 
          url: this.generateDataUrlImage('回锅肉', '#ff8a80'),
          thumbnailUrl: this.generateDataUrlImage('回锅肉', '#ff8a80', 150)
        }
      ]
      this.testData.display_data.total = this.testData.display_data.images.length
    },
    
    loadMixedImages() {
      // 加载混合图片（有效和无效）
      this.testData.display_data.images = [
        { 
          url: this.generateDataUrlImage('有效图片1', '#ff6b6b'),
          thumbnailUrl: this.generateDataUrlImage('有效图片1', '#ff6b6b', 150)
        },
        { 
          url: 'https://invalid-domain-12345.com/invalid.jpg',  // 确保无效的URL
          thumbnailUrl: 'https://invalid-domain-12345.com/invalid-thumb.jpg'
        },
        { 
          url: this.generateDataUrlImage('有效图片2', '#4ecdc4'),
          thumbnailUrl: this.generateDataUrlImage('有效图片2', '#4ecdc4', 150)
        },
        { 
          url: 'https://broken-link-example-xyz.jpg',  // 无效图片
          thumbnailUrl: 'https://broken-link-example-xyz-thumb.jpg'
        },
        { 
          url: this.generateDataUrlImage('有效图片3', '#45b7d1'),
          thumbnailUrl: this.generateDataUrlImage('有效图片3', '#45b7d1', 150)
        },
        { 
          url: 'data:image/svg+xml;charset=utf-8,<svg>invalid</svg>',  // 无效的SVG
          thumbnailUrl: 'data:image/svg+xml;charset=utf-8,<svg>invalid</svg>'
        }
      ]
      this.testData.display_data.total = this.testData.display_data.images.length
    },
    
    clearImages() {
      this.testData.display_data.images = []
      this.testData.display_data.total = 0
    },
    
    /**
     * @description 生成数据URL图片
     * @param {string} text 图片上的文字
     * @param {string} color 背景颜色
     * @param {number} size 图片尺寸
     */
    generateDataUrlImage(text, color, size = 300) {
      const canvas = document.createElement('canvas')
      const ctx = canvas.getContext('2d')
      
      canvas.width = size
      canvas.height = size
      
      // 设置背景色
      ctx.fillStyle = color
      ctx.fillRect(0, 0, size, size)
      
      // 设置文字样式
      ctx.fillStyle = '#ffffff'
      ctx.font = `bold ${Math.floor(size * 0.08)}px Arial`
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      
      // 绘制文字
      ctx.fillText(text, size / 2, size / 2)
      
      // 添加一些装饰
      ctx.strokeStyle = '#ffffff'
      ctx.lineWidth = 2
      ctx.strokeRect(10, 10, size - 20, size - 20)
      
      return canvas.toDataURL('image/png')
    }
  }
}
</script>

<style scoped>
.image-gallery-test {
  max-width: 1200px;
  margin: 20px auto;
  padding: 20px;
}

.test-controls {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.test-btn {
  padding: 10px 20px;
  background: #6c63ff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background 0.3s;
}

.test-btn:hover {
  background: #5a54d6;
}

.test-info {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  border-left: 4px solid #6c63ff;
}

.test-info h3 {
  margin: 0 0 10px 0;
  color: #333;
}

.test-info ul {
  margin: 10px 0;
  padding-left: 20px;
}

.test-info li {
  margin-bottom: 5px;
  color: #666;
}
</style> 
<template>
  <div class="amap-container">
    <div class="map-header">
      <h3 class="map-title">
        <span class="map-icon">🗺️</span>
        {{ title }}
      </h3>
      <div class="map-controls">
        <button @click="getCurrentLocation" class="control-btn" :disabled="isLocating">
          <span v-if="isLocating">📍 定位中...</span>
          <span v-else>📍 我的位置</span>
        </button>
        <button @click="fitToMarkers" class="control-btn" v-if="locations.length > 0">
          🔍 显示全部
        </button>
      </div>
    </div>
    
    <div class="map-wrapper">
      <div id="amap-container" class="amap-element" ref="mapContainer"></div>
      
      <!-- 加载状态 -->
      <div v-if="isLoading" class="map-loading">
        <div class="loading-spinner"></div>
        <p>地图加载中...</p>
      </div>
      
      <!-- 错误状态 -->
      <div v-if="mapError" class="map-error">
        <div class="error-icon">❌</div>
        <p>地图加载失败</p>
        <button @click="initializeMap" class="retry-btn">重试</button>
      </div>
    </div>
    
    <!-- 地图图例 -->
    <div class="map-legend" v-if="!isLoading && !mapError">
      <div class="legend-item">
        <span class="legend-marker current-location">📍</span>
        <span class="legend-text">我的位置</span>
      </div>
      <div class="legend-item" v-if="locations.length > 0">
        <span class="legend-marker restaurant">🍴</span>
        <span class="legend-text">餐厅位置</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AmapDisplay',
  props: {
    locations: {
      type: Array,
      default: () => []
    },
    title: {
      type: String,
      default: '附近餐厅'
    },
    center: {
      type: Array,
      default: () => [112.982279, 28.194090] // 长沙默认坐标
    },
    zoom: {
      type: Number,
      default: 13
    },
    amapKey: {
      type: String,
      default: null
    }
  },
  emits: ['locationChange', 'markerClick'],
  data() {
    return {
      map: null,
      AMap: null,
      isLoading: true,
      mapError: false,
      isLocating: false,
      userLocation: null,
      markers: [],
      userMarker: null,
      infoWindow: null
    }
  },
  mounted() {
    this.loadAmapScript()
  },
  beforeUnmount() {
    if (this.map) {
      this.map.destroy()
    }
  },
  watch: {
    locations: {
      handler(newLocations) {
        if (this.map && newLocations) {
          this.updateMarkers()
        }
      },
      deep: true
    }
  },
  methods: {
    /**
     * @description 加载高德地图脚本
     */
    async loadAmapScript() {
      try {
        // 检查是否已加载
        if (window.AMap && window.AMap.Map) {
          this.AMap = window.AMap
          console.log('高德地图API已存在，直接初始化')
          this.initializeMap()
          return
        }
        
        // 获取高德地图API密钥
        const amapKey = this.getAmapKey()
        if (!amapKey) {
          throw new Error('未配置高德地图API密钥')
        }
        
        // 检查是否已有相同的脚本在加载
        const existingScript = document.querySelector('script[src*="webapi.amap.com"]')
        if (existingScript) {
          console.log('高德地图脚本正在加载中，等待加载完成')
          return new Promise((resolve) => {
            const checkInterval = setInterval(() => {
              if (window.AMap && window.AMap.Map) {
                clearInterval(checkInterval)
                this.AMap = window.AMap
                this.initializeMap()
                resolve()
              }
            }, 100)
            
            // 10秒超时
            setTimeout(() => {
              clearInterval(checkInterval)
              if (!window.AMap || !window.AMap.Map) {
                this.mapError = true
                this.isLoading = false
                console.error('高德地图脚本加载超时')
              }
            }, 10000)
          })
        }
        
        console.log('开始加载高德地图API脚本')
        
        // 动态加载高德地图脚本
        const script = document.createElement('script')
        script.type = 'text/javascript'
        script.charset = 'utf-8'
        script.async = true
        script.src = `https://webapi.amap.com/maps?v=2.0&key=${amapKey}&plugin=AMap.Scale,AMap.ToolBar,AMap.Geolocation`
        
        // 添加脚本加载回调
        script.onload = () => {
          console.log('高德地图脚本加载成功')
          if (window.AMap && window.AMap.Map) {
            this.AMap = window.AMap
            this.initializeMap()
          } else {
            console.error('高德地图API加载后未找到AMap对象')
            this.mapError = true
            this.isLoading = false
          }
        }
        
        script.onerror = (error) => {
          console.error('高德地图脚本加载失败:', error)
          this.mapError = true
          this.isLoading = false
        }
        
        // 添加到文档头部
        document.head.appendChild(script)
        
        // 设置加载超时
        setTimeout(() => {
          if (!window.AMap || !window.AMap.Map) {
            console.error('高德地图脚本加载超时')
            this.mapError = true
            this.isLoading = false
          }
        }, 15000) // 15秒超时
        
      } catch (error) {
        console.error('加载地图失败:', error)
        this.mapError = true
        this.isLoading = false
      }
    },
    
    /**
     * @description 获取高德地图API密钥
     */
    getAmapKey() {
      // 优先从props获取
      if (this.amapKey) {
        console.log('🔑 使用props提供的API密钥')
        return this.amapKey
      }
      
      // 从环境变量获取
      if (process.env.VUE_APP_AMAP_KEY) {
        console.log('🔑 使用环境变量中的API密钥')
        return process.env.VUE_APP_AMAP_KEY
      }
      
      // 从全局配置获取
      if (window.APP_CONFIG && window.APP_CONFIG.AMAP_KEY) {
        console.log('🔑 使用全局配置中的API密钥:', window.APP_CONFIG.AMAP_KEY.substring(0, 8) + '...')
        return window.APP_CONFIG.AMAP_KEY
      }
      
      // 开发环境默认密钥（需要替换为实际密钥）
      if (process.env.NODE_ENV === 'development') {
        console.warn('⚠️ 使用开发环境默认密钥，请配置正确的API密钥')
        return 'your-default-key-here'
      }
      
      console.error('❌ 未找到有效的高德地图API密钥')
      return null
    },
    
    /**
     * @description 初始化地图
     */
    initializeMap() {
      try {
        this.isLoading = true
        this.mapError = false
        
        // 检查地图容器是否存在
        const mapContainer = document.getElementById('amap-container')
        if (!mapContainer) {
          throw new Error('地图容器元素未找到')
        }
        
        // 检查容器是否有可见大小
        const containerRect = mapContainer.getBoundingClientRect()
        console.log('📏 地图容器尺寸:', {
          width: containerRect.width,
          height: containerRect.height
        })
        
        if (containerRect.width === 0 || containerRect.height === 0) {
          console.warn('⚠️ 地图容器尺寸为0，将在下一个事件循环中重试')
          setTimeout(() => this.initializeMap(), 100)
          return
        }
        
        console.log('🗺️ 开始创建地图实例...')
        
        // 创建地图实例
        this.map = new this.AMap.Map('amap-container', {
          zoom: this.zoom,
          center: this.center,
          mapStyle: 'amap://styles/normal',
          features: ['bg', 'road', 'building', 'point'],
          viewMode: '2D',
          resizeEnable: true
        })
        
        console.log('✅ 地图实例创建成功')
        
        // 添加地图控件
        this.map.addControl(new this.AMap.Scale())
        this.map.addControl(new this.AMap.ToolBar({
          direction: false,
          ruler: false,
          locate: false
        }))
        
        // 创建信息窗体
        this.infoWindow = new this.AMap.InfoWindow({
          offset: new this.AMap.Pixel(0, -30),
          closeWhenClickMap: true
        })
        
        // 地图加载完成
        this.map.on('complete', () => {
          console.log('✅ 地图加载完成')
          this.isLoading = false
          this.updateMarkers()
          this.getCurrentLocation()
        })
        
        // 地图点击事件
        this.map.on('click', () => {
          this.infoWindow.close()
        })
        
        // 地图错误事件
        this.map.on('error', (error) => {
          console.error('❌ 地图错误:', error)
          this.mapError = true
          this.isLoading = false
        })
        
      } catch (error) {
        console.error('❌ 地图初始化失败:', error)
        this.mapError = true
        this.isLoading = false
      }
    },
    
    /**
     * @description 获取用户当前位置
     */
    getCurrentLocation() {
      if (!this.map) return
      
      this.isLocating = true
      
      // 使用高德地图定位插件
      this.AMap.plugin('AMap.Geolocation', () => {
        const geolocation = new this.AMap.Geolocation({
          enableHighAccuracy: true,
          timeout: 8000,
          maximumAge: 60000,
          convert: true,
          showButton: false,
          showMarker: false,
          showCircle: false,
          panToLocation: false,
          zoomToAccuracy: false
        })
        
        geolocation.getCurrentPosition((status, result) => {
          if (status === 'complete') {
            const position = [result.position.lng, result.position.lat]
            this.userLocation = position
            
            // 更新用户位置标记
            this.updateUserMarker(position)
            
            // 移动地图中心到用户位置
            this.map.setCenter(position)
            
            this.$emit('locationChange', {
              longitude: result.position.lng,
              latitude: result.position.lat,
              address: result.formattedAddress,
              accuracy: 'amap_location'
            })
            
            this.isLocating = false
            console.log('✅ 高德定位成功:', result.formattedAddress)
            
          } else {
            console.warn('高德定位失败:', result.message, '错误码:', result.info)
            // 降级到浏览器定位
            this.getBrowserLocation()
          }
        })
      })
    },
    
    /**
     * @description 使用浏览器定位API
     */
    getBrowserLocation() {
      if (!navigator.geolocation) {
        console.warn('浏览器不支持地理位置API')
        this.getIPLocation()
        return
      }
      
      console.log('🌍 尝试浏览器地理位置API...')
      
      const options = {
        enableHighAccuracy: true,
        timeout: 8000,
        maximumAge: 60000
      }
      
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const lng = position.coords.longitude
          const lat = position.coords.latitude
          const userPos = [lng, lat]
          
          this.userLocation = userPos
          this.updateUserMarker(userPos)
          this.map.setCenter(userPos)
          
          this.$emit('locationChange', {
            longitude: lng,
            latitude: lat,
            address: '浏览器定位',
            accuracy: 'browser_location'
          })
          
          this.isLocating = false
          console.log('✅ 浏览器定位成功')
        },
        (error) => {
          let errorMessage = '浏览器定位失败'
          switch(error.code) {
            case error.PERMISSION_DENIED:
              errorMessage = '用户拒绝了地理位置权限请求'
              break
            case error.POSITION_UNAVAILABLE:
              errorMessage = '位置信息不可用'
              break
            case error.TIMEOUT:
              errorMessage = '定位请求超时'
              break
          }
          console.warn('⚠️', errorMessage, '错误详情:', error)
          // 最后降级到IP定位
          this.getIPLocation()
        },
        options
      )
    },
    
    /**
     * @description 使用IP定位API作为最后的备选方案
     */
    async getIPLocation() {
      try {
        console.log('🌐 开始IP定位...')
        
        // 检查是否有后端服务
        const apiUrl = window.APP_CONFIG?.API_BASE_URL || 'http://localhost:8000'
        
        try {
          // 调用后端IP定位接口
          const response = await fetch(`${apiUrl}/api/get_ip_location`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({}),
            timeout: 5000 // 5秒超时
          })
          
          if (response.ok) {
            const data = await response.json()
            
            if (data.success && data.center_coordinates) {
              const [lng, lat] = data.center_coordinates
              const userPos = [lng, lat]
              
              this.userLocation = userPos
              this.updateUserMarker(userPos)
              this.map.setCenter(userPos)
              
              this.$emit('locationChange', {
                longitude: lng,
                latitude: lat,
                address: data.formatted_address || '未知位置',
                accuracy: 'ip_location',
                city: data.city,
                province: data.province
              })
              
              console.log('✅ IP定位成功:', data.formatted_address)
              this.isLocating = false
              return
            }
          }
        } catch (apiError) {
          console.warn('后端API请求失败:', apiError.message)
        }
        
        // API失败时，使用第三方IP定位服务
        console.log('🌐 尝试第三方IP定位服务...')
        try {
          const ipResponse = await fetch('https://ipapi.co/json/', {
            timeout: 3000
          })
          
          if (ipResponse.ok) {
            const ipData = await ipResponse.json()
            if (ipData.latitude && ipData.longitude) {
              const userPos = [ipData.longitude, ipData.latitude]
              
              this.userLocation = userPos
              this.updateUserMarker(userPos)
              this.map.setCenter(userPos)
              
              this.$emit('locationChange', {
                longitude: ipData.longitude,
                latitude: ipData.latitude,
                address: `${ipData.city || '未知城市'}, ${ipData.country_name || '未知国家'}`,
                accuracy: 'ip_location_external',
                city: ipData.city,
                country: ipData.country_name
              })
              
              console.log('✅ 第三方IP定位成功:', ipData.city)
              this.isLocating = false
              return
            }
          }
        } catch (externalError) {
          console.warn('第三方IP定位失败:', externalError.message)
        }
        
        // 所有IP定位都失败时，使用默认位置
        this.handleLocationFailure()
        
      } catch (error) {
        console.error('IP定位异常:', error)
        this.handleLocationFailure()
      } finally {
        this.isLocating = false
      }
    },
    
    /**
     * @description 处理所有定位方式都失败的情况
     */
    handleLocationFailure() {
      console.warn('所有定位方式都失败，使用默认位置')
      
      // 使用默认位置（长沙）
      const defaultPos = this.center
      this.userLocation = defaultPos
      this.updateUserMarker(defaultPos)
      this.map.setCenter(defaultPos)
      
      this.$emit('locationChange', {
        longitude: defaultPos[0],
        latitude: defaultPos[1],
        address: '长沙市（默认位置）',
        accuracy: 'default_location'
      })
      
      this.isLocating = false
    },
    
    /**
     * @description 更新用户位置标记
     */
    updateUserMarker(position) {
      if (!this.map) return
      
      // 移除旧的用户标记
      if (this.userMarker) {
        this.map.remove(this.userMarker)
      }
      
      // 创建用户位置标记
      this.userMarker = new this.AMap.Marker({
        position: position,
        icon: new this.AMap.Icon({
          image: 'data:image/svg+xml;base64,' + btoa(`
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="48 48 48 48">
              <defs>
                <filter id="userShadow" x="-50%" y="-50%" width="200%" height="200%">
                  <feDropShadow dx="2" dy="2" stdDeviation="3" flood-color="rgba(0,0,0,0.3)"/>
                </filter>
              </defs>
              <circle cx="24" cy="24" r="18" fill="rgba(33, 150, 243, 0.3)" filter="url(#userShadow)"/>
              <circle cx="24" cy="24" r="16" fill="#2196F3" stroke="white" stroke-width="4"/>
              <circle cx="24" cy="24" r="8" fill="white"/>
              <circle cx="24" cy="24" r="4" fill="#1976D2"/>
            </svg>
          `),
          size: new this.AMap.Size(48, 48),
          imageOffset: new this.AMap.Pixel(-24, -24)
        }),
        title: '我的位置',
        zIndex: 1000
      })
      
      this.map.add(this.userMarker)
      
      // 添加点击事件
      this.userMarker.on('click', () => {
        this.infoWindow.setContent(`
          <div class="info-window">
            <h4>📍 我的位置</h4>
            <p>经度: ${position[0].toFixed(6)}</p>
            <p>纬度: ${position[1].toFixed(6)}</p>
          </div>
        `)
        this.infoWindow.open(this.map, position)
      })
    },
    
    /**
     * @description 更新餐厅标记
     */
    updateMarkers() {
      if (!this.map || !this.locations) return
      
      // 清除旧标记
      this.markers.forEach(marker => {
        this.map.remove(marker)
      })
      this.markers = []
      
      // 添加新标记
      this.locations.forEach((location, index) => {
        // 验证坐标数据
        if (!location.location_coords) {
          console.warn(`餐厅 "${location.name}" 缺少坐标信息`)
          return
        }
        
        const coords = location.location_coords.split(',')
        if (coords.length !== 2) {
          console.warn(`餐厅 "${location.name}" 坐标格式错误: ${location.location_coords}`)
          return
        }
        
        const longitude = parseFloat(coords[0].trim())
        const latitude = parseFloat(coords[1].trim())
        
        // 验证坐标是否为有效数字
        if (isNaN(longitude) || isNaN(latitude)) {
          console.warn(`餐厅 "${location.name}" 坐标无效: 经度=${longitude}, 纬度=${latitude}`)
          return
        }
        
        // 验证坐标范围（中国境内大致范围）
        if (longitude < 73 || longitude > 135 || latitude < 3 || latitude > 54) {
          console.warn(`餐厅 "${location.name}" 坐标超出中国范围: 经度=${longitude}, 纬度=${latitude}`)
          return
        }
        
        const position = [longitude, latitude]
        
        // 创建餐厅标记图标
        let markerIcon
        
        try {
          // 尝试使用自定义SVG图标
          console.log(`🎨 为餐厅 "${location.name}" 创建自定义SVG图标`)
          markerIcon = new this.AMap.Icon({
            image: 'data:image/svg+xml;base64,' + btoa(`
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="10" fill="#FF6B35" stroke="#fff" stroke-width="2"/>
                <circle cx="12" cy="12" r="6" fill="#fff"/>
                <circle cx="12" cy="12" r="3" fill="#FF6B35"/>
              </svg>
            `),
            size: new this.AMap.Size(24, 24),
            imageOffset: new this.AMap.Pixel(-12, -12)
          })
          console.log(`✅ 餐厅 "${location.name}" SVG图标创建成功`)
        } catch (error) {
          console.warn(`❌ 餐厅 "${location.name}" 自定义SVG图标创建失败，使用备选图标:`, error)
          // 备选方案：使用高德地图内置图标
          markerIcon = new this.AMap.Icon({
            image: '//a.amap.com/jsapi_demos/static/demo-center/icons/poi-marker-red.png',
            size: new this.AMap.Size(25, 34),
            imageOffset: new this.AMap.Pixel(-13, -34)
          })
          console.log(`🔄 餐厅 "${location.name}" 使用备选图标`)
        }

        const marker = new this.AMap.Marker({
          position: position,
          icon: markerIcon,
          title: location.name,
          zIndex: 100,
          extData: { location: location, index: index } // 存储额外数据
        })
        
        console.log(`📍 餐厅标记创建完成: ${location.name} at (${longitude}, ${latitude})`)
        
        this.map.add(marker)
        this.markers.push(marker)
        
        console.log(`✅ 餐厅标记已添加到地图: ${location.name}`)

        // 添加点击事件
        marker.on('click', () => {
          console.log(`🖱️ 点击了餐厅标记: ${location.name}`)
          this.showLocationInfo(location, position)
          this.$emit('markerClick', location)
        })
      })
      
      console.log(`总计添加 ${this.markers.length} 个餐厅标记`)
    },
    
    /**
     * @description 显示位置信息窗口
     */
    showLocationInfo(location, position) {
      const content = `
        <div class="info-window">
          <h4>🍴 ${location.name}</h4>
          <p class="address">📍 ${location.address}</p>
          <div class="coordinates">
            <p class="coord-info">📐 经度: ${position[0].toFixed(6)}</p>
            <p class="coord-info">📐 纬度: ${position[1].toFixed(6)}</p>
          </div>
          ${location.rating ? `<p class="rating">⭐ ${location.rating}</p>` : ''}
          ${location.distance ? `<p class="distance">📏 ${location.distance}</p>` : ''}
          ${location.price_level ? `<p class="price">💰 ${location.price_level}</p>` : ''}
          ${location.tel ? `<p class="phone">📞 ${location.tel}</p>` : ''}
          <div class="info-actions">
            ${location.map_url ? `<a href="${location.map_url}" target="_blank" class="info-btn">导航</a>` : ''}
            ${location.tel ? `<a href="tel:${location.tel}" class="info-btn">电话</a>` : ''}
          </div>
        </div>
      `
      
      this.infoWindow.setContent(content)
      this.infoWindow.open(this.map, position)
    },
    
    /**
     * @description 适应所有标记的视野
     */
    fitToMarkers() {
      if (!this.map || this.markers.length === 0) return
      
      const allMarkers = [...this.markers]
      if (this.userMarker) {
        allMarkers.push(this.userMarker)
      }
      
      this.map.setFitView(allMarkers, false, [20, 20, 20, 20])
    }
  }
}
</script>

<style scoped>
.amap-container {
  width: 100%;
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.map-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, #6C63FF 0%, #5A52FF 100%);
  color: white;
}

.map-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.map-icon {
  font-size: 18px;
}

.map-controls {
  display: flex;
  gap: 8px;
}

.control-btn {
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  color: white;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.control-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.3);
}

.control-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.map-wrapper {
  position: relative;
  height: 400px;
}

.amap-element {
  width: 100%;
  height: 100%;
}

.map-loading, .map-error {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.9);
  z-index: 1000;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #6C63FF;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.retry-btn {
  padding: 8px 16px;
  background: #6C63FF;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  margin-top: 8px;
}

.map-legend {
  display: flex;
  gap: 16px;
  padding: 12px 20px;
  background: #f8f9fa;
  border-top: 1px solid #e9ecef;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  background: white;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.legend-marker {
  font-size: 18px;
  filter: drop-shadow(1px 1px 2px rgba(0, 0, 0, 0.2));
}

.legend-text {
  font-size: 13px;
  color: #444;
  font-weight: 500;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 信息窗口样式 */
:global(.amap-info-content) {
  border-radius: 8px !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
}

:global(.info-window) {
  padding: 12px;
  min-width: 200px;
}

:global(.info-window h4) {
  margin: 0 0 8px 0;
  color: #333;
  font-size: 14px;
}

:global(.info-window p) {
  margin: 4px 0;
  font-size: 12px;
  color: #666;
}

:global(.coordinates) {
  background: #f5f5f5;
  padding: 8px;
  border-radius: 4px;
  margin: 8px 0;
  border-left: 3px solid #6C63FF;
}

:global(.coord-info) {
  margin: 2px 0 !important;
  font-family: 'Courier New', monospace;
  font-size: 11px !important;
  color: #2c3e50 !important;
  font-weight: 500;
}

:global(.info-actions) {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

:global(.info-btn) {
  padding: 4px 8px;
  background: #6C63FF;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  font-size: 12px;
  transition: background 0.3s ease;
}

:global(.info-btn:hover) {
  background: #5A52FF;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .map-header {
    flex-direction: column;
    gap: 12px;
  }
  
  .map-controls {
    width: 100%;
    justify-content: center;
  }
  
  .map-wrapper {
    height: 300px;
  }
  
  .map-legend {
    flex-direction: column;
    gap: 8px;
  }
}
</style> 
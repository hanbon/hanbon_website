<template>
    <div class="search-wrapper">
        <div class="content-container" :class="{ 'has-results': hasResults }">
            <!-- 搜索输入区域 -->
            <div class="search-input-container" :class="{ 'sticky': hasResults }">
                <img :src="logoSrc" alt="Logo" class="logo">
                <!-- <h1>汉邦美食搜索</h1> -->
                <!-- <h1>汉邦美食搜索</h1> -->
                <div class="input-group">
                    <div class="search-input-wrapper">
                        <input 
                            type="text" 
                            v-model="searchText"
                            placeholder="输入食物名称..."
                            @keyup.enter="debouncedSearch"
                            @input="handleInput"
                            :aria-invalid="!!inputError"
                            :aria-describedby="inputError ? 'error-message' : undefined"
                        >
                        <div class="input-buttons">
                            <button class="icon-btn image-upload-btn" @click="triggerImageUpload">
                                <ion-icon name="camera-outline"></ion-icon>
                                <input 
                                    type="file" 
                                    ref="imageInput" 
                                    accept="image/*" 
                                    style="display: none" 
                                    @change="handleImageUpload"
                                >
                            </button>
                            <button class="search-btn" @click="debouncedSearch">
                                <ion-icon name="search-outline"></ion-icon>
                            </button>
                        </div>
                        <!-- 添加建议列表 -->
                        <div class="suggestions-list" v-if="suggestions.length && showSuggestions">
                            <div 
                                v-for="suggestion in suggestions" 
                                :key="suggestion"
                                class="suggestion-item"
                                @click="selectSuggestion(suggestion)"
                            >
                                {{ suggestion }}
                            </div>
                        </div>
                    </div>
                    <!-- <div class="button-row">
                        <button @click="debouncedSearch">搜索</button>
                    </div> -->
                </div>
                
                <!-- 错误提示 -->
                <div v-if="inputError" id="error-message" class="error-message">
                    {{ inputError }}
                </div>

                <!-- 今日推荐 -->
                <div class="daily-recommendations" v-if="!hasResults">
                    <h3>今日推荐 <span class="subtitle">基于天气：{{ weather.city }} {{ weather.temperature }}°C {{ weather.weather_icon }} {{ weather.weather }}</span></h3>
                    <div class="recommendation-cards">
                        <div v-for="item in dailyRecommendations" 
                             :key="item.name" 
                             class="recommendation-card"
                             @click="selectFood(item.name)">
                            <img :src="item.image" :alt="item.name">
                            <div class="card-content">
                                <h4>{{item.name}}</h4>
                                <p>{{item.description}}</p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 搜索历史 -->
                <div class="search-history" v-if="!hasResults && searchHistory.length">
                    <h3>最近搜索</h3>
                    <div class="history-tags">
                        <span v-for="item in searchHistory" 
                              :key="item" 
                              @click="selectHistoryItem(item)"
                              class="history-tag"
                              tabindex="0"
                              role="button"
                              @keyup.enter="selectHistoryItem(item)">
                            {{ item }}
                        </span>
                    </div>
                </div>
                
                <!-- 添加菜谱来源切换按钮 -->
                <div class="recipe-source-toggle">
                    <button 
                        :class="{ active: recipeSource === 'juhe' }"
                        @click="recipeSource = 'juhe'"
                    >
                        聚合数据
                    </button>
                    <button 
                        :class="{ active: recipeSource === 'qwen' }"
                        @click="recipeSource = 'qwen'"
                    >
                        AI生成
                    </button>
                </div>
                
                <!-- 常用食物快捷选择区域 -->
                <div class="quick-food-tags">
                    <div 
                        v-for="food in commonFoods" 
                        :key="food.name"
                        class="food-tag"
                        @click="selectFood(food.name)"
                    >
                        <ion-icon :name="food.icon"></ion-icon>
                        {{ food.name }}
                    </div>
                </div>
            </div>

            <!-- 搜索结果区域 -->
            <div v-if="hasResults" class="results-container">
                <div class="results-content">
                    <div class="recipe-container">
                        <!-- 卡路里面板 -->
                        <div class="calorie-panel" :class="{ 'loading': isLoading }">
                            <h3>卡路里信息</h3>
                            <div v-if="isLoading" class="skeleton-loading">
                                <div class="skeleton" style="height: 24px; width: 80%;"></div>
                            </div>
                            <div v-else class="calorie-info" v-html="calorieInfo || '加载中...'"></div>
                        </div>

                        <!-- 食谱内容 -->
                        <div class="recipe-content">
                            <h2 class="recipe-title">{{ searchText }}的详细食谱</h2>
                            <div v-if="isLoading" class="skeleton-loading">
                                <div v-for="i in 5" :key="i" class="skeleton" :style="{
                                    height: '20px',
                                    width: `${Math.random() * 40 + 60}%`,
                                    marginBottom: '10px'
                                }"></div>
                            </div>
                            <div v-else class="recipe-details markdown-body" v-html="recipeDetails"></div>
                        </div>

                        <!-- 配图面板 -->
                        <div class="recipe-image-panel">
                            <h3>美食图片</h3>
                            <div class="recipe-images" :class="{ 'loading': isLoading }">
                                <div v-if="isLoading" class="skeleton" style="height: 300px;"></div>
                                <img 
                                    v-else-if="foodImage" 
                                    :src="foodImage" 
                                    alt="食物图片"
                                    @load="onImageLoad"
                                    :class="{ 'loaded': imageLoaded }"
                                >
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 添加定时器组件 -->
            <div v-if="hasResults" class="timer-container">
                <div class="timer" v-if="showTimer">
                    <div class="timer-display">{{formatTime(timerSeconds)}}</div>
                    <div class="timer-controls">
                        <button @click="startTimer" v-if="!timerRunning">开始</button>
                        <button @click="pauseTimer" v-else>暂停</button>
                        <button @click="resetTimer">重置</button>
                    </div>
                </div>
                <button class="timer-toggle" @click="toggleTimer">
                    <ion-icon :name="showTimer ? 'timer-outline' : 'timer'"></ion-icon>
                </button>
            </div>

            <!-- 返回顶部按钮 -->
            <div v-show="showBackToTop" class="back-to-top" @click="scrollToTop" role="button" tabindex="0">
                <ion-icon name="arrow-up-outline"></ion-icon>
            </div>
        </div>
    </div>
</template>

<script>
import { marked } from 'marked';
import { debounce } from 'lodash-es';

/**
 * @description 搜索组件，用于食物搜索和食谱展示
 */
export default {
    name: 'SearchComponent',
    data() {
        return {
            logoSrc: require('@/assets/hanbon_logo.png'),
            searchText: '',
            hasResults: false,
            recipeSource: 'juhe',
            calorieInfo: '',
            recipeDetails: '',
            foodImage: '',
            isLoading: false,
            allFoods: [
                // 主食类
                { name: '米饭', icon: 'restaurant-outline' },
                { name: '馒头', icon: 'restaurant-outline' },
                { name: '面条', icon: 'restaurant-outline' },
                { name: '饺子', icon: 'restaurant-outline' },
                { name: '包子', icon: 'restaurant-outline' },
                { name: '粥', icon: 'restaurant-outline' },
                { name: '炒饭', icon: 'restaurant-outline' },
                { name: '炒面', icon: 'restaurant-outline' },
                { name: '拉面', icon: 'restaurant-outline' },
                { name: '烩面', icon: 'restaurant-outline' },

                // 肉类菜品
                { name: '红烧肉', icon: 'restaurant-outline' },
                { name: '糖醋排骨', icon: 'restaurant-outline' },
                { name: '宫保鸡丁', icon: 'restaurant-outline' },
                { name: '回锅肉', icon: 'restaurant-outline' },
                { name: '东坡肉', icon: 'restaurant-outline' },
                { name: '辣子鸡', icon: 'restaurant-outline' },
                { name: '酱爆鸭丁', icon: 'restaurant-outline' },
                { name: '红烧排骨', icon: 'restaurant-outline' },
                { name: '可乐鸡翅', icon: 'restaurant-outline' },
                { name: '烤鸭', icon: 'restaurant-outline' },
                { name: '酸菜鱼', icon: 'fish-outline' },
                { name: '水煮鱼', icon: 'fish-outline' },
                { name: '清蒸鲈鱼', icon: 'fish-outline' },
                { name: '红烧带鱼', icon: 'fish-outline' },
                { name: '麻辣香锅', icon: 'restaurant-outline' },
                { name: '烤肉', icon: 'restaurant-outline' },
                { name: '羊肉串', icon: 'restaurant-outline' },
                { name: '酱牛肉', icon: 'restaurant-outline' },
                { name: '卤鸭', icon: 'restaurant-outline' },
                { name: '烧鸡', icon: 'restaurant-outline' },

                // 素菜
                { name: '青椒炒蛋', icon: 'egg-outline' },
                { name: '番茄炒蛋', icon: 'egg-outline' },
                { name: '麻婆豆腐', icon: 'leaf-outline' },
                { name: '地三鲜', icon: 'leaf-outline' },
                { name: '炒青菜', icon: 'leaf-outline' },
                { name: '蒜蓉菠菜', icon: 'leaf-outline' },
                { name: '干煸四季豆', icon: 'leaf-outline' },
                { name: '炒空心菜', icon: 'leaf-outline' },
                { name: '炒韭菜', icon: 'leaf-outline' },
                { name: '炒白菜', icon: 'leaf-outline' },

                // 汤类
                { name: '番茄蛋汤', icon: 'restaurant-outline' },
                { name: '紫菜蛋汤', icon: 'restaurant-outline' },
                { name: '西红柿牛腩汤', icon: 'restaurant-outline' },
                { name: '排骨汤', icon: 'restaurant-outline' },
                { name: '鸡汤', icon: 'restaurant-outline' },
                { name: '羊肉汤', icon: 'restaurant-outline' },
                { name: '海鲜汤', icon: 'restaurant-outline' },
                { name: '冬瓜排骨汤', icon: 'restaurant-outline' },
                { name: '萝卜牛腩汤', icon: 'restaurant-outline' },
                { name: '玉米排骨汤', icon: 'restaurant-outline' },

                // 小吃
                { name: '春卷', icon: 'restaurant-outline' },
                { name: '锅贴', icon: 'restaurant-outline' },
                { name: '煎饺', icon: 'restaurant-outline' },
                { name: '炸鸡', icon: 'restaurant-outline' },
                { name: '薯条', icon: 'restaurant-outline' },
                { name: '炸串', icon: 'restaurant-outline' },
                { name: '炸酱面', icon: 'restaurant-outline' },
                { name: '肉夹馍', icon: 'restaurant-outline' },
                { name: '煎包', icon: 'restaurant-outline' },
                { name: '生煎', icon: 'restaurant-outline' },

                // 川菜
                { name: '麻婆豆腐', icon: 'restaurant-outline' },
                { name: '回锅肉', icon: 'restaurant-outline' },
                { name: '鱼香肉丝', icon: 'restaurant-outline' },
                { name: '宫保鸡丁', icon: 'restaurant-outline' },
                { name: '水煮牛肉', icon: 'restaurant-outline' },
                { name: '夫妻肺片', icon: 'restaurant-outline' },
                { name: '辣子鸡', icon: 'restaurant-outline' },
                { name: '毛血旺', icon: 'restaurant-outline' },
                { name: '麻辣兔头', icon: 'restaurant-outline' },
                { name: '干煸四季豆', icon: 'restaurant-outline' },

                // 粤菜
                { name: '白切鸡', icon: 'restaurant-outline' },
                { name: '烧鹅', icon: 'restaurant-outline' },
                { name: '叉烧', icon: 'restaurant-outline' },
                { name: '虾饺', icon: 'restaurant-outline' },
                { name: '蒸排骨', icon: 'restaurant-outline' },
                { name: '蚝油生菜', icon: 'restaurant-outline' },
                { name: '清蒸鱼', icon: 'fish-outline' },
                { name: '咕噜肉', icon: 'restaurant-outline' },
                { name: '豉汁蒸排骨', icon: 'restaurant-outline' },
                { name: '白灼虾', icon: 'restaurant-outline' }

                // ... 更多食物
            ],
            commonFoods: [], // 用于存储随机选择的食物
            imageLoaded: false,
            searchHistory: [],
            inputError: '',
            showBackToTop: false,
            isRecording: false,
            weather: {
                city: '长沙',
                temperature: 25,
                weather: '晴朗',
                weather_icon: '☀️'
            },
            dailyRecommendations: [],
            showTimer: false,
            timerSeconds: 0,
            timerRunning: false,
            timerInterval: null,
            suggestions: [],
            showSuggestions: false,
        }
    },
    created() {
        // 添加防抖处理
        this.debouncedSearch = debounce(this.performSearch, 300);
        // 从localStorage加载搜索历史
        this.loadSearchHistory();
        // 随机选择20个食物
        this.updateRandomFoods();
        // 获取天气推荐
        this.fetchWeatherRecommendations();
    },
    mounted() {
        window.addEventListener('scroll', this.handleScroll);
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.search-input-wrapper')) {
                this.showSuggestions = false;
            }
        });
    },
    beforeUnmount() {
        window.removeEventListener('scroll', this.handleScroll);
        document.removeEventListener('click', this.handleClickOutside);
    },
    methods: {
        /**
         * @description 加载搜索历史
         */
        loadSearchHistory() {
            const history = localStorage.getItem('searchHistory');
            if (history) {
                this.searchHistory = JSON.parse(history);
            }
        },

        /**
         * @description 保存搜索历史
         * @param {string} searchTerm - 搜索词
         */
        saveToHistory(searchTerm) {
            if (!this.searchHistory.includes(searchTerm)) {
                this.searchHistory.unshift(searchTerm);
                if (this.searchHistory.length > 10) {
                    this.searchHistory.pop();
                }
                localStorage.setItem('searchHistory', JSON.stringify(this.searchHistory));
            }
        },

        /**
         * @description 处理流式响应数据
         * @param {Response} response - 响应对象
         * @param {Function} onData - 数据处理回调
         */
        async processStreamResponse(response, onData) {
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';
            let isReading = true;
            
            try {
                while (isReading) {
                    const {value, done} = await reader.read();
                    if (done) {
                        isReading = false;
                        break;
                    }
                    
                    buffer += decoder.decode(value, {stream: true});
                    const lines = buffer.split('\n');
                    buffer = lines.pop() || '';
                    
                    for (const line of lines) {
                        const cleanLine = line.replace(/^data:\s*/, '').trim();
                        if (cleanLine && !cleanLine.startsWith('Error:')) {
                            onData(cleanLine);
                        }
                    }
                }
                
                if (buffer) {
                    const cleanBuffer = buffer.replace(/^data:\s*/, '').trim();
                    if (cleanBuffer && !cleanBuffer.startsWith('Error:')) {
                        onData(cleanBuffer);
                    }
                }
            } catch (error) {
                console.error('Error processing stream:', error);
                throw error;
            } finally {
                reader.releaseLock();
            }
        },

        /**
         * @description 执行搜索操作
         */
        async performSearch() {
            if (!this.searchText.trim()) {
                this.inputError = '请输入搜索内容';
                return;
            }

            this.inputError = '';
            this.isLoading = true;
            this.hasResults = true;
            this.imageLoaded = false;
            this.foodImage = '';

            try {
                // 保存到搜索历史
                this.saveToHistory(this.searchText);

                // 并行请求处理
                const [calorieResponse, recipeResponse] = await Promise.all([
                    this.fetchCalorieInfo(),
                    this.fetchRecipeInfo()
                ]);

                // 单独处理图片请求
                await this.fetchFoodImage();

                if (calorieResponse.ok) {
                    const data = await calorieResponse.json();
                    this.calorieInfo = data.content;
                }

                if (recipeResponse.ok) {
                    this.recipeDetails = '';
                    let markdownContent = '';
                    await this.processStreamResponse(recipeResponse, 
                        content => {
                            if (content) {
                                markdownContent += content + '\n';
                                this.recipeDetails = marked(markdownContent);
                            }
                        }
                    );
                }

            } catch (error) {
                console.error('搜索出错:', error);
                if (error.response) {
                    this.showError(`请求失败: ${error.response.data.message || '未知错误'}`);
                } else if (error.request) {
                    this.showError('网络请求失败，请检查网络连接');
                } else {
                    this.showError('发生未知错误，请稍后重试');
                }
            } finally {
                this.isLoading = false;
            }
        },

        /**
         * @description 显示错误信息
         * @param {string} message - 错误信息
         */
        showError(message) {
            // 这里可以使用你的UI框架的提示组件，比如Element UI的Message组件
            // 如果没有UI框架，可以简单设置error状态
            this.inputError = message;
        },

        /**
         * @description 选择快捷食物标签
         * @param {string} food - 食物名称
         */
        selectFood(food) {
            this.searchText = food;
            this.performSearch();
            // 选择食物后更新随机列表
            this.updateRandomFoods();
        },

        async getRecipeRecommendation(food) {
            try {
                const response = await fetch(`${process.env.VUE_APP_API_BASE_URL}/get_recipe?food=${encodeURIComponent(food)}`);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                // 返回 response 对象而不是文本
                return response;
            } catch (error) {
                console.error('Recipe request failed:', error);
                return null;
            }
        },

        async displayRecipe(food, resultsDiv) {
            let response;
            if (this.recipeSource === 'qwen') {
                response = await fetch(`${process.env.VUE_APP_API_BASE_URL}/get_qwen_recipe?food=${encodeURIComponent(food)}`);
            } else {
                response = await this.getRecipeRecommendation(food);
            }

            if (response) {
                // 获取食谱详细内容区域
                const recipeDetails = resultsDiv.querySelector('.recipe-details');

                try {
                    const reader = response.body.getReader();
                    const decoder = new TextDecoder();
                    let buffer = '';

                    const processStream = async () => {
                        const { value, done } = await reader.read();
                        if (done) return;

                        buffer += decoder.decode(value, { stream: true });
                        const lines = buffer.split('\n');
                        
                        buffer = lines.pop() || '';
                        
                        for (const line of lines) {
                            const cleanLine = line.replace(/data:\s*/g, '').trim();
                            if (cleanLine) {
                                await this.simulateStreamOutput(cleanLine, recipeDetails);
                            }
                        }

                        await processStream();
                    };

                    await processStream();
                    
                    if (buffer) {
                        const cleanBuffer = buffer.replace(/data:\s*/g, '').trim();
                        if (cleanBuffer) {
                            await this.simulateStreamOutput(cleanBuffer, recipeDetails);
                        }
                    }
                } catch (error) {
                    console.error('Error reading stream:', error);
                    recipeDetails.textContent = '获取食谱信息失败，请稍后重试...';
                }
            }
        },

        async processStreams(items, resultsDiv) {
            // 创建所有流的容器元素
            const streamElements = items.map(() => {
                const p = document.createElement('p');
                resultsDiv.appendChild(p);
                return p;
            });

            // 创建流处理任务
            const streamTasks = items.map((item, index) => {
                return async () => {
                    await this.simulateStreamOutput(item, streamElements[index]);
                };
            });

            // 使用队列处理流
            this.streamQueue = [...streamTasks];
            await this.processStreamQueue();
        },

        async processStreamQueue() {
            while (this.streamQueue.length > 0 && this.activeStreams < this.maxConcurrent) {
                const task = this.streamQueue.shift();
                this.activeStreams++;
                
                task().finally(() => {
                    this.activeStreams--;
                    this.processStreamQueue();
                });
            }
        },

        async simulateStreamOutput(text, element) {
            const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
            let currentText = '';
            
            // Create a span for the cursor
            const cursor = document.createElement('span');
            cursor.className = 'cursor';
            cursor.textContent = '▋';

            // 创建新的段落元素
            const p = document.createElement('p');
            element.appendChild(p);
            p.appendChild(cursor);

            // 检查内容类型并设置相应的样式
            if (text.startsWith('**') && text.includes('**\n')) {
                // 这是一个标题
                const titleParts = text.split('\n');
                const title = titleParts[0].replace(/\*\*/g, '');
                const content = titleParts.slice(1).join('\n');

                // 创建标题元素
                const strong = document.createElement('strong');
                element.insertBefore(strong, p);
                
                // 输出标题
                for (let char of title) {
                    currentText += char;
                    strong.textContent = currentText;
                    await delay(50 + Math.random() * 50);
                }

                // 重置当前文本，准备输出内容
                currentText = '';
                
                // 输出内容
                if (content) {
                    // 根据内容类型设置段落的data-type
                    if (title.includes('主料')) {
                        p.setAttribute('data-type', 'ingredients');
                    } else if (title.includes('调料')) {
                        p.setAttribute('data-type', 'seasonings');
                    } else if (title.includes('小贴士') || title.includes('特色')) {
                        p.setAttribute('data-type', 'tips');
                    } else if (title.includes('步骤')) {
                        p.setAttribute('data-type', 'step');
                    }

                    for (let char of content) {
                        currentText += char;
                        if (char === '\n') {
                            p.innerHTML = currentText.replace(/\n/g, '<br>');
                        } else {
                            p.innerHTML = currentText.replace(/\n/g, '<br>');
                        }
                        p.appendChild(cursor);
                        await delay(50 + Math.random() * 50);
                    }
                }
            } else {
                // 普通内容
                for (let char of text) {
                    currentText += char;
                    if (char === '\n') {
                        p.innerHTML = currentText.replace(/\n/g, '<br>');
                    } else {
                        p.innerHTML = currentText.replace(/\n/g, '<br>');
                    }
                    p.appendChild(cursor);
                    await delay(50 + Math.random() * 50);
                }
            }
            
            // 移除光标
            cursor.remove();
            
            // 添加完成动画
            p.classList.add('complete');
        },
        getInitialTemplate(food) {
            return `
                <div class="recipe-container">
                    <!-- 卡路里面板 -->
                    <div class="calorie-panel">
                        <h3>卡路里面板</h3>
                        <div class="calorie-info">
                            <!-- 卡路里信息将在这里显示 -->
                        </div>
                    </div>

                    <!-- 食谱内容 -->
                    <div class="recipe-content">
                        <h2 class="recipe-title">${food}的详细食谱</h2>
                        <div class="recipe-details">
                            <!-- 食谱详细内容将在这里显示 -->
                        </div>
                    </div>

                    <!-- 配图面板 -->
                    <div class="recipe-image-panel">
                        <h3>配图面板</h3>
                        <div class="recipe-images">
                            <!-- 食谱图片将在这里显示 -->
                        </div>
                    </div>
                </div>
            `;
        },
        onImageLoad() {
            this.imageLoaded = true;
        },
        /**
         * @description 选择历史搜索项
         * @param {string} item - 搜索历史项
         */
        selectHistoryItem(item) {
            this.searchText = item;
            this.debouncedSearch();
        },

        /**
         * @description 获取卡路里信息
         * @returns {Promise} 卡路里信息的响应
         */
        async fetchCalorieInfo() {
            return fetch(`${process.env.VUE_APP_API_BASE_URL}/call_openai?query=${encodeURIComponent(this.searchText)}`);
        },

        /**
         * @description 获取食谱信息
         * @returns {Promise} 食谱信息的响应
         */
        async fetchRecipeInfo() {
            const recipeEndpoint = this.recipeSource === 'qwen' ? 'get_qwen_recipe' : 'get_recipe';
            return fetch(`${process.env.VUE_APP_API_BASE_URL}/${recipeEndpoint}?food=${encodeURIComponent(this.searchText)}`);
        },

        /**
         * @description 获取食物图片
         */
        async fetchFoodImage() {
            try {
                const response = await fetch(`${process.env.VUE_APP_API_BASE_URL}/generate_food_image_baidu?food=${encodeURIComponent(this.searchText)}&limit=1&page=1`);
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                if (data.code === 200 && data.data.length > 0) {
                    this.foodImage = data.data[0];  // 直接使用第一张图片的URL
                } else {
                    console.error('获取图片失败:', data.msg);
                    this.foodImage = '';  // 清空图片
                }
            } catch (error) {
                console.error('获取图片失败:', error);
                this.foodImage = '';  // 清空图片
            }
        },

        /**
         * @description 处理滚动事件
         */
        handleScroll() {
            this.showBackToTop = window.scrollY > 300;
        },

        /**
         * @description 滚动到顶部
         */
        scrollToTop() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        },

        /**
         * @description 更新随机食物列表
         */
        updateRandomFoods() {
            const shuffled = [...this.allFoods].sort(() => 0.5 - Math.random());
            this.commonFoods = shuffled.slice(0, 20);
        },

        /**
         * @description 开始语音搜索
         */
        async startVoiceSearch() {
            // 检查浏览器是否支持语音识别
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRecognition) {
                this.showError('您的浏览器不支持语音识别功能');
                return;
            }

            try {
                const recognition = new SpeechRecognition();
                recognition.continuous = false;
                recognition.interimResults = false;
                recognition.lang = 'zh-CN';

                this.isRecording = true;

                recognition.onresult = (event) => {
                    const transcript = event.results[0][0].transcript;
                    this.searchText = transcript;
                    this.debouncedSearch();
                };

                recognition.onerror = (event) => {
                    this.isRecording = false;
                    this.showError('语音识别失败: ' + event.error);
                };

                recognition.onend = () => {
                    this.isRecording = false;
                };

                recognition.start();
            } catch (error) {
                this.isRecording = false;
                this.showError('启动语音识别失败: ' + error.message);
            }
        },

        /**
         * @description 触发图片上传
         */
        triggerImageUpload() {
            this.$refs.imageInput.click();
        },

        /**
         * @description 处理图片上传
         */
        async handleImageUpload(event) {
            const file = event.target.files[0];
            if (!file) return;

            const formData = new FormData();
            formData.append('image', file);

            try {
                const response = await fetch(`${process.env.VUE_APP_API_BASE_URL}/recognize_food`, {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();
                if (data.success) {
                    this.searchText = data.foodName;
                    this.debouncedSearch();
                }
            } catch (error) {
                console.error('图片识别失败:', error);
                this.showError('图片识别失败，请重试');
            }
        },

        /**
         * @description 格式化时间
         */
        formatTime(seconds) {
            const minutes = Math.floor(seconds / 60);
            const remainingSeconds = seconds % 60;
            return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
        },

        /**
         * @description 开始定时器
         */
        startTimer() {
            if (!this.timerRunning) {
                this.timerRunning = true;
                this.timerInterval = setInterval(() => {
                    if (this.timerSeconds > 0) {
                        this.timerSeconds--;
                    } else {
                        this.stopTimer();
                        // 播放提示音
                        new Audio('/timer-done.mp3').play();
                    }
                }, 1000);
            }
        },

        /**
         * @description 暂停定时器
         */
        pauseTimer() {
            this.timerRunning = false;
            clearInterval(this.timerInterval);
        },

        /**
         * @description 重置定时器
         */
        resetTimer() {
            this.timerSeconds = 0;
            this.pauseTimer();
        },

        /**
         * @description 切换定时器显示
         */
        toggleTimer() {
            this.showTimer = !this.showTimer;
            if (!this.showTimer) {
                this.pauseTimer();
            }
        },

        /**
         * @description 获取天气推荐
         */
        async fetchWeatherRecommendations() {
            try {
                const response = await fetch(`${process.env.VUE_APP_API_BASE_URL}/get_weather_recommendations`);
                const data = await response.json();
                
                if (data.success) {
                    this.weather = data.weather;
                    this.dailyRecommendations = data.recommendations.map(item => ({
                        ...item,
                        image: item.image || ''  // 确保有默认值
                    }));
                } else {
                    console.error('获取天气推荐失败:', data.error);
                    // 设置默认推荐
                    this.dailyRecommendations = [
                        {
                            name: '清爽凉面',
                            image: '',
                            description: '清凉解暑的夏日美食'
                        },
                        {
                            name: '水果沙拉',
                            image: '',
                            description: '营养清爽的健康美食'
                        }
                    ];
                }
            } catch (error) {
                console.error('获取天气推荐失败:', error);
                // 设置默认推荐
                this.dailyRecommendations = [
                    {
                        name: '清爽凉面',
                        image: '',
                        description: '清凉解暑的夏日美食'
                    },
                    {
                        name: '水果沙拉',
                        image: '',
                        description: '营养清爽的健康美食'
                    }
                ];
            }
        },

        /**
         * @description 处理输入事件，生成搜索建议
         */
        handleInput() {
            if (!this.searchText.trim()) {
                this.suggestions = [];
                this.showSuggestions = false;
                return;
            }

            // 从所有食物中筛选匹配的建议
            this.suggestions = this.allFoods
                .map(food => food.name)
                .filter(name => name.includes(this.searchText))
                .slice(0, 5);
            
            this.showSuggestions = true;
        },

        /**
         * @description 选择建议项
         * @param {string} suggestion - 选中的建议项
         */
        selectSuggestion(suggestion) {
            this.searchText = suggestion;
            this.showSuggestions = false;
            this.debouncedSearch();
        },

        // 添加点击外部关闭建议列表的处理
        mounted() {
            document.addEventListener('click', (e) => {
                if (!e.target.closest('.search-input-wrapper')) {
                    this.showSuggestions = false;
                }
            });
        },

        beforeUnmount() {
            document.removeEventListener('click', this.handleClickOutside);
        },
    }
}
</script>

<style scoped>
.search-wrapper {
    min-height: 100vh;
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: flex-start;
    padding: 20px;
    box-sizing: border-box;
    background: transparent;
}

.content-container {
    width: 100%;
    max-width: 1100px;
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: 5vh;
    transition: all 0.4s ease;
    gap: 20px;
}

.content-container.has-results {
    margin-top: 20px;
}

/* 搜索框容器 */
.search-input-container {
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 30px;
    width: 90%;
    max-width: 600px;
    text-align: center;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
}

.search-input-container.sticky {
    padding: 15px;
    max-width: 1100px;
    border-radius: 16px;
    margin-bottom: 20px;
}

/* Logo和标题 */
.logo {
    width: 60px;
    height: 60px;
    margin-bottom: 10px;
    transition: all 0.3s ease;
}

.sticky .logo {
    width: 40px;
    height: 40px;
    margin-bottom: 5px;
}

h1 {
    font-size: 24px;
    color: #333;
    margin: 10px 0;
    transition: all 0.3s ease;
}

.sticky h1 {
    font-size: 18px;
    margin: 5px 0;
}

/* 搜索输入框 */
.input-group {
    display: flex;
    gap: 10px;
    margin: 20px 0;
}

input {
    flex: 1;
    padding: 12px 20px;
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    font-size: 16px;
    transition: all 0.3s ease;
}

input:focus {
    outline: none;
    border-color: #0071e3;
    box-shadow: 0 0 0 2px rgba(0, 113, 227, 0.2);
}

button {
    padding: 12px 24px;
    background: #0071e3;
    color: white;
    border: none;
    border-radius: 10px;
    font-size: 16px;
    cursor: pointer;
    transition: all 0.3s ease;
}

button:hover {
    background: #0077ED;
    transform: translateY(-1px);
}

/* 快捷标签 */
.quick-food-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: center;
    margin-top: 15px;
}

.food-tag {
    padding: 6px 12px;
    background: rgba(0, 113, 227, 0.1);
    border-radius: 20px;
    color: #0071e3;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 4px;
}

.food-tag:hover {
    background: rgba(0, 113, 227, 0.2);
    transform: translateY(-1px);
}

/* 结果容器 */
.results-container {
    width: 100%;
    max-width: 1100px;
    opacity: 0;
    transform: translateY(20px);
    animation: slideIn 0.5s forwards;
}

@keyframes slideIn {
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.recipe-container {
    display: grid;
    grid-template-columns: minmax(300px, 1fr) minmax(300px, 1fr);
    grid-template-rows: auto 1fr;
    gap: 20px;
    padding: 30px;
}

.calorie-panel {
    grid-column: 1 / 2;
    grid-row: 1 / 2;
    min-height: 120px;
}

.recipe-content {
    grid-column: 1 / 2;
    grid-row: 2 / 3;
    max-height: calc(100vh - 300px);
    overflow-y: auto;
}

.recipe-image-panel {
    grid-column: 2 / 3;
    grid-row: 1 / 3;
    height: calc(100vh - 200px);
    display: flex;
    flex-direction: column;
}

.recipe-images {
    flex: 1;
    min-height: 400px;
    max-height: 100%;
}

/* 面板样式 */
.calorie-panel,
.recipe-content,
.recipe-image-panel {
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 20px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.calorie-panel h3 {
    color: #333;
    font-size: 20px;
    margin-bottom: 15px;
}

.calorie-info {
    font-size: 24px;
    color: #22c55e;
    font-weight: 600;
    text-align: center;
    padding: 15px;
    background: rgba(34, 197, 94, 0.1);
    border-radius: 12px;
    min-width: 200px;
}

/* 加载状态样式 */
.calorie-panel.loading .calorie-info {
    position: relative;
    overflow: hidden;
}

.calorie-panel.loading .calorie-info::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(
        90deg,
        rgba(255, 255, 255, 0) 0%,
        rgba(255, 255, 255, 0.5) 50%,
        rgba(255, 255, 255, 0) 100%
    );
    animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
    0% {
        transform: translateX(-100%);
    }
    100% {
        transform: translateX(100%);
    }
}

.recipe-content h2 {
    color: #333;
    font-size: 24px;
    margin-bottom: 20px;
    border-bottom: 2px solid #0071e3;
    padding-bottom: 10px;
}

/* 食谱详细内容样式 */
.recipe-details {
    text-align: left;
    line-height: 1.6;
}

/* Markdown 格式支持 */
.recipe-details strong,
.recipe-details b {
    display: block;
    color: #0071e3;
    font-size: 18px;
    margin: 20px 0 10px 0;
    padding-bottom: 5px;
    border-bottom: 1px solid rgba(0, 113, 227, 0.2);
}

.recipe-details p {
    margin: 10px 0;
    padding: 10px;
    background: rgba(255, 255, 255, 0.8);
    border-radius: 8px;
}

/* 主料和调料部分 - 通过内容识别 */
.recipe-details p:has(strong:contains("主料")),
.recipe-details p:has(strong:contains("调料")) {
    background: rgba(0, 113, 227, 0.05);
    padding: 15px;
    border-radius: 10px;
    margin: 10px 0;
}

/* 步骤部分 - 通过内容识别 */
.recipe-details p:has(strong:contains("步骤")) + p {
    padding: 10px 15px;
    margin: 5px 0;
    position: relative;
    background: rgba(255, 255, 255, 0.9);
}

/* 小贴士部分 - 通过内容识别 */
.recipe-details p:has(strong:contains("小贴士")) + p {
    background: rgba(34, 197, 94, 0.1);
    padding: 15px;
    border-radius: 10px;
    margin: 15px 0;
    position: relative;
}

.recipe-details p:has(strong:contains("小贴士")) + p::before {
    content: '💡';
    margin-right: 8px;
}

/* 列表样式 */
.recipe-details ul {
    list-style: none;
    padding: 0;
    margin: 10px 0;
}

.recipe-details li {
    padding: 8px 15px;
    margin: 5px 0;
    background: rgba(0, 113, 227, 0.05);
    border-radius: 8px;
}

/* 动画效果 */
.recipe-details p {
    opacity: 0;
    transform: translateY(10px);
    animation: fadeInUp 0.5s forwards;
}

@keyframes fadeInUp {
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* 暗色模式适配 */
@media (prefers-color-scheme: dark) {
    .recipe-content {
        background: rgba(255, 255, 255, 0.95);
    }
    
    .recipe-details strong {
        color: #0077ED;
    }
    
    .recipe-details p[data-type="ingredients"],
    .recipe-details p[data-type="seasonings"] {
        background: rgba(0, 113, 227, 0.08);
    }
    
    .recipe-details p[data-type="tips"] {
        background: rgba(34, 197, 94, 0.15);
    }
}

/* 移动端适配 */
@media (max-width: 768px) {
    .recipe-container {
        grid-template-columns: 1fr;
        grid-template-rows: auto auto auto;
    }

    .calorie-panel {
        grid-column: 1 / 2;
        grid-row: 1 / 2;
    }

    .recipe-content {
        grid-column: 1 / 2;
        grid-row: 2 / 3;
        max-height: none;
    }

    .recipe-image-panel {
        grid-column: 1 / 2;
        grid-row: 3 / 4;
        height: auto;
    }

    .recipe-images {
        height: 300px;
        min-height: 300px;
    }

    /* 移动端输入组件样式优化 */
    .input-group {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    .input-group input {
        width: 100%;
        height: 42px;
        margin-right: 0;  /* 移动端下清除右边距 */
    }

    .input-group .button-row {
        display: flex;
        gap: 8px;
        width: 100%;
    }

    .input-group .voice-btn,
    .input-group .image-upload-btn {
        width: 42px;
        height: 42px;
        padding: 0;
        flex: none;
    }

    .input-group button:last-child {
        flex: 1;
        height: 42px;
    }
}

.recipe-image-panel h3 {
    color: #333;
    font-size: 20px;
    margin-bottom: 15px;
    text-align: left;
}

.recipe-images img {
    width: 100%;
    height: 100%;
    object-fit: contain;
    object-position: center;
    transition: all 0.5s ease;
    opacity: 0;
    transform: scale(1.05);
    padding: 10px;
    box-sizing: border-box;
    background: white;
}

.recipe-images img.loaded {
    opacity: 1;
    transform: scale(1);
}

.recipe-images.loading {
    position: relative;
}

.recipe-images.loading::after {
    content: '加载中...';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    color: #666;
    font-size: 14px;
}

.recipe-images.loading::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(
        90deg,
        rgba(255, 255, 255, 0) 0%,
        rgba(255, 255, 255, 0.5) 50%,
        rgba(255, 255, 255, 0) 100%
    );
    animation: shimmer 1.5s infinite;
}

.loading {
    position: relative;
}

.loading::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(4px);
    display: flex;
    justify-content: center;
    align-items: center;
    border-radius: inherit;
}

/* 切换按钮样式 */
.recipe-source-toggle {
    display: flex;
    gap: 10px;
    justify-content: center;
    margin: 15px 0;
}

.recipe-source-toggle button {
    padding: 8px 16px;
    background: transparent;
    border: 1px solid #0071e3;
    color: #0071e3;
}

.recipe-source-toggle button.active {
    background: #0071e3;
    color: white;
}

/* 添加 markdown 样式 */
.markdown-body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    line-height: 1.6;
    word-wrap: break-word;
    padding: 15px;
}

.markdown-body h1,
.markdown-body h2,
.markdown-body h3,
.markdown-body h4,
.markdown-body h5,
.markdown-body h6 {
    margin-top: 24px;
    margin-bottom: 16px;
    font-weight: 600;
    line-height: 1.25;
}

.markdown-body strong {
    display: block;
    color: #0071e3;
    font-size: 18px;
    margin: 20px 0 10px 0;
    padding-bottom: 5px;
    border-bottom: 1px solid rgba(0, 113, 227, 0.2);
}

.markdown-body ul,
.markdown-body ol {
    padding-left: 2em;
    margin-top: 0;
    margin-bottom: 16px;
}

.markdown-body li {
    margin: 8px 0;
    padding: 8px 15px;
    background: rgba(0, 113, 227, 0.05);
    border-radius: 8px;
    list-style-position: inside;
}

.markdown-body li:before {
    content: "•";
    color: #0071e3;
    display: inline-block;
    width: 1em;
    margin-left: -1em;
}

.markdown-body p {
    margin-top: 0;
    margin-bottom: 16px;
    padding: 10px;
    background: rgba(255, 255, 255, 0.8);
    border-radius: 8px;
}

/* 特殊内容样式 */
.markdown-body p:has(strong:contains("主料")),
.markdown-body p:has(strong:contains("调料")) {
    background: rgba(0, 113, 227, 0.05);
}

.markdown-body p:has(strong:contains("小贴士")) {
    background: rgba(34, 197, 94, 0.1);
}

.markdown-body p:has(strong:contains("小贴士"))::before {
    content: '💡';
    margin-right: 8px;
}
</style>
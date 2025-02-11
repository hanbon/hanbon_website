<template>
    <div class="search-wrapper">
        <div class="content-container" :class="{ 'has-results': hasResults }">
            <!-- 搜索输入区域 -->
            <div class="search-input-container" :class="{ 'sticky': hasResults }">
                <img :src="logoSrc" alt="Logo" class="logo">
                <h1>汉邦美食搜索</h1>
                <div class="input-group">
                    <input 
                        type="text" 
                        v-model="searchText"
                        placeholder="输入食物名称..."
                        @keyup.enter="performSearch"
                    >
                    <button @click="performSearch">搜索</button>
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
                            <div class="calorie-info" v-html="calorieInfo || '加载中...'"></div>
                        </div>

                        <!-- 食谱内容 -->
                        <div class="recipe-content">
                            <h2 class="recipe-title">{{ searchText }}的详细食谱</h2>
                            <div class="recipe-details markdown-body" v-html="recipeDetails"></div>
                        </div>

                        <!-- 配图面板 -->
                        <div class="recipe-image-panel">
                            <h3>美食图片</h3>
                            <div class="recipe-images" :class="{ 'loading': isLoading }">
                                <img 
                                    v-if="foodImage" 
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
        </div>
    </div>
</template>

<script>
import { marked } from 'marked';

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
            commonFoods: [
                { name: '红烧肉', icon: 'restaurant-outline' },
                { name: '糖醋排骨', icon: 'nutrition-outline' },
                { name: '宫保鸡丁', icon: 'restaurant-outline' },
                { name: '麻婆豆腐', icon: 'leaf-outline' },
                { name: '水煮鱼', icon: 'fish-outline' },
                { name: '回锅肉', icon: 'restaurant-outline' },
                { name: '青椒炒蛋', icon: 'egg-outline' },
                { name: '番茄炒蛋', icon: 'nutrition-outline' }
            ],
            imageLoaded: false,
        }
    },
    methods: {
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
            if (!this.searchText) return;
            this.isLoading = true;
            this.hasResults = true;
            this.imageLoaded = false;
            this.foodImage = ''; // 重置图片
            
            try {
                // 获取卡路里信息
                const calorieResponse = await fetch(`${process.env.VUE_APP_API_BASE_URL}/call_openai?query=${encodeURIComponent(this.searchText)}`);
                if (calorieResponse.ok) {
                    const data = await calorieResponse.json();
                    this.calorieInfo = data.content;
                }

                // 获取食谱信息
                const recipeEndpoint = this.recipeSource === 'qwen' ? 
                    'get_qwen_recipe' : 'get_recipe';
                    
                const recipeResponse = await fetch(`${process.env.VUE_APP_API_BASE_URL}/${recipeEndpoint}?food=${encodeURIComponent(this.searchText)}`);
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
                
                // 获取食物图片
                const imageResponse = await fetch(`${process.env.VUE_APP_API_BASE_URL}/generate_food_image?food=${encodeURIComponent(this.searchText)}`);
                if (imageResponse.ok) {
                    await this.processStreamResponse(imageResponse, 
                        content => {
                            if (content && !content.startsWith('Error')) {
                                this.foodImage = `data:image/jpeg;base64,${content}`;
                            }
                        }
                    );
                }
                
            } catch (error) {
                console.error('搜索出错:', error);
                this.recipeDetails = '抱歉，获取数据时出现错误，请稍后重试。';
            } finally {
                this.isLoading = false;
            }
        },

        /**
         * @description 选择快捷食物标签
         * @param {string} food - 食物名称
         */
        selectFood(food) {
            this.searchText = food;
            this.performSearch();
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
        }
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
    max-width: 1200px;
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: 20vh;
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
    margin: 0 auto;
}

.search-input-container.sticky {
    padding: 15px;
    width: 100%;
    max-width: 1200px;
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
    max-width: 1200px;
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
    padding: 20px;
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

@media (max-width: 480px) {
    .search-input-container.sticky {
        padding: 10px;
    }

    .sticky .logo {
        width: 32px;
        height: 32px;
    }

    .sticky h1 {
        font-size: 16px;
    }

    .sticky .input-group {
        margin: 8px 0;
    }

    .sticky button {
        padding: 8px 16px;
        font-size: 14px;
    }
}

/* 加载动画 */
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
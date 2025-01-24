<template>
    <div class="search-wrapper">
        <div class="content-container" :class="{ 'has-results': hasResults }">
            <!-- 搜索输入区域 -->
            <div class="search-input-container" id="searchContainer">
                <img :src="logoSrc" alt="Logo" class="logo">
                <h1>hanbon 's AI Search</h1>
                <div class="input-group">
                    <input 
                        type="text" 
                        id="searchQuery" 
                        v-model="searchText"
                        placeholder="输入食物名称..."
                        @keyup.enter="performSearch"
                    >
                    <button @click="performSearch">Search</button>
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
            <div id="results" class="results-container" :class="{ 'show': hasResults }">
                <div class="results-content"></div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    data() {
        return {
            logoSrc: require('@/assets/hanbon_logo.png'),
            maxConcurrent: 5,
            activeStreams: 0,
            streamQueue: [],
            systemPrompt: "请简要回答以下问题，限制在20个字以内。",
            hasResults: false,
            searchText: '',
            commonFoods: [
                { name: '苹果', icon: 'nutrition-outline' },
                { name: '香蕉', icon: 'leaf-outline' },
                { name: '鸡胸肉', icon: 'restaurant-outline' },
                { name: '米饭', icon: 'fast-food-outline' },
                { name: '牛奶', icon: 'cafe-outline' },
                { name: '鸡蛋', icon: 'egg-outline' },
                { name: '三明治', icon: 'pizza-outline' },
                { name: '面包', icon: 'restaurant-outline' },
                { name: '牛肉', icon: 'restaurant-outline' },
                { name: '西兰花', icon: 'leaf-outline' }
            ]
        }
    },
    mounted() {
        const searchInput = document.getElementById('searchQuery');
        searchInput.addEventListener('keypress', (event) => {
            if (event.key === 'Enter') {
                this.performSearch();
            }
        });
    },
    methods: {
        selectFood(food) {
            this.searchText = food;
            this.performSearch();
        },
        async performSearch() {
            const query = document.getElementById('searchQuery').value;
            const resultsDiv = document.querySelector('.results-content');
            const searchContainer = document.getElementById('searchContainer');
            const searchWrapper = document.querySelector('.search-wrapper');
            
            resultsDiv.innerHTML = '';
            this.hasResults = true;

            // 添加类名以调整布局
            searchContainer.classList.add('sticky');
            searchWrapper.classList.add('has-results');

            // 确保结果容器在搜索框移动后正确定位
            setTimeout(() => {
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }, 100);

            if (!query) {
                const defaultPrompts = [
                    "生成示例结果1...",
                    "分析数据2...",
                    "处理信息3...",
                    "计算结果4...",
                    "总结内容5..."
                ];

                this.processStreams(defaultPrompts, resultsDiv);
            } else {
                try {
                    const requests = Array.from({ length: 5 }, async () => {
                        const p = document.createElement('p');
                        resultsDiv.appendChild(p);

                        try {
                            const response = await fetch(`http://localhost:7999/call_openai?query=${encodeURIComponent(query)}`);
                            if (!response.ok) {
                                throw new Error(`HTTP error! status: ${response.status}`);
                            }
                            const data = await response.text();
                            const cleanedData = data.replace(/^data:\s*/gm, '').trim();
                            await this.simulateStreamOutput(cleanedData, p);
                        } catch (error) {
                            console.error('Request failed:', error);
                            p.textContent = '请求失败，请稍后重试...';
                        }
                    });

                    await Promise.all(requests);
                } catch (error) {
                    console.error('Error:', error);
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
            element.appendChild(cursor);

            // 模拟流式输出
            for (let char of text) {
                currentText += char;
                element.textContent = currentText;
                element.appendChild(cursor); // Re-append cursor to keep it at the end
                await delay(50 + Math.random() * 50); // 随机延迟，使输出看起来更自然
            }
            
            // 移除光标
            element.removeChild(cursor);
            
            // 添加完成动画
            element.classList.add('complete');
        }
    }
}
</script>

<style scoped>
/* 整体容器样式 */
.search-wrapper {
    min-height: 100vh;
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: flex-start;
    padding: 20px;
    box-sizing: border-box;
    background: transparent;
    position: relative;
    z-index: 1;
}

.content-container {
    width: 100%;
    max-width: 800px;
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: 20vh;
    transition: margin-top 0.4s ease;
    background: transparent;
}

.content-container.has-results {
    margin-top: 40px;
}

/* 搜索框和结果容器的共同样式 */
.search-input-container,
.results-container {
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border-radius: 20px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.06);
    width: 90%;
    max-width: 800px;
    padding: 24px;
    color: #1d1d1f;
    border: 1px solid rgba(255, 255, 255, 0.2);
}

/* 搜索框样式 */
.search-input-container {
    text-align: center;
    margin-bottom: 20px;
}

.search-input-container.sticky {
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 100;
    padding: 16px;
    width: calc(100% - 40px);
    max-width: 800px;
}

/* 结果容器样式 */
.results-container {
    display: none;
    opacity: 0;
    transform: translateY(20px);
    margin-top: 20px;
    background: rgba(255, 255, 255, 0.8);
}

.results-container.show {
    display: block;
    opacity: 1;
    transform: translateY(0);
}

/* 移动端适配 */
@media (max-width: 768px) {
    .search-wrapper {
        padding: 12px;
    }

    .content-container {
        margin-top: 15vh;
    }

    .content-container.has-results {
        margin-top: 20px;
    }

    .search-input-container.sticky {
        padding: 12px;
        width: calc(100% - 24px);
    }

    .search-input-container.sticky .logo {
        width: 32px;
        height: 32px;
    }

    .search-input-container.sticky h1 {
        display: none;
    }

    .quick-food-tags {
        transform: scale(0.9);
    }
}

/* 特小屏幕优化 */
@media (max-width: 360px) {
    .search-wrapper {
        padding: 8px;
    }

    .content-container.has-results {
        margin-top: 12px;
    }

    .search-input-container.sticky {
        padding: 8px;
        width: calc(100% - 16px);
    }
}

/* 保留其他现有样式 ... */
html, body {
    height: 100%;
    margin: 0;
}

.search-wrapper.has-results {
    padding-top: 220px;
}

/* 搜索框和结果容器的共同样式 */
.search-input-container,
.results-container {
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border-radius: 20px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.06);
    width: 90%;
    max-width: 800px;
    padding: 24px;
    color: #1d1d1f;
    border: 1px solid rgba(255, 255, 255, 0.2);
}

/* 搜索框特定样式 */
.search-input-container {
    text-align: center;
    margin-bottom: 20px;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    position: absolute;
    left: 50%;
    transform: translate(-50%, -50%);
    top: 50%;
}

/* 搜索框固定状态 */
.search-input-container.sticky {
    position: fixed;
    top: 20px;
    transform: translateX(-50%);
    padding: 20px;
    z-index: 100;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.search-input-container.sticky h1 {
    display: none;
}

.search-input-container.sticky .input-group {
    margin-top: 0;
}

.search-input-container.sticky .logo {
    width: 40px;
    height: 40px;
    margin-bottom: 5px;
}

.input-group {
    display: flex;
    gap: 10px;
    margin-top: 20px;
    transition: all 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

.logo {
    width: 60px;
    height: 60px;
    margin-bottom: 10px;
}

input[type="text"] {
    flex: 1;
    padding: 16px 20px;
    border: none;
    border-radius: 12px;
    background-color: rgba(0, 0, 0, 0.03);
    color: #1d1d1f;
    font-size: 17px;
    transition: all 0.3s ease;
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text";
}

input[type="text"]:focus {
    background-color: rgba(0, 0, 0, 0.05);
    outline: none;
}

button {
    padding: 16px 28px;
    background-color: #0071e3;
    color: white;
    border: none;
    border-radius: 12px;
    font-size: 17px;
    font-weight: 500;
    transition: all 0.3s ease;
}

button:hover {
    background-color: #0077ED;
    transform: none;
    box-shadow: none;
}

/* 结果内容样式 */
.results-content p {
    margin: 0;
    padding: 16px;
    background: rgba(255, 255, 255, 0.5);
    backdrop-filter: blur(5px);
    -webkit-backdrop-filter: blur(5px);
    border-radius: 12px;
    border: none;
    transition: all 0.3s ease;
    margin-bottom: 12px;
    font-size: 15px;
    line-height: 1.5;
    color: #1d1d1f;
}

.results-content p:hover {
    background: rgba(0, 0, 0, 0.05);
    transform: translateX(8px);
}

.results-content p.complete {
    animation: completeFade 0.5s ease forwards;
}

@keyframes completeFade {
    from {
        background-color: rgba(0, 0, 0, 0.02);
    }
    to {
        background-color: rgba(0, 0, 0, 0.03);
    }
}

/* 容器悬停效果 */
.search-input-container:hover,
.results-container:hover {
    box-shadow: 0 12px 36px rgba(0, 0, 0, 0.08);
}

/* 深色模式 */
@media (prefers-color-scheme: dark) {
    .search-input-container,
    .results-container {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
    }

    .input-group input[type="text"] {
        background-color: rgba(0, 0, 0, 0.03);
        color: #1d1d1f;
    }

    .food-tag {
        background: rgba(0, 0, 0, 0.03);
        color: #1d1d1f;
    }

    .results-content p {
        background: rgba(255, 255, 255, 0.5);
    }
}

/* 优化搜索框阴影效果 */
.search-input-container {
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.06);
}

.search-input-container:hover {
    box-shadow: 0 12px 36px rgba(0, 0, 0, 0.08);
}

.search-input-container.sticky:hover {
    box-shadow: 0 6px 28px rgba(0, 0, 0, 0.12);
}

@keyframes starryBackground {
    from {
        background-position: 0 0;
    }
    to {
        background-position: 1000px 1000px;
    }
}

body::before {
    display: none;
}

/* 添加打字机效果相关样式 */
@keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0; }
}

.cursor {
    display: inline-block;
    animation: blink 1s step-end infinite;
}

/* 添加到现有的样式中 */
.quick-food-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 12px;
    justify-content: center;
}

.food-tag {
    background: rgba(0, 0, 0, 0.03);
    border: none;
    padding: 8px 16px;
    border-radius: 20px;
    cursor: pointer;
    transition: all 0.3s ease;
    font-size: 15px;
    color: #1d1d1f;
    display: flex;
    align-items: center;
    gap: 6px;
    font-weight: 500;
}

.food-tag:hover {
    background: rgba(0, 0, 0, 0.06);
}

.food-tag ion-icon {
    font-size: 16px;
    color: #0071e3;
}

/* 搜索框固定时的食物标签样式 */
.search-input-container.sticky .quick-food-tags {
    margin-top: 10px;
    transform: scale(0.9);
    transform-origin: top center;
    margin-bottom: 5px;
}
</style>
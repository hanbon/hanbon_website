<style>
/* 搜索按钮特殊样式 */
.search-btn {
    width: 36px;
    height: 36px;
    padding: 0;
    background: var(--primary-color);
    color: white;
}

.search-btn:hover {
    background: var(--primary-hover);
    transform: translateY(-1px);
}

/* 按钮基础样式 */
button {
    padding: 12px 24px;
    background: var(--primary-color);
    color: white;
    border: none;
    border-radius: 10px;
    font-size: 16px;
    cursor: pointer;
    transition: all 0.3s ease;
}

button:hover {
    background: var(--primary-hover);
    transform: translateY(-1px);
}

/* 食物标签 */
.food-tag {
    padding: 6px 12px;
    background: var(--primary-light);
    border-radius: 20px;
    color: var(--primary-color);
    font-size: 14px;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 4px;
}

.food-tag:hover {
    background: var(--secondary-light);
    color: var(--secondary-color);
    transform: translateY(-1px);
}

/* 历史标签 */
.history-tag {
    padding: 4px 12px;
    background: var(--primary-light);
    border-radius: 16px;
    color: var(--primary-color);
    font-size: 14px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.history-tag:hover {
    background: var(--secondary-light);
    color: var(--secondary-color);
    transform: translateY(-1px);
}

.history-tag:focus {
    outline: 2px solid var(--primary-color);
    outline-offset: 2px;
}

/* 切换按钮样式 */
.recipe-source-toggle button {
    padding: 8px 16px;
    background: transparent;
    border: 1px solid var(--primary-color);
    color: var(--primary-color);
}

.recipe-source-toggle button.active {
    background: var(--primary-color);
    color: white;
}

/* 定时器样式 */
.timer-toggle {
    background: var(--primary-color);
}

.timer-display {
    color: var(--primary-color);
}

/* 返回顶部按钮 */
.back-to-top {
    background: var(--primary-color);
}

.back-to-top:hover {
    background: var(--primary-hover);
}

.back-to-top:focus {
    box-shadow: 0 0 0 3px var(--primary-light);
}

/* 输入框焦点样式 */
input:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 2px var(--primary-light);
}

/* 标题和强调文本 */
.recipe-content h2 {
    border-bottom: 2px solid var(--primary-color);
}

.recipe-details strong,
.recipe-details b,
.markdown-body strong {
    color: var(--primary-color);
    border-bottom: 1px solid var(--primary-light);
}

/* 主料和调料部分 */
.recipe-details p[data-type="ingredients"],
.recipe-details p[data-type="seasonings"],
.markdown-body p:has(strong:contains("主料")),
.markdown-body p:has(strong:contains("调料")) {
    background: var(--primary-light);
}

/* 小贴士部分 */
.recipe-details p[data-type="tips"],
.markdown-body p:has(strong:contains("小贴士")) {
    background: var(--secondary-light);
}

/* 错误消息 */
.error-message {
    color: var(--error-color);
}

/* 卡路里信息 */
.calorie-info {
    color: var(--success-color);
    background: var(--success-color-light);
}
</style> 
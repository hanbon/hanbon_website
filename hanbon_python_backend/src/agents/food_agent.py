#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@file: food_agent.py
@description: 美食AI代理核心类
@author: AI Assistant
@created: 2024
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, AsyncGenerator, Any
import openai
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class ConversationContext(BaseModel):
    """对话上下文模型"""
    user_id: str
    session_id: str
    messages: List[Dict[str, str]] = []
    preferences: Dict[str, Any] = {}
    current_location: Optional[str] = None
    enabled_tools: List[str] = []

class FoodAgent:
    """
    美食AI代理类
    集成Plan(计划)、Memory(记忆)、Action(行动)三大功能
    """
    
    def __init__(self, config, memory_client, mcp_manager, model_manager=None):
        """
        初始化美食AI代理
        
        Args:
            config: 配置对象（包含AI模型配置）
            memory_client: 记忆客户端
            mcp_manager: MCP工具管理器
            model_manager: 模型管理器（可选，兼容旧版本）
        """
        self.config = config
        self.memory_client = memory_client
        self.mcp_manager = mcp_manager
        self.model_manager = model_manager
        
        if model_manager:
            # 使用新的模型管理器
            self.ai_clients = model_manager.ai_clients
        else:
            # 兼容性：使用旧的初始化方法
            self.ai_clients = {}
            self._init_ai_clients()
        
        # 兼容性：保持deepseek_client属性
        self.deepseek_client = self.ai_clients.get('deepseek')
        
        # 活跃的对话上下文
        self.active_contexts: Dict[str, ConversationContext] = {}
        
        # AI代理的人格设定
        self.personality = {
            "friendly_food_expert": self._get_friendly_personality(),
            "professional_food_expert": self._get_professional_personality()
        }
        
        self.current_personality = "friendly_food_expert"
    
    def _init_ai_clients(self):
        """初始化所有可用的AI客户端"""
        for model_id, model_config in self.config.AI_MODELS.items():
            if model_config.get('enabled', False) and model_config.get('api_key'):
                try:
                    self.ai_clients[model_id] = openai.AsyncOpenAI(
                        api_key=model_config['api_key'],
                        base_url=model_config['api_base']
                    )
                    logger.info(f"成功初始化 {model_config['name']} 客户端")
                except Exception as e:
                    logger.error(f"初始化 {model_config['name']} 客户端失败: {e}")
    
    def _get_ai_client(self, model_name: str = None):
        """获取指定模型的AI客户端"""
        if self.model_manager:
            # 使用新的模型管理器
            return self.model_manager.get_ai_client(model_name)
        else:
            # 兼容性：使用旧的方法
            if not model_name:
                model_name = self.config.DEFAULT_MODEL
            
            if model_name in self.ai_clients:
                return self.ai_clients[model_name], self.config.AI_MODELS[model_name]
            else:
                # 回退到默认模型
                default_model = self.config.DEFAULT_MODEL
                if default_model in self.ai_clients:
                    logger.warning(f"模型 {model_name} 不可用，使用默认模型 {default_model}")
                    return self.ai_clients[default_model], self.config.AI_MODELS[default_model]
                else:
                    raise ValueError(f"没有可用的AI模型客户端")
        
    def _get_friendly_personality(self) -> str:
        """获取友好型人格设定"""
        return """你是食慧美食AI助手，一个热情友好的美食专家。你的特点：

1. **专业知识**：精通中华料理、世界各地美食、营养搭配、烹饪技巧
2. **性格特点**：热情、耐心、幽默、善于倾听
3. **交流风格**：用温暖的语调，适当使用表情符号，让用户感到亲切
4. **服务理念**：以用户需求为中心，提供个性化的美食建议

你能够：
- 🍳 推荐适合的菜谱和做法
- 🗺️ 根据地理位置推荐当地美食
- 🌡️ 结合天气情况给出饮食建议
- 📷 识别食物图片并提供相关信息
- 💡 记住用户的口味偏好和饮食习惯
- 🎯 制定个性化的饮食计划

请始终保持友好、专业的态度，用你的专业知识帮助用户享受美食生活！"""

    def _get_professional_personality(self) -> str:
        """获取专业型人格设定"""
        return """您好，我是食慧美食AI专业顾问。作为专业的美食分析系统，我具备：

1. **专业能力**：深度美食知识库、营养学分析、烹饪工艺研究
2. **服务标准**：准确、高效、个性化、数据驱动
3. **技术优势**：多模态分析、智能推荐、实时信息获取
4. **专业领域**：菜谱分析、营养评估、食材搭配、烹饪指导

核心功能：
- 精准的食谱匹配与优化建议
- 基于地理位置的餐饮信息查询
- 营养成分分析与健康建议
- 食物图像识别与成分分析
- 个性化饮食方案制定
- 专业烹饪技巧指导

我将为您提供最专业、准确的美食咨询服务。"""

    async def get_context(self, user_id: str, session_id: str) -> ConversationContext:
        """获取或创建对话上下文"""
        context_key = f"{user_id}:{session_id}"
        
        if context_key not in self.active_contexts:
            # 从记忆中恢复上下文
            memories = await self.memory_client.get_user_memories(user_id)
            preferences = {}
            
            # 从记忆中提取用户偏好
            for memory in memories:
                if memory.get('type') == 'preference':
                    preferences.update(memory.get('content', {}))
            
            self.active_contexts[context_key] = ConversationContext(
                user_id=user_id,
                session_id=session_id,
                preferences=preferences
            )
        
        return self.active_contexts[context_key]

    async def process_message(
        self, 
        message: str, 
        user_id: str = "default", 
        session_id: str = "default",
        enabled_tools: List[str] = None,
        model: str = None
    ) -> Dict[str, Any]:
        """
        处理用户消息
        
        Args:
            message: 用户消息
            user_id: 用户ID
            session_id: 会话ID
            enabled_tools: 启用的工具列表
            
        Returns:
            处理结果
        """
        try:
            # 获取对话上下文
            context = await self.get_context(user_id, session_id)
            context.enabled_tools = enabled_tools or []
            
            # 添加用户消息到上下文
            context.messages.append({
                "role": "user",
                "content": message,
                "timestamp": datetime.now().isoformat()
            })
            
            # 计划阶段 - 分析用户意图和需要的工具
            plan = await self._plan_response(message, context, model)
            
            # 行动阶段 - 执行必要的工具调用
            action_results = await self._execute_actions(plan, context, model)
            
            # 生成回复
            response = await self._generate_response(message, context, plan, action_results, model)
            
            # 记忆阶段 - 更新用户记忆
            memory_updated = await self._update_memory(context, message, response)
            
            return {
                "response": response,
                "tools_used": plan.get("tools", []),
                "memory_updated": memory_updated,
                "session_id": session_id,
                "plan": plan
            }
            
        except Exception as e:
            logger.error(f"处理消息失败: {e}")
            return {
                "response": f"抱歉，处理您的请求时出现了错误：{str(e)}",
                "tools_used": [],
                "memory_updated": False,
                "session_id": session_id
            }

    async def stream_message(
        self,
        message: str,
        user_id: str = "default",
        session_id: str = "default",
        enabled_tools: List[str] = None,
        model: str = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        流式处理用户消息（带思维链）
        
        Args:
            message: 用户消息
            user_id: 用户ID  
            session_id: 会话ID
            enabled_tools: 启用的工具列表
            
        Yields:
            流式响应块
        """
        try:
            # 获取对话上下文
            context = await self.get_context(user_id, session_id)
            context.enabled_tools = enabled_tools or []
            
            # 添加用户消息到上下文
            context.messages.append({
                "role": "user",
                "content": message,
                "timestamp": datetime.now().isoformat()
            })
            
            # 发送开始信号
            yield {
                "type": "start",
                "content": "开始处理您的请求..."
            }
            
            # 思维链阶段 - 分析用户意图
            yield {
                "type": "thinking_step",
                "step": 1,
                "title": "理解用户需求",
                "content": "正在分析您的问题...",
                "status": "processing"
            }
            
            # 流式生成意图分析
            thinking_analysis_chunks = []
            async for chunk in self._stream_user_intent_analysis(message, context, model):
                thinking_analysis_chunks.append(chunk)
                yield {
                    "type": "thinking_step", 
                    "step": 1,
                    "title": "理解用户需求",
                    "content": "".join(thinking_analysis_chunks),
                    "status": "processing"
                }
            
            yield {
                "type": "thinking_step",
                "step": 1,
                "title": "理解用户需求",
                "content": "".join(thinking_analysis_chunks),
                "status": "completed"
            }
            
            # 思维链阶段 - 制定计划
            yield {
                "type": "thinking_step", 
                "step": 2,
                "title": "制定解决方案",
                "content": "根据需求分析，正在制定最佳的回答策略...",
                "status": "processing"
            }
            
            plan = await self._plan_response_with_thinking(message, context, model)
            
            # 流式生成计划思考过程
            plan_thinking_content = ""
            plan_parts = [
                f"我的计划：",
                f"• 用户意图：{plan.get('intent', '未知')}",
                f"• 需要使用的工具：{', '.join(plan.get('tools', [])) if plan.get('tools') else '无'}",
                f"• 回答类型：{plan.get('response_type', 'text')}",
                f"• 策略：{plan.get('strategy', '直接回答用户问题')}"
            ]
            
            for part in plan_parts:
                plan_thinking_content += part + "\n"
                yield {
                    "type": "thinking_step",
                    "step": 2,
                    "title": "制定解决方案", 
                    "content": plan_thinking_content.strip(),
                    "status": "processing"
                }
                # 模拟思考时间
                await asyncio.sleep(0.3)
            
            yield {
                "type": "thinking_step",
                "step": 2, 
                "title": "制定解决方案",
                "content": plan_thinking_content.strip(),
                "status": "completed"
            }
            
            # 思维链阶段 - 执行工具
            action_results = {}
            if plan.get("tools"):
                yield {
                    "type": "thinking_step",
                    "step": 3,
                    "title": "收集信息",
                    "content": f"正在使用 {', '.join(plan['tools'])} 工具收集相关信息...",
                    "status": "processing"
                }
                
                action_results = await self._execute_actions_with_thinking(plan, context, model)
                
                # 分析工具结果
                tools_summary = []
                for tool_name, result in action_results.items():
                    if 'error' not in result:
                        if tool_name == 'image_search':
                            count = len(result.get('display_data', {}).get('images', []))
                            tools_summary.append(f"图片搜索：找到 {count} 张相关图片")
                        elif tool_name == 'food_recommendation':
                            count = result.get('display_data', {}).get('total_count', 0)
                            tools_summary.append(f"美食推荐：生成 {count} 个推荐")
                        elif tool_name == 'recipe_generator':
                            dish_name = result.get('display_data', {}).get('recipe', {}).get('dish_name', '菜谱')
                            tools_summary.append(f"菜谱生成：制作 {dish_name} 的详细菜谱")
                        else:
                            tools_summary.append(f"{tool_name}：执行成功")
                    else:
                        tools_summary.append(f"{tool_name}：执行失败")
                
                tools_result_text = f"""
信息收集完成：
{chr(10).join(['• ' + summary for summary in tools_summary])}

现在我有了足够的信息来回答您的问题。
"""
                
                yield {
                    "type": "thinking_step",
                    "step": 3,
                    "title": "收集信息", 
                    "content": tools_result_text.strip(),
                    "status": "completed"
                }
                
                # 发送工具结果
                tool_results_list = []
                for tool_name, result in action_results.items():
                    tool_results_list.append(result)
                
                yield {
                    "type": "action_result",
                    "content": tool_results_list
                }
            
            # 思维链阶段 - 生成回复
            yield {
                "type": "thinking_step",
                "step": 4,
                "title": "组织回答",
                "content": "正在整理信息，为您生成最合适的回答...",
                "status": "processing"
            }
            
            # 流式生成回复并收集完整响应
            response_chunks = []
            try:
                async for chunk in self._stream_response_with_thinking(message, context, plan, action_results, model):
                    response_chunks.append(chunk)
                    yield {
                        "type": "response_chunk", 
                        "content": chunk
                    }
                
                # 确保思维链第四步完成
                yield {
                    "type": "thinking_step",
                    "step": 4,
                    "title": "组织回答",
                    "content": "回答生成完成！已为您整理好完整的信息，希望对您有帮助。",
                    "status": "completed"
                }
                
            except Exception as stream_error:
                logger.error(f"流式回复生成失败: {stream_error}")
                # 即使出错也要完成思维链
                yield {
                    "type": "thinking_step",
                    "step": 4,
                    "title": "组织回答",
                    "content": f"回答生成过程中遇到问题，但我已尽力为您整理信息。错误: {str(stream_error)}",
                    "status": "completed"
                }
                
                # 提供备用回答
                response_chunks.append("抱歉，在生成详细回答时遇到了一些问题，但工具执行结果仍然有效。")
            
            # 合并完整响应并更新记忆
            full_response = "".join(response_chunks)
            memory_updated = await self._update_memory(context, message, full_response)
            
            yield {
                "type": "complete",
                "content": {
                    "memory_updated": memory_updated,
                    "tools_used": plan.get("tools", [])
                }
            }
            
        except Exception as e:
            logger.error(f"流式处理失败: {e}")
            yield {
                "type": "error",
                "content": f"处理请求时出现错误：{str(e)}"
            }

    async def _plan_response(self, message: str, context: ConversationContext, model: str = None) -> Dict[str, Any]:
        """
        计划阶段 - 分析用户意图并制定响应计划
        
        Args:
            message: 用户消息
            context: 对话上下文
            
        Returns:
            响应计划
        """
        system_prompt = f"""你是美食AI助手的计划模块。请分析用户的消息，判断需要使用哪些工具来最好地回答用户的问题。

可用工具：
- amap_search: 高德地图搜索（查找餐厅、美食地点）【参数：keyword(必需)】
- bing_search: 必应搜索（获取最新信息）【参数：query(必需)】
- weather_api: 天气API（获取天气信息）【参数：city(必需)】
- food_recommendation: 美食推荐【参数：preferences(可选)】
- image_search: 图片搜索（当用户要求"图片"、"照片"、"看看"、"展示"、"搜索图片"时使用）【参数：query(必需)】
- recipe_generator: 菜谱生成（当用户要求"做法"、"菜谱"、"怎么做"时使用）【参数：dish_name(必需)】

**重要识别规则：**
1. 如果用户提到"图片"、"照片"、"看看"、"展示"、"搜索图片"等关键词，必须使用image_search工具，参数名为query
2. 如果用户要求菜谱或做法，使用recipe_generator工具，参数名为dish_name
3. 如果用户询问餐厅位置，使用amap_search工具，参数名为keyword
4. 如果用户要求美食推荐，使用food_recommendation工具，参数名为preferences

**图片搜索query生成规则：**
- 分析用户需求，主动生成最优的搜索关键词（不是简单提取）
- 根据食物类型智能增强关键词以提高搜索效果
- 例如："给我看看红烧肉的图片" → 分析：用户要红烧肉图片 → 生成query: "红烧肉 美食 成品"
- 例如："我想看看川菜的照片" → 分析：用户要川菜图片 → 生成query: "川菜 菜谱 特色菜"
- 例如："展示一些意大利面的图片" → 分析：用户要意大利面图片 → 生成query: "意大利面 pasta 美食"
- 思考：什么关键词组合能搜到最相关的图片？而不是简单去除修饰词

用户偏好：{context.preferences}
当前位置：{context.current_location}
可用工具：{context.enabled_tools}

请返回JSON格式的计划（必须严格按照JSON格式）：
{{
    "intent": "用户意图描述",
    "tools": ["需要使用的工具列表"],
    "parameters": {{"工具名": {{"参数": "值"}}}},
    "response_type": "text/recipe/recommendation/location"
}}

用户消息：{message}"""

        try:
            # 获取指定模型的客户端和配置
            ai_client, model_config = self._get_ai_client(model)
            
            response = await ai_client.chat.completions.create(
                model=model_config['model'],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            plan_text = response.choices[0].message.content
            
            # 尝试解析JSON
            try:
                plan = json.loads(plan_text)
            except json.JSONDecodeError:
                # 如果不是有效JSON，使用规则引擎创建计划
                plan = self._create_fallback_plan(message)
            
            # 过滤不可用的工具
            if context.enabled_tools:
                plan["tools"] = [tool for tool in plan.get("tools", []) if tool in context.enabled_tools]
            
            return plan
            
        except Exception as e:
            logger.error(f"制定计划失败: {e}")
            # 使用规则引擎作为回退
            return self._create_fallback_plan(message)
    
    def _create_fallback_plan(self, message: str) -> Dict[str, Any]:
        """
        基于规则的回退计划生成器
        当AI模型调用失败时使用
        """
        message_lower = message.lower()
        
        # 图片搜索关键词
        image_keywords = ['图片', '照片', '看看', '展示', '搜索图片', '显示', '图像', '看一下', '瞧瞧']
        # 菜谱关键词
        recipe_keywords = ['做法', '菜谱', '怎么做', '制作方法', '烹饪', '料理', '步骤']
        # 推荐关键词
        recommendation_keywords = ['推荐', '建议', '什么好吃', '吃什么']
        # 地图搜索关键词
        location_keywords = ['附近', '餐厅', '饭店', '哪里有', '地址', '位置']
        
        plan = {
            "intent": "回答用户关于美食的问题",
            "tools": [],
            "parameters": {},
            "response_type": "text"
        }
        
        # 检查图片搜索需求
        if any(keyword in message_lower for keyword in image_keywords):
            plan["intent"] = "搜索美食图片"
            plan["tools"].append("image_search")
            plan["response_type"] = "image"
            
            # 智能生成搜索关键词
            search_query = self._generate_smart_image_query(message)
            
            plan["parameters"]["image_search"] = {
                "query": search_query,
                "count": 5
            }
        
        # 检查菜谱需求
        elif any(keyword in message_lower for keyword in recipe_keywords):
            plan["intent"] = "生成菜谱并展示图片"
            plan["tools"].extend(["recipe_generator", "image_search"])  # 同时添加图片搜索
            plan["response_type"] = "recipe"
            
            # 从消息中提取食物名称
            food_name = self._extract_food_name_simple(message)
            dish_name = food_name if food_name else "家常菜"
            
            plan["parameters"]["recipe_generator"] = {
                "dish_name": dish_name
            }
            
            # 同时搜索相关图片以增强用户体验
            search_query = self._enhance_search_keywords(dish_name, message)
            plan["parameters"]["image_search"] = {
                "query": search_query
            }
        
        # 检查推荐需求
        elif any(keyword in message_lower for keyword in recommendation_keywords):
            plan["intent"] = "美食推荐"
            plan["tools"].append("food_recommendation")
            plan["response_type"] = "recommendation"
            
            plan["parameters"]["food_recommendation"] = {
                "preferences": {},
                "count": 5
            }
        
        # 检查位置搜索需求
        elif any(keyword in message_lower for keyword in location_keywords):
            plan["intent"] = "搜索餐厅位置"
            plan["tools"].append("amap_search")
            plan["response_type"] = "location"
            
            # 提取关键词
            keyword = "餐厅"
            for word in ['火锅', '川菜', '粤菜', '湘菜', '烧烤', '西餐']:
                if word in message:
                    keyword = word
                    break
            
            plan["parameters"]["amap_search"] = {
                "keyword": keyword
            }
        
        logger.info(f"使用回退计划: {plan}")
        return plan
    
    def _generate_smart_image_query(self, message: str) -> str:
        """
        根据用户消息智能生成图片搜索关键词
        
        Args:
            message: 用户原始消息
            
        Returns:
            优化的搜索关键词组合
        """
        import re
        
        # 首先提取基本的食物名称
        base_food = self._extract_food_name_simple(message)
        
        # 根据食物类型和消息内容智能增强关键词
        enhanced_query = self._enhance_search_keywords(base_food, message)
        
        return enhanced_query
    
    def _extract_food_name_simple(self, message: str) -> str:
        """
        从用户消息中简单提取食物名称
        
        Args:
            message: 用户原始消息
            
        Returns:
            提取的食物名称
        """
        import re
        
        # 定义要清理的停用词（按长度排序，先匹配长的）
        stop_words = [
            # 长短语优先
            '给我看看', '我想看看', '请搜索', '能给我', '麻烦给', '能否给我',
            # 动作词
            '给我', '帮我', '我想', '请', '能否', '可以', '麻烦', '能',
            # 展示词
            '看看', '展示', '显示', '搜索', '找', '查找', '瞧瞧', '看',
            # 图片词
            '图片', '照片', '图像', '图', '相片', '照',
            # 量词和修饰词
            '一些', '几张', '几个', '一点', '几种', '一张', '一下', '成品', '制作',
            # 助词
            '的', '了', '吗', '呢', '吧', '啊', '呀'
        ]
        
        # 开始清理消息
        cleaned = message.strip()
        
        # 移除标点符号
        cleaned = re.sub(r'[，。！？：；""''（）【】\[\](),.!?:;"\'\-]', '', cleaned)
        
        # 按顺序移除停用词
        for stop_word in stop_words:
            cleaned = cleaned.replace(stop_word, '')
        
        # 清理多余的空格
        cleaned = re.sub(r'\s+', '', cleaned).strip()
        
        # 如果结果为空或太短，尝试使用正则模式匹配
        if not cleaned or len(cleaned) < 2:
            # 尝试匹配常见的美食名称模式
            food_patterns = [
                r'([一-龯]*[肉][一-龯]*)',        # 包含"肉"的词
                r'([一-龯]*[鱼虾蟹蛋][一-龯]*)',   # 包含海鲜蛋类的词
                r'([一-龯]*[菜][一-龯]*)',        # 包含"菜"的词  
                r'([一-龯]*[汤粥面条饭][一-龯]*)', # 包含主食的词
                r'([一-龯]*[糖饼干蛋糕][一-龯]*)', # 包含甜品的词
                r'([一-龯]*[豆腐][一-龯]*)',      # 包含豆腐的词
            ]
            
            for pattern in food_patterns:
                matches = re.findall(pattern, message)
                if matches:
                    # 选择最长的匹配
                    longest_match = max(matches, key=len)
                    if len(longest_match) >= 2:
                        cleaned = longest_match
                        break
        
        # 如果还是没有结果，返回默认值
        if not cleaned or len(cleaned) < 2:
            return "美食"
        
        # 限制长度，防止过长
        if len(cleaned) > 8:
            cleaned = cleaned[:8]
        
        return cleaned
    
    def _enhance_search_keywords(self, base_food: str, original_message: str) -> str:
        """
        根据食物类型智能增强搜索关键词
        
        Args:
            base_food: 基础食物名称
            original_message: 原始用户消息
            
        Returns:
            增强后的搜索关键词组合
        """
        # 菜系和特色关键词映射
        cuisine_keywords = {
            # 中式菜系
            '红烧肉': '红烧肉 家常菜 美食',
            '宫保鸡丁': '宫保鸡丁 川菜 经典',
            '麻婆豆腐': '麻婆豆腐 川菜 豆腐',
            '糖醋里脊': '糖醋里脊 酸甜 家常菜',
            '回锅肉': '回锅肉 川菜 家常',
            '鱼香肉丝': '鱼香肉丝 川菜 下饭菜',
            
            # 菜系分类
            '川菜': '川菜 四川菜 麻辣',
            '粤菜': '粤菜 广东菜 清淡',
            '湘菜': '湘菜 湖南菜 辣椒',
            '鲁菜': '鲁菜 山东菜 传统',
            
            # 国际美食
            '意大利面': '意大利面 pasta 西餐',
            '牛排': '牛排 steak 西餐',
            '寿司': '寿司 日本料理 生鱼片',
            '拉面': '拉面 日式 汤面',
            '披萨': '披萨 pizza 西餐',
            
            # 甜品类
            '蛋糕': '蛋糕 甜品 烘焙',
            '奶茶': '奶茶 饮品 珍珠',
            '冰淇淋': '冰淇淋 甜品 夏季',
            
            # 主食类
            '包子': '包子 早餐 蒸',
            '饺子': '饺子 传统 面食',
            '面条': '面条 主食 汤面',
            '米饭': '米饭 主食 搭配'
        }
        
        # 检查是否有预定义的关键词组合
        if base_food in cuisine_keywords:
            return cuisine_keywords[base_food]
        
        # 根据食物特征动态生成关键词
        enhanced_query = base_food
        
        # 判断食物类型并添加相应关键词
        if any(word in base_food for word in ['肉', '鸡', '鸭', '鱼', '虾', '蟹']):
            enhanced_query += ' 美食 荤菜'
        elif any(word in base_food for word in ['菜', '豆腐', '萝卜', '土豆']):
            enhanced_query += ' 蔬菜 家常菜'
        elif any(word in base_food for word in ['面', '饭', '粥', '包子', '饺子']):
            enhanced_query += ' 主食 传统'
        elif any(word in base_food for word in ['汤', '羹']):
            enhanced_query += ' 汤品 营养'
        elif any(word in base_food for word in ['糕', '饼', '甜']):
            enhanced_query += ' 甜品 烘焙'
        else:
            enhanced_query += ' 美食 菜谱'
        
        # 如果用户提到特定需求，添加相应关键词
        if any(word in original_message for word in ['做法', '制作', '步骤']):
            enhanced_query += ' 制作过程'
        elif any(word in original_message for word in ['成品', '完成', '最终']):
            enhanced_query += ' 成品图'
        elif any(word in original_message for word in ['材料', '食材']):
            enhanced_query += ' 食材'
        
        return enhanced_query

    async def _stream_user_intent_analysis(self, message: str, context: ConversationContext, model: str = None) -> AsyncGenerator[str, None]:
        """
        流式分析用户意图（思维链第一步）
        
        Args:
            message: 用户消息
            context: 对话上下文
            model: 使用的模型
            
        Yields:
            意图分析内容块
        """
        system_prompt = f"""你是一个专业的美食AI助手，正在分析用户的问题。请详细分析用户的意图和需求。

用户的历史偏好：{context.preferences}
当前可用工具：{context.enabled_tools}

请按以下格式分析用户意图：
1. 用户的核心需求是什么？
2. 用户可能期望什么样的回答？  
3. 这个问题的难度如何？
4. 需要哪些信息来回答这个问题？

请用简洁明了的语言分析，让用户能看懂你的思考过程。

用户问题：{message}"""

        try:
            ai_client, model_config = self._get_ai_client(model)
            
            stream = await ai_client.chat.completions.create(
                model=model_config['model'],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=800,
                temperature=0.7,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"流式意图分析失败: {e}")
            yield f"我正在分析您的问题：「{message}」\n\n看起来您想了解美食相关的信息，让我为您查找相关资料。"

    async def _analyze_user_intent(self, message: str, context: ConversationContext, model: str = None) -> str:
        """
        分析用户意图（思维链第一步）
        
        Args:
            message: 用户消息
            context: 对话上下文
            model: 使用的模型
            
        Returns:
            意图分析结果
        """
        system_prompt = f"""你是一个专业的美食AI助手，正在分析用户的问题。请详细分析用户的意图和需求。

用户的历史偏好：{context.preferences}
当前可用工具：{context.enabled_tools}

请按以下格式分析用户意图：
1. 用户的核心需求是什么？
2. 用户可能期望什么样的回答？  
3. 这个问题的难度如何？
4. 需要哪些信息来回答这个问题？

请用简洁明了的语言分析，让用户能看懂你的思考过程。

用户问题：{message}"""

        try:
            ai_client, model_config = self._get_ai_client(model)
            
            response = await ai_client.chat.completions.create(
                model=model_config['model'],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"意图分析失败: {e}")
            return f"我正在分析您的问题：「{message}」\n\n看起来您想了解美食相关的信息，让我为您查找相关资料。"

    async def _plan_response_with_thinking(self, message: str, context: ConversationContext, model: str = None) -> Dict[str, Any]:
        """
        带思维链的计划制定
        
        Args:
            message: 用户消息
            context: 对话上下文
            model: 使用的模型
            
        Returns:
            详细的响应计划
        """
        system_prompt = f"""你是美食AI助手的计划模块。请分析用户的消息，制定详细的回答策略。

可用工具：
- amap_search: 高德地图搜索（查找餐厅、美食地点）【参数：keyword(必需)】
- bing_search: 必应搜索（获取最新信息）【参数：query(必需)】
- weather_api: 天气API（获取天气信息）【参数：city(必需)】
- food_recommendation: 美食推荐【参数：preferences(可选)】
- image_search: 图片搜索（当用户要求"图片"、"照片"、"看看"、"展示"、"搜索图片"时使用）【参数：query(必需)】
- recipe_generator: 菜谱生成（当用户要求"做法"、"菜谱"、"怎么做"时使用）【参数：dish_name(必需)】

**图片搜索关键词生成策略：**
- 分析用户真正想看的内容
- 根据食物类型智能增强关键词
- 例如："红烧肉的图片" → 分析：用户要看红烧肉成品 → 生成query: "红烧肉 美食 成品"

用户偏好：{context.preferences}
当前位置：{context.current_location}
可用工具：{context.enabled_tools}

请返回JSON格式的详细计划：
{{
    "intent": "用户意图描述", 
    "tools": ["需要使用的工具列表"],
    "parameters": {{"工具名": {{"参数": "值"}}}},
    "response_type": "text/recipe/recommendation/location/image",
    "strategy": "回答策略描述",
    "reasoning": "选择这个策略的原因"
}}

用户消息：{message}"""

        try:
            ai_client, model_config = self._get_ai_client(model)
            
            response = await ai_client.chat.completions.create(
                model=model_config['model'],
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            plan_text = response.choices[0].message.content
            
            try:
                plan = json.loads(plan_text)
            except json.JSONDecodeError:
                plan = self._create_fallback_plan(message)
                plan["strategy"] = "使用备用策略回答用户问题"
                plan["reasoning"] = "AI模型返回格式错误，使用规则引擎"
            
            # 过滤不可用的工具
            if context.enabled_tools:
                plan["tools"] = [tool for tool in plan.get("tools", []) if tool in context.enabled_tools]
            
            return plan
            
        except Exception as e:
            logger.error(f"制定思维链计划失败: {e}")
            plan = self._create_fallback_plan(message)
            plan["strategy"] = "使用备用策略回答用户问题"
            plan["reasoning"] = f"AI调用失败：{str(e)}"
            return plan

    async def _execute_single_tool(self, tool_name: str, plan: Dict, context: ConversationContext) -> Dict:
        """
        执行单个工具
        
        Args:
            tool_name: 工具名称
            plan: 执行计划
            context: 对话上下文
            
        Returns:
            工具执行结果
        """
        try:
            parameters = plan.get("parameters", {}).get(tool_name, {})
            result = await self.mcp_manager.execute_tool(tool_name, parameters)
            return result
        except Exception as e:
            logger.error(f"工具 {tool_name} 执行失败: {e}")
            return {"success": False, "error": str(e)}

    async def _execute_actions_with_thinking(self, plan: Dict[str, Any], context: ConversationContext, model: str = None) -> Dict[str, Any]:
        """
        带思维链的工具执行
        """
        return await self._execute_actions(plan, context, model)

    async def _stream_response_with_thinking(
        self, 
        message: str, 
        context: ConversationContext, 
        plan: Dict[str, Any], 
        action_results: Dict[str, Any],
        model: str = None
    ) -> AsyncGenerator[str, None]:
        """
        带思维链的流式回复生成
        """
        # 可以在这里添加更多思维过程，现在先使用原有的生成方法
        async for chunk in self._stream_response(message, context, plan, action_results, model):
            yield chunk

    async def _execute_actions(self, plan: Dict[str, Any], context: ConversationContext, model: str = None) -> Dict[str, Any]:
        """
        行动阶段 - 执行计划中的工具调用
        
        Args:
            plan: 响应计划
            context: 对话上下文
            model: 用户选择的模型
            
        Returns:
            工具执行结果
        """
        action_results = {}
        
        for tool_name in plan.get("tools", []):
            try:
                parameters = plan.get("parameters", {}).get(tool_name, {})
                
                # 如果是菜谱生成工具，添加模型信息
                if tool_name == "recipe_generator" and model:
                    parameters["model_id"] = model
                
                result = await self.mcp_manager.execute_tool(tool_name, parameters)
                
                # 为结果添加展示类型信息
                enhanced_result = self._enhance_tool_result(tool_name, result)
                action_results[tool_name] = enhanced_result
                
                logger.info(f"工具 {tool_name} 执行成功")
                
            except Exception as e:
                logger.error(f"工具 {tool_name} 执行失败: {e}")
                action_results[tool_name] = {
                    "error": str(e),
                    "display_type": "error",
                    "tool_name": tool_name
                }
        
        return action_results

    def _enhance_tool_result(self, tool_name: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        为工具结果添加展示类型信息，优化前端展示
        
        Args:
            tool_name: 工具名称
            result: 原始工具结果
            
        Returns:
            增强后的结果，包含展示信息
        """
        enhanced_result = result.copy()
        enhanced_result["tool_name"] = tool_name
        
        # 根据工具类型添加展示信息
        if tool_name == "image_search":
            enhanced_result["display_type"] = "image_gallery"
            enhanced_result["display_config"] = {
                "layout": "grid",
                "columns": 3,
                "show_modal": True,
                "lazy_load": True
            }
            # 确保图片数据格式正确
            # 检查工具结果的嵌套结构
            tool_result = result.get("result", result)  # MCP包装后的结果
            if "images" in tool_result and isinstance(tool_result["images"], list):
                enhanced_result["display_data"] = {
                    "images": tool_result["images"],
                    "total": len(tool_result["images"]),
                    "query": tool_result.get("query", "")
                }
            else:
                # 如果没有图片数据，提供默认结构
                enhanced_result["display_data"] = {
                    "images": [],
                    "total": 0,
                    "query": tool_result.get("query", ""),
                    "message": tool_result.get("message", "未找到图片")
                }
        
        elif tool_name == "food_recommendation":
            enhanced_result["display_type"] = "recommendation_cards"
            enhanced_result["display_config"] = {
                "layout": "card_grid", 
                "show_ratings": True,
                "show_difficulty": True,
                "interactive": True
            }
            # 格式化推荐数据
            tool_result = result.get("result", result)
            if "recommendations" in tool_result:
                enhanced_result["display_data"] = {
                    "recommendations": tool_result["recommendations"],
                    "total_count": tool_result.get("total_count", 0),
                    "categories": self._extract_recommendation_categories(tool_result["recommendations"])
                }
            else:
                enhanced_result["display_data"] = {
                    "recommendations": [],
                    "total_count": 0,
                    "categories": []
                }
        
        elif tool_name == "recipe_generator":
            enhanced_result["display_type"] = "recipe_detailed"
            enhanced_result["display_config"] = {
                "layout": "detailed_card",
                "show_nutrition": True,
                "show_steps": True,
                "interactive": True,
                "printable": True
            }
            # 格式化菜谱数据
            tool_result = result.get("result", result)
            if "data" in tool_result:
                recipe_data = tool_result["data"]
                enhanced_result["display_data"] = {
                    "recipe": recipe_data,
                    "metadata": {
                        "prep_time": recipe_data.get("prep_time", ""),
                        "cook_time": recipe_data.get("cook_time", ""),
                        "difficulty": recipe_data.get("difficulty", ""),
                        "serving_size": recipe_data.get("serving_size", "")
                    }
                }
            else:
                enhanced_result["display_data"] = {
                    "recipe": {},
                    "metadata": {
                        "prep_time": "",
                        "cook_time": "",
                        "difficulty": "",
                        "serving_size": ""
                    }
                }
        
        elif tool_name == "amap_search":
            # 检查工具是否已经返回了正确的显示格式
            tool_result = result.get("result", result)
            
            # 如果工具已经提供了display_type，使用工具的格式
            if "display_type" in tool_result:
                enhanced_result.update(tool_result)
            else:
                # 回退到默认格式化
                enhanced_result["display_type"] = "location_list"
                enhanced_result["display_config"] = {
                    "layout": "list_with_map",
                    "show_distance": True,
                    "show_rating": True,
                    "interactive": True
                }
                # 格式化位置数据
                locations = tool_result.get("locations", [])
                if not locations:
                    # 兼容旧格式
                    locations = tool_result.get("results", [])
                
                enhanced_result["display_data"] = {
                    "locations": locations,
                    "search_query": tool_result.get("query", ""),
                    "total_found": len(locations)
                }
        
        elif tool_name == "weather_api":
            enhanced_result["display_type"] = "weather_card"
            enhanced_result["display_config"] = {
                "layout": "card_with_suggestions",
                "show_temperature": True,
                "show_suggestions": True,
                "animated": True
            }
            # 格式化天气数据
            tool_result = result.get("result", result)
            enhanced_result["display_data"] = {
                "weather": tool_result.get("weather", {}),
                "food_suggestions": tool_result.get("food_suggestions", []),
                "location": tool_result.get("location", "")
            }
        
        elif tool_name == "bing_search":
            enhanced_result["display_type"] = "search_results"
            enhanced_result["display_config"] = {
                "layout": "compact_list",
                "show_snippets": True,
                "max_results": 5
            }
            # 格式化搜索结果
            tool_result = result.get("result", result)
            enhanced_result["display_data"] = {
                "results": tool_result.get("results", []),
                "query": tool_result.get("query", ""),
                "total_results": tool_result.get("total_results", 0)
            }
        
        else:
            # 默认展示类型
            enhanced_result["display_type"] = "simple_text"
            enhanced_result["display_config"] = {
                "layout": "plain",
                "format": "json"
            }
            enhanced_result["display_data"] = result
        
        return enhanced_result
    
    def _extract_recommendation_categories(self, recommendations: List[Dict[str, Any]]) -> List[str]:
        """从推荐结果中提取分类"""
        categories = set()
        for rec in recommendations:
            if "category" in rec:
                categories.add(rec["category"])
        return list(categories)

    async def _generate_response(
        self, 
        message: str, 
        context: ConversationContext, 
        plan: Dict[str, Any], 
        action_results: Dict[str, Any],
        model: str = None
    ) -> str:
        """
        生成最终回复
        
        Args:
            message: 用户消息
            context: 对话上下文
            plan: 响应计划
            action_results: 工具执行结果
            
        Returns:
            AI回复
        """
        personality_prompt = self.personality[self.current_personality]
        
        system_prompt = f"""{personality_prompt}

当前对话上下文：
- 用户偏好：{context.preferences}
- 当前位置：{context.current_location}
- 执行的工具：{plan.get('tools', [])}
- 工具结果：{action_results}

请基于以上信息，生成一个有用、准确、友好的回复。如果使用了工具，请整合工具结果来增强你的回答。"""

        try:
            # 构建消息历史
            messages = [{"role": "system", "content": system_prompt}]
            
            # 添加最近的对话历史（限制长度）
            recent_messages = context.messages[-10:]  # 只保留最近10条消息
            for msg in recent_messages:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # 获取指定模型的客户端和配置
            ai_client, model_config = self._get_ai_client(model)
            
            response = await ai_client.chat.completions.create(
                model=model_config['model'],
                messages=messages,
                max_tokens=model_config.get('max_tokens', 2000),
                temperature=model_config.get('temperature', 0.7)
            )
            
            ai_response = response.choices[0].message.content
            
            # 添加AI回复到上下文
            context.messages.append({
                "role": "assistant",
                "content": ai_response,
                "timestamp": datetime.now().isoformat()
            })
            
            return ai_response
            
        except Exception as e:
            logger.error(f"生成回复失败: {e}")
            return "抱歉，我暂时无法处理您的请求，请稍后再试。"

    async def _stream_response(
        self, 
        message: str, 
        context: ConversationContext, 
        plan: Dict[str, Any], 
        action_results: Dict[str, Any],
        model: str = None
    ) -> AsyncGenerator[str, None]:
        """流式生成回复"""
        personality_prompt = self.personality[self.current_personality]
        
        system_prompt = f"""{personality_prompt}

当前对话上下文：
- 用户偏好：{context.preferences}
- 当前位置：{context.current_location}
- 执行的工具：{plan.get('tools', [])}
- 工具结果：{action_results}

请基于以上信息，生成一个有用、准确、友好的回复。"""

        try:
            messages = [{"role": "system", "content": system_prompt}]
            
            # 添加最近的对话历史
            recent_messages = context.messages[-10:]
            for msg in recent_messages:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # 获取指定模型的客户端和配置
            ai_client, model_config = self._get_ai_client(model)
            
            stream = await ai_client.chat.completions.create(
                model=model_config['model'],
                messages=messages,
                max_tokens=model_config.get('max_tokens', 2000),
                temperature=model_config.get('temperature', 0.7),
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"流式生成失败: {e}")
            yield f"抱歉，生成回复时出现错误：{str(e)}"

    async def _update_memory(self, context: ConversationContext, user_message: str, ai_response: str) -> bool:
        """
        更新用户记忆
        
        Args:
            context: 对话上下文
            user_message: 用户消息
            ai_response: AI回复
            
        Returns:
            是否成功更新记忆
        """
        try:
            # 分析对话内容，提取可记忆的信息
            memory_data = {
                "type": "conversation",
                "timestamp": datetime.now().isoformat(),
                "user_message": user_message,
                "ai_response": ai_response,
                "session_id": context.session_id
            }
            
            # 提取用户偏好
            preferences = await self._extract_preferences(user_message, ai_response)
            if preferences:
                memory_data["preferences"] = preferences
                context.preferences.update(preferences)
            
            # 保存到记忆系统
            await self.memory_client.add_memory(
                user_id=context.user_id,
                memory_data=memory_data
            )
            
            return True
            
        except Exception as e:
            logger.error(f"更新记忆失败: {e}")
            return False

    async def _extract_preferences(self, user_message: str, ai_response: str) -> Dict[str, Any]:
        """从对话中提取用户偏好"""
        # 这里可以使用NLP技术或规则来提取偏好
        # 简化实现，后续可以完善
        preferences = {}
        
        # 检测口味偏好
        if any(word in user_message.lower() for word in ['辣', '麻辣', '川菜']):
            preferences['spicy_preference'] = 'high'
        elif any(word in user_message.lower() for word in ['清淡', '不辣']):
            preferences['spicy_preference'] = 'low'
        
        # 检测饮食习惯
        if any(word in user_message.lower() for word in ['素食', 'vegetarian']):
            preferences['diet_type'] = 'vegetarian'
        elif any(word in user_message.lower() for word in ['减肥', '低热量']):
            preferences['health_goal'] = 'weight_loss'
        
        return preferences

    async def search_food(self, food_name: str, location: str = None, preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        搜索美食信息
        
        Args:
            food_name: 食物名称
            location: 位置信息
            preferences: 用户偏好
            
        Returns:
            搜索结果
        """
        try:
            results = {}
            
            # 使用多个工具搜索
            if location and 'amap_search' in self.mcp_manager.available_tools:
                # 搜索附近餐厅
                restaurant_results = await self.mcp_manager.execute_tool(
                    'amap_search',
                    {'keyword': food_name, 'location': location}
                )
                results['restaurants'] = restaurant_results
            
            if 'recipe_generator' in self.mcp_manager.available_tools:
                # 生成菜谱
                recipe_results = await self.mcp_manager.execute_tool(
                    'recipe_generator',
                    {'food_name': food_name, 'preferences': preferences}
                )
                results['recipe'] = recipe_results
            
            if 'image_search' in self.mcp_manager.available_tools:
                # 搜索图片
                image_results = await self.mcp_manager.execute_tool(
                    'image_search',
                    {'query': food_name}
                )
                results['images'] = image_results
            
            return {
                'success': True,
                'food_name': food_name,
                'results': results
            }
            
        except Exception as e:
            logger.error(f"搜索美食失败: {e}")
            return {
                'success': False,
                'error': str(e)
            } 
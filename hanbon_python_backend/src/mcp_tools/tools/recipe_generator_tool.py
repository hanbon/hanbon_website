#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@file: recipe_generator_tool.py
@description: AI菜谱生成工具 - 使用用户选择的默认模型
@author: AI Assistant
@created: 2024
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from ..base_tool import BaseMCPTool

logger = logging.getLogger(__name__)

class RecipeGeneratorTool(BaseMCPTool):
    """AI菜谱生成工具类"""
    
    def __init__(self, name: str, description: str, model_manager=None, **config):
        """
        初始化菜谱生成工具
        
        Args:
            name: 工具名称
            description: 工具描述
            model_manager: 模型管理器实例
        """
        super().__init__(name, description, **config)
        self.category = "food"
        self.model_manager = model_manager
        
        # 菜系分类
        self.cuisine_types = {
            "川菜": "四川菜，以麻辣著称",
            "湘菜": "湖南菜，以辣鲜香著名",
            "粤菜": "广东菜，清淡鲜美",
            "鲁菜": "山东菜，咸鲜为主",
            "苏菜": "江苏菜，清淡微甜",
            "浙菜": "浙江菜，清鲜脆嫩",
            "闽菜": "福建菜，鲜香清淡",
            "徽菜": "安徽菜，重油重色",
            "家常菜": "简单易做的日常菜品",
            "西餐": "西式料理",
            "日式": "日本料理",
            "韩式": "韩国料理"
        }
        
        # 难度等级
        self.difficulty_levels = {
            "简单": "适合初学者，步骤简单",
            "中等": "需要一定烹饪经验",
            "困难": "需要专业技巧和经验"
        }
        
        # 营养成分模板
        self.nutrition_template = {
            "calories": "卡路里",
            "protein": "蛋白质",
            "carbs": "碳水化合物", 
            "fat": "脂肪",
            "fiber": "膳食纤维",
            "sodium": "钠"
        }
    
    async def generate_recipe(
        self, 
        dish_name: str,
        cuisine_type: str = "家常菜",
        difficulty: str = "简单",
        serving_size: int = 2,
        dietary_restrictions: List[str] = None,
        available_ingredients: List[str] = None,
        model_id: str = None
    ) -> Dict[str, Any]:
        """
        生成详细菜谱
        
        Args:
            dish_name: 菜名
            cuisine_type: 菜系类型
            difficulty: 难度等级
            serving_size: 份数
            dietary_restrictions: 饮食限制
            available_ingredients: 可用食材
            model_id: 指定使用的模型ID，如果为None则使用默认模型
            
        Returns:
            详细菜谱信息
        """
        try:
            if not self.model_manager:
                logger.warning("模型管理器未初始化，使用默认菜谱")
                return self._get_default_recipe(dish_name)
            
            # 获取AI客户端和模型配置
            try:
                ai_client, model_config = self.model_manager.get_ai_client(model_id)
                logger.info(f"使用模型: {model_config.get('name', model_id or '默认模型')} 生成菜谱")
            except Exception as e:
                logger.error(f"获取AI模型客户端失败: {e}")
                return self._get_default_recipe(dish_name)
            
            # 构建提示词
            prompt = self._build_recipe_prompt(
                dish_name, cuisine_type, difficulty, 
                serving_size, dietary_restrictions, available_ingredients
            )
            
            # 调用AI API生成菜谱
            response = await ai_client.chat.completions.create(
                model=model_config.get('model', 'gpt-3.5-turbo'),
                messages=[
                    {"role": "system", "content": "你是一位专业的烹饪大师和营养专家，擅长创作详细的菜谱。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=model_config.get('max_tokens', 2500),
                temperature=model_config.get('temperature', 0.7)
            )
            
            recipe_text = response.choices[0].message.content
            
            # 解析生成的菜谱
            parsed_recipe = self._parse_recipe_response(recipe_text, dish_name)
            
            # 添加营养信息估算
            nutrition_info = await self._estimate_nutrition(parsed_recipe["ingredients"])
            parsed_recipe["nutrition"] = nutrition_info
            
            # 添加使用的模型信息
            parsed_recipe["generated_by"] = model_config.get('name', model_id or '默认模型')
            parsed_recipe["model_id"] = model_id or self.model_manager.config.DEFAULT_MODEL
            
            return parsed_recipe
            
        except Exception as e:
            logger.error(f"生成菜谱失败: {e}")
            return self._get_default_recipe(dish_name)
    
    def _build_recipe_prompt(
        self,
        dish_name: str,
        cuisine_type: str,
        difficulty: str,
        serving_size: int,
        dietary_restrictions: List[str],
        available_ingredients: List[str]
    ) -> str:
        """构建菜谱生成的提示词"""
        
        prompt = f"""请为"{dish_name}"生成一份详细的菜谱。要求如下：

基本信息：
- 菜系：{cuisine_type}
- 难度：{difficulty}
- 份数：{serving_size}人份
"""
        
        if dietary_restrictions:
            prompt += f"- 饮食限制：{', '.join(dietary_restrictions)}\n"
        
        if available_ingredients:
            prompt += f"- 优先使用食材：{', '.join(available_ingredients)}\n"
        
        prompt += """
请按以下JSON格式生成菜谱：

{
    "dish_name": "菜名",
    "description": "菜品简介",
    "prep_time": "准备时间（分钟）",
    "cook_time": "烹饪时间（分钟）",
    "total_time": "总时间（分钟）",
    "difficulty": "难度等级",
    "serving_size": "份数",
    "ingredients": [
        {
            "name": "食材名称",
            "amount": "用量",
            "unit": "单位",
            "notes": "备注（可选）"
        }
    ],
    "equipment": ["所需厨具"],
    "steps": [
        {
            "step_number": 1,
            "instruction": "详细步骤说明",
            "time": "此步骤耗时",
            "tips": "小贴士（可选）"
        }
    ],
    "tips_and_variations": [
        "制作技巧和变化建议"
    ],
    "storage_tips": "保存方法",
    "nutrition_highlights": "营养特点"
}

请确保菜谱详细、实用，步骤清晰易懂。"""
        
        return prompt
    
    def _parse_recipe_response(self, recipe_text: str, dish_name: str) -> Dict[str, Any]:
        """
        解析AI生成的菜谱响应
        
        Args:
            recipe_text: AI生成的菜谱文本
            dish_name: 菜名
            
        Returns:
            解析后的菜谱字典
        """
        try:
            # 尝试解析JSON
            if "{" in recipe_text and "}" in recipe_text:
                start = recipe_text.find("{")
                end = recipe_text.rfind("}") + 1
                json_text = recipe_text[start:end]
                recipe_data = json.loads(json_text)
                
                # 添加额外信息
                recipe_data["generated_time"] = datetime.now().isoformat()
                recipe_data["source"] = "AI生成"
                
                return recipe_data
            else:
                # 如果不是JSON格式，手动解析
                return self._manual_parse_recipe(recipe_text, dish_name)
                
        except json.JSONDecodeError:
            logger.warning("菜谱JSON解析失败，尝试手动解析")
            return self._manual_parse_recipe(recipe_text, dish_name)
        except Exception as e:
            logger.error(f"解析菜谱失败: {e}")
            return self._get_default_recipe(dish_name)
    
    def _manual_parse_recipe(self, recipe_text: str, dish_name: str) -> Dict[str, Any]:
        """手动解析菜谱文本"""
        lines = recipe_text.split('\n')
        
        return {
            "dish_name": dish_name,
            "description": f"{dish_name}的详细制作方法",
            "prep_time": "15",
            "cook_time": "30", 
            "total_time": "45",
            "difficulty": "中等",
            "serving_size": "2-3",
            "ingredients": [
                {"name": "主料", "amount": "适量", "unit": "", "notes": "根据配方调整"}
            ],
            "equipment": ["炒锅", "锅铲", "菜板", "刀具"],
            "steps": [
                {
                    "step_number": 1,
                    "instruction": recipe_text[:200] + "..." if len(recipe_text) > 200 else recipe_text,
                    "time": "按步骤进行",
                    "tips": "请参考详细说明"
                }
            ],
            "tips_and_variations": ["根据个人口味调整调料"],
            "storage_tips": "密封保存，及时食用",
            "nutrition_highlights": "营养丰富，搭配均衡",
            "generated_time": datetime.now().isoformat(),
            "source": "AI生成"
        }
    
    async def _estimate_nutrition(self, ingredients: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        估算营养成分
        
        Args:
            ingredients: 食材列表
            
        Returns:
            营养成分估算
        """
        try:
            # 简单的营养估算（实际项目中可接入专业营养数据库）
            total_calories = 0
            protein = 0
            carbs = 0
            fat = 0
            
            for ingredient in ingredients:
                name = ingredient.get("name", "").lower()
                
                # 基础营养估算
                if any(meat in name for meat in ["肉", "鸡", "鱼", "虾", "蛋"]):
                    total_calories += 150
                    protein += 20
                    fat += 8
                elif any(veg in name for veg in ["菜", "瓜", "豆", "笋"]):
                    total_calories += 25
                    protein += 2
                    carbs += 5
                elif any(grain in name for grain in ["米", "面", "粉", "饼"]):
                    total_calories += 100
                    carbs += 20
                    protein += 3
                else:
                    total_calories += 50
                    carbs += 8
            
            return {
                "per_serving": {
                    "calories": f"{total_calories}大卡",
                    "protein": f"{protein}g",
                    "carbohydrates": f"{carbs}g", 
                    "fat": f"{fat}g",
                    "fiber": "适量",
                    "sodium": "根据调料而定"
                },
                "health_benefits": [
                    "提供优质蛋白质",
                    "富含维生素和矿物质",
                    "营养搭配均衡"
                ],
                "notes": "营养数据为估算值，具体数值可能因食材品质和制作方法而异"
            }
            
        except Exception as e:
            logger.error(f"营养估算失败: {e}")
            return {
                "per_serving": {
                    "calories": "约300大卡",
                    "protein": "适量",
                    "carbohydrates": "适量",
                    "fat": "适量"
                },
                "notes": "营养数据暂不可用"
            }
    
    def _get_default_recipe(self, dish_name: str) -> Dict[str, Any]:
        """获取默认菜谱（当生成失败时使用）"""
        return {
            "dish_name": dish_name,
            "description": f"经典{dish_name}制作方法",
            "prep_time": "15",
            "cook_time": "30",
            "total_time": "45",
            "difficulty": "中等",
            "serving_size": "2-3",
            "ingredients": [
                {"name": "主要食材", "amount": "适量", "unit": "", "notes": "根据实际情况调整"}
            ],
            "equipment": ["基本厨具"],
            "steps": [
                {
                    "step_number": 1,
                    "instruction": "抱歉，菜谱生成暂时不可用，请稍后再试或寻找其他资源。",
                    "time": "",
                    "tips": ""
                }
            ],
            "tips_and_variations": ["可根据个人喜好调整"],
            "storage_tips": "常温保存，及时食用",
            "nutrition_highlights": "营养丰富",
            "nutrition": {
                "per_serving": {"calories": "适量"},
                "notes": "数据暂不可用"
            },
            "generated_time": datetime.now().isoformat(),
            "source": "默认模板",
            "status": "fallback"
        }
    
    async def execute(self, **parameters) -> Dict[str, Any]:
        """
        执行菜谱生成工具
        
        Args:
            parameters: 工具参数
            
        Returns:
            执行结果
        """
        try:
            dish_name = parameters.get("dish_name", "家常菜")
            cuisine_type = parameters.get("cuisine_type", "家常菜")
            difficulty = parameters.get("difficulty", "简单")
            serving_size = parameters.get("serving_size", 2)
            dietary_restrictions = parameters.get("dietary_restrictions", [])
            available_ingredients = parameters.get("available_ingredients", [])
            model_id = parameters.get("model_id")
            
            recipe = await self.generate_recipe(
                dish_name=dish_name,
                cuisine_type=cuisine_type,
                difficulty=difficulty,
                serving_size=serving_size,
                dietary_restrictions=dietary_restrictions,
                available_ingredients=available_ingredients,
                model_id=model_id
            )
            
            return {
                "success": True,
                "tool_name": self.name,
                "data": recipe,
                "message": f"成功生成{dish_name}的详细菜谱"
            }
            
        except Exception as e:
            logger.error(f"菜谱生成工具执行失败: {e}")
            return {
                "success": False,
                "tool_name": self.name,
                "error": str(e),
                "message": "菜谱生成失败"
            }
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        """获取参数模式"""
        return {
            "type": "object",
            "properties": {
                "dish_name": {
                    "type": "string",
                    "description": "要生成菜谱的菜名"
                },
                "cuisine_type": {
                    "type": "string",
                    "description": "菜系类型",
                    "enum": list(self.cuisine_types.keys()),
                    "default": "家常菜"
                },
                "difficulty": {
                    "type": "string",
                    "description": "难度等级",
                    "enum": list(self.difficulty_levels.keys()),
                    "default": "简单"
                },
                "serving_size": {
                    "type": "integer",
                    "description": "份数",
                    "minimum": 1,
                    "maximum": 10,
                    "default": 2
                },
                "dietary_restrictions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "饮食限制（如素食、无糖等）"
                },
                "available_ingredients": {
                    "type": "array", 
                    "items": {"type": "string"},
                    "description": "可用的食材列表"
                },
                "model_id": {
                    "type": "string",
                    "description": "指定使用的模型ID，如果为None则使用默认模型"
                }
            },
            "required": ["dish_name"]
        } 
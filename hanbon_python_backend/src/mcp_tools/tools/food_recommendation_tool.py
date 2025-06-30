#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@file: food_recommendation_tool.py
@description: 智能美食推荐工具
@author: AI Assistant
@created: 2024
"""

import logging
import random
from typing import Dict, Any, List
from datetime import datetime
from ..base_tool import BaseMCPTool

logger = logging.getLogger(__name__)

class FoodRecommendationTool(BaseMCPTool):
    """智能美食推荐工具"""
    
    def __init__(self, name: str, description: str, **config):
        super().__init__(name, description, **config)
        self.category = "recommendation"
        
        # 美食数据库
        self.food_database = self._initialize_food_database()
        
    def _initialize_food_database(self) -> Dict[str, Any]:
        """初始化美食数据库"""
        return {
            "cuisines": {
                "川菜": {
                    "dishes": ["麻婆豆腐", "回锅肉", "宫保鸡丁", "鱼香肉丝", "水煮鱼", "麻辣香锅"],
                    "characteristics": ["麻辣", "鲜香", "重口味"],
                    "weather_suitable": ["冬季", "阴雨"],
                    "difficulty": "medium"
                },
                "粤菜": {
                    "dishes": ["白切鸡", "烧鹅", "蒸排骨", "虾饺", "叉烧", "煲仔饭"],
                    "characteristics": ["清淡", "鲜美", "精致"],
                    "weather_suitable": ["夏季", "春季"],
                    "difficulty": "hard"
                },
                "湘菜": {
                    "dishes": ["剁椒鱼头", "口味虾", "辣椒炒肉", "东安子鸡", "糖醋排骨"],
                    "characteristics": ["辣", "鲜", "香"],
                    "weather_suitable": ["冬季", "秋季"],
                    "difficulty": "medium"
                },
                "家常菜": {
                    "dishes": ["番茄炒蛋", "青椒肉丝", "红烧肉", "糖醋里脊", "蒜蓉菠菜"],
                    "characteristics": ["简单", "营养", "家庭味"],
                    "weather_suitable": ["全年"],
                    "difficulty": "easy"
                }
            },
            "dietary_preferences": {
                "素食": ["麻婆豆腐", "蒜蓉菠菜", "红烧茄子", "干煸四季豆"],
                "低热量": ["蒸蛋羹", "清蒸鱼", "白灼菜心", "冬瓜汤"],
                "高蛋白": ["白切鸡", "蒸蛋", "牛肉汤", "豆腐炖鱼"],
                "儿童适宜": ["番茄炒蛋", "蒸蛋羹", "胡萝卜炖牛肉", "玉米排骨汤"]
            },
            "seasonal_foods": {
                "春季": ["春笋炒肉", "韭菜炒蛋", "菠菜汤", "豌豆尖"],
                "夏季": ["凉拌黄瓜", "冬瓜汤", "绿豆汤", "清蒸鱼"],
                "秋季": ["栗子烧鸡", "莲藕排骨汤", "银耳汤", "秋梨汤"],
                "冬季": ["羊肉汤", "红烧肉", "火锅", "炖牛肉"]
            },
            "mood_foods": {
                "开心": ["糖醋排骨", "可乐鸡翅", "红烧肉", "蛋炒饭"],
                "减压": ["小米粥", "银耳汤", "蒸蛋羹", "绿茶"],
                "聚会": ["火锅", "烤肉", "麻辣香锅", "干锅"],
                "浪漫": ["红酒牛排", "三文鱼", "意面", "提拉米苏"]
            }
        }
    
    async def execute(self, **parameters) -> Dict[str, Any]:
        """
        执行美食推荐
        
        Args:
            preferences: 用户偏好
            weather: 天气情况
            mood: 心情
            dietary_restrictions: 饮食限制
            skill_level: 烹饪技能水平
            occasion: 场合
        """
        try:
            preferences = parameters.get('preferences', {})
            weather = parameters.get('weather', '')
            mood = parameters.get('mood', '')
            dietary_restrictions = parameters.get('dietary_restrictions', [])
            skill_level = parameters.get('skill_level', 'medium')
            occasion = parameters.get('occasion', 'daily')
            
            # 生成推荐
            recommendations = self._generate_recommendations(
                preferences, weather, mood, dietary_restrictions, skill_level, occasion
            )
            
            return {
                "success": True,
                "recommendations": recommendations,
                "total_count": len(recommendations),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"美食推荐失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "recommendations": []
            }
    
    def _generate_recommendations(
        self, 
        preferences: Dict[str, Any],
        weather: str,
        mood: str,
        dietary_restrictions: List[str],
        skill_level: str,
        occasion: str
    ) -> List[Dict[str, Any]]:
        """生成推荐列表"""
        
        recommendations = []
        
        # 基于心情推荐
        if mood and mood in self.food_database["mood_foods"]:
            mood_foods = self.food_database["mood_foods"][mood]
            for food in mood_foods[:2]:  # 取前2个
                recommendations.append(self._create_recommendation(
                    food, "心情推荐", f"适合{mood}时享用"
                ))
        
        # 基于季节推荐
        season = self._get_current_season()
        if season in self.food_database["seasonal_foods"]:
            seasonal_foods = self.food_database["seasonal_foods"][season]
            for food in random.sample(seasonal_foods, min(2, len(seasonal_foods))):
                recommendations.append(self._create_recommendation(
                    food, "时令推荐", f"{season}时令美食"
                ))
        
        # 基于饮食偏好推荐
        for restriction in dietary_restrictions:
            if restriction in self.food_database["dietary_preferences"]:
                diet_foods = self.food_database["dietary_preferences"][restriction]
                for food in diet_foods[:2]:
                    recommendations.append(self._create_recommendation(
                        food, "健康推荐", f"适合{restriction}饮食"
                    ))
        
        # 基于技能水平推荐
        skill_recommendations = self._get_skill_based_recommendations(skill_level)
        recommendations.extend(skill_recommendations)
        
        # 去重并限制数量
        unique_recommendations = self._deduplicate_recommendations(recommendations)
        
        return unique_recommendations[:8]  # 最多返回8个推荐
    
    def _create_recommendation(self, dish_name: str, category: str, reason: str) -> Dict[str, Any]:
        """创建推荐项"""
        return {
            "dish_name": dish_name,
            "category": category,
            "reason": reason,
            "difficulty": self._get_dish_difficulty(dish_name),
            "cooking_time": self._estimate_cooking_time(dish_name),
            "ingredients": self._get_basic_ingredients(dish_name),
            "nutrition_score": random.randint(70, 95),  # 模拟营养评分
            "popularity": random.randint(60, 100)  # 模拟受欢迎程度
        }
    
    def _get_current_season(self) -> str:
        """获取当前季节"""
        month = datetime.now().month
        if month in [3, 4, 5]:
            return "春季"
        elif month in [6, 7, 8]:
            return "夏季"
        elif month in [9, 10, 11]:
            return "秋季"
        else:
            return "冬季"
    
    def _get_skill_based_recommendations(self, skill_level: str) -> List[Dict[str, Any]]:
        """基于技能水平的推荐"""
        recommendations = []
        
        for cuisine, info in self.food_database["cuisines"].items():
            if (skill_level == "easy" and info["difficulty"] == "easy") or \
               (skill_level == "medium" and info["difficulty"] in ["easy", "medium"]) or \
               (skill_level == "hard"):
                
                dish = random.choice(info["dishes"])
                recommendations.append(self._create_recommendation(
                    dish, "技能推荐", f"适合{skill_level}水平制作"
                ))
        
        return recommendations[:3]
    
    def _get_dish_difficulty(self, dish_name: str) -> str:
        """获取菜品难度"""
        easy_dishes = ["番茄炒蛋", "蒸蛋羹", "青椒肉丝"]
        hard_dishes = ["烧鹅", "叉烧", "蒸排骨"]
        
        if dish_name in easy_dishes:
            return "简单"
        elif dish_name in hard_dishes:
            return "困难"
        else:
            return "中等"
    
    def _estimate_cooking_time(self, dish_name: str) -> str:
        """估算烹饪时间"""
        quick_dishes = ["番茄炒蛋", "青椒肉丝", "蒜蓉菠菜"]
        slow_dishes = ["红烧肉", "炖牛肉", "羊肉汤"]
        
        if dish_name in quick_dishes:
            return "15-20分钟"
        elif dish_name in slow_dishes:
            return "1-2小时"
        else:
            return "30-45分钟"
    
    def _get_basic_ingredients(self, dish_name: str) -> List[str]:
        """获取基本食材"""
        ingredient_map = {
            "番茄炒蛋": ["鸡蛋", "番茄", "盐", "糖", "葱"],
            "麻婆豆腐": ["豆腐", "肉末", "豆瓣酱", "花椒", "葱"],
            "宫保鸡丁": ["鸡胸肉", "花生米", "青椒", "干辣椒", "生抽"],
            "红烧肉": ["五花肉", "冰糖", "生抽", "老抽", "料酒"]
        }
        
        return ingredient_map.get(dish_name, ["根据菜谱准备"])
    
    def _deduplicate_recommendations(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去除重复推荐"""
        seen_dishes = set()
        unique_recommendations = []
        
        for rec in recommendations:
            if rec["dish_name"] not in seen_dishes:
                seen_dishes.add(rec["dish_name"])
                unique_recommendations.append(rec)
        
        return unique_recommendations
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        """获取参数模式"""
        return {
            "type": "object",
            "properties": {
                "preferences": {
                    "type": "object",
                    "description": "用户偏好设置",
                    "properties": {
                        "cuisine_type": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "喜欢的菜系"
                        },
                        "spicy_level": {
                            "type": "string",
                            "enum": ["不辣", "微辣", "中辣", "重辣"],
                            "description": "辣度偏好"
                        }
                    }
                },
                "weather": {
                    "type": "string",
                    "description": "当前天气情况",
                    "enum": ["晴天", "雨天", "阴天", "炎热", "寒冷"]
                },
                "mood": {
                    "type": "string",
                    "description": "当前心情",
                    "enum": ["开心", "减压", "聚会", "浪漫"]
                },
                "dietary_restrictions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "饮食限制",
                    "enum": ["素食", "低热量", "高蛋白", "儿童适宜"]
                },
                "skill_level": {
                    "type": "string",
                    "description": "烹饪技能水平",
                    "enum": ["easy", "medium", "hard"],
                    "default": "medium"
                },
                "occasion": {
                    "type": "string",
                    "description": "用餐场合",
                    "enum": ["daily", "party", "date", "family"],
                    "default": "daily"
                }
            }
        } 
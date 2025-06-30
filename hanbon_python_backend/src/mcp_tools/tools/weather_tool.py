#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@file: weather_tool.py
@description: 天气查询工具 - 使用OpenWeather API
@author: AI Assistant
@created: 2024
"""

import aiohttp
import logging
from typing import Dict, Any, Optional
from ..base_tool import BaseMCPTool

logger = logging.getLogger(__name__)

class WeatherTool(BaseMCPTool):
    """天气查询工具 - 基于OpenWeather API"""
    
    def __init__(self, name: str, description: str, api_key: str = "", **config):
        super().__init__(name, description, **config)
        self.api_key = api_key or self._get_default_weather_key()
        self.category = "weather"
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        self.forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
        
    def _get_default_weather_key(self) -> str:
        """获取默认的OpenWeather API密钥"""
        import os
        return os.getenv('OPENWEATHER_API_KEY', '')
        
    async def execute(self, **parameters) -> Dict[str, Any]:
        """
        查询天气信息
        
        Args:
            city: 城市名称，如果不提供则使用默认城市
            extensions: 返回结果类型，base:返回实况天气 forecast:返回预报天气
            lat: 纬度（可选，与city二选一）
            lon: 经度（可选，与city二选一）
        """
        try:
            # 获取参数，提供默认值
            city = parameters.get('city', 'Changsha,CN')  # 默认城市为长沙
            extensions = parameters.get('extensions', 'base')
            lat = parameters.get('lat')
            lon = parameters.get('lon')
            
            logger.info(f"开始查询天气信息 - 城市: {city}, 类型: {extensions}")
            
            if not city and not (lat and lon):
                city = 'Changsha,CN'  # 确保有查询参数
            
            # 构建请求参数
            params = {
                'appid': self.api_key,
                'units': 'metric',  # 使用摄氏度
                'lang': 'zh_cn'     # 中文描述
            }
            
            # 根据参数类型添加位置信息
            if lat and lon:
                params['lat'] = lat
                params['lon'] = lon
            else:
                params['q'] = city
            
            # 选择API端点
            url = self.forecast_url if extensions == 'forecast' else self.base_url
            
            # 发送请求
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if extensions == 'forecast':
                            return self._parse_forecast_result(data)
                        else:
                            return self._parse_weather_result(data)
                    else:
                        logger.error(f"OpenWeather API请求失败，状态码: {response.status}")
                        return self._create_error_result(f"天气API请求失败: {response.status}")
                        
        except Exception as e:
            logger.error(f"天气查询失败: {e}")
            return self._create_error_result(str(e))
    
    def _parse_weather_result(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """解析当前天气查询结果"""
        try:
            # 添加调试日志
            logger.info(f"🔍 OpenWeather API原始返回数据: {data}")
            
            if 'main' not in data:
                error_msg = data.get('message', '未知错误')
                logger.warning(f"OpenWeather API返回错误: {error_msg}")
                return self._create_error_result(error_msg)
            
            main = data.get('main', {})
            weather = data.get('weather', [{}])[0]
            wind = data.get('wind', {})
            
            # 获取城市信息 - 改进处理逻辑
            city_name = data.get('name', '')
            country = data.get('sys', {}).get('country', '')
            
            # 如果没有城市名称，尝试从查询参数获取
            if not city_name:
                logger.warning("⚠️ API返回数据中没有城市名称(name字段)")
                # 可以从coord字段推断或使用默认值
                coord = data.get('coord', {})
                if coord:
                    city_name = f"经纬度({coord.get('lat', '--')}, {coord.get('lon', '--')})"
                else:
                    city_name = "长沙"  # 使用默认值
            
            # 组合城市和国家信息
            if country and city_name:
                # 特殊处理中国城市
                if country == 'CN':
                    city_name = f"{city_name}"  # 对中国城市不显示CN
                else:
                    city_name = f"{city_name}, {country}"
            elif not city_name:
                city_name = "未知城市"
                
            logger.info(f"🏙️ 解析出的城市名称: {city_name}")
            
            # 转换风向
            wind_deg = wind.get('deg', 0)
            wind_direction = self._deg_to_direction(wind_deg)
            
            result = {
                "success": True,
                "display_type": "weather_card",
                "city": city_name,
                "province": "",  # OpenWeather不直接提供省份信息
                "weather": {
                    "temperature": f"{main.get('temp', '--'):.1f}°C",
                    "humidity": f"{main.get('humidity', '--')}%",
                    "wind_direction": wind_direction,
                    "wind_power": f"{wind.get('speed', 0):.1f} m/s",
                    "description": weather.get('description', ''),
                    "feels_like": f"{main.get('feels_like', '--'):.1f}°C",
                    "pressure": f"{main.get('pressure', '--')} hPa",
                    "visibility": f"{data.get('visibility', '--')} m" if 'visibility' in data else '--',
                    "report_time": "当前"
                },
                "food_suggestions": self._get_weather_food_suggestions(
                    weather.get('description', ''),
                    str(int(main.get('temp', 20)))
                )
            }
            
            logger.info(f"天气查询成功: {result['city']} - {result['weather']['description']}")
            return result
                
        except Exception as e:
            logger.error(f"解析天气结果失败: {e}")
            return self._create_error_result(f"解析天气数据失败: {str(e)}")
    
    def _parse_forecast_result(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """解析天气预报结果"""
        try:
            if 'list' not in data:
                error_msg = data.get('message', '未知错误')
                logger.warning(f"OpenWeather API返回错误: {error_msg}")
                return self._create_error_result(error_msg)
            
            forecasts = data.get('list', [])
            city_info = data.get('city', {})
            
            if not forecasts:
                return self._create_error_result("未获取到预报数据")
            
            # 取第一个预报作为今日天气
            today_forecast = forecasts[0]
            main = today_forecast.get('main', {})
            weather = today_forecast.get('weather', [{}])[0]
            wind = today_forecast.get('wind', {})
            
            city_name = city_info.get('name', '未知城市')
            country = city_info.get('country', '')
            if country:
                city_name = f"{city_name}, {country}"
            
            wind_direction = self._deg_to_direction(wind.get('deg', 0))
            
            result = {
                "success": True,
                "display_type": "weather_card",
                "city": city_name,
                "province": "",
                "weather": {
                    "temperature": f"{main.get('temp', '--'):.1f}°C",
                    "humidity": f"{main.get('humidity', '--')}%",
                    "wind_direction": wind_direction,
                    "wind_power": f"{wind.get('speed', 0):.1f} m/s",
                    "description": weather.get('description', ''),
                    "feels_like": f"{main.get('feels_like', '--'):.1f}°C",
                    "pressure": f"{main.get('pressure', '--')} hPa",
                    "report_time": today_forecast.get('dt_txt', '').split(' ')[0] if 'dt_txt' in today_forecast else '今日'
                },
                "forecast": [
                    {
                        "date": forecast.get('dt_txt', '').split(' ')[0],
                        "time": forecast.get('dt_txt', '').split(' ')[1] if 'dt_txt' in forecast else '',
                        "temperature": f"{forecast.get('main', {}).get('temp', '--'):.1f}°C",
                        "description": forecast.get('weather', [{}])[0].get('description', ''),
                        "humidity": f"{forecast.get('main', {}).get('humidity', '--')}%"
                    }
                    for forecast in forecasts[:8]  # 显示未来8个时段
                ],
                "food_suggestions": self._get_weather_food_suggestions(
                    weather.get('description', ''),
                    str(int(main.get('temp', 20)))
                )
            }
            
            logger.info(f"天气预报查询成功: {result['city']} - {result['weather']['description']}")
            return result
            
        except Exception as e:
            logger.error(f"解析天气预报结果失败: {e}")
            return self._create_error_result(f"解析天气预报数据失败: {str(e)}")
    
    def _deg_to_direction(self, deg: float) -> str:
        """将风向角度转换为方向描述"""
        directions = [
            "北风", "东北风", "东风", "东南风",
            "南风", "西南风", "西风", "西北风"
        ]
        index = int((deg + 22.5) / 45) % 8
        return directions[index]
    
    def _get_weather_food_suggestions(self, weather_desc: str, temperature: str) -> list:
        """根据天气生成美食建议"""
        suggestions = []
        
        try:
            temp = int(temperature) if temperature.isdigit() else 20
            weather_lower = weather_desc.lower()
            
            # 根据温度推荐
            if temp < 10:
                suggestions.extend(["热汤面条", "麻辣火锅", "红烧肉", "羊肉汤"])
            elif temp > 30:
                suggestions.extend(["冰镇啤酒", "凉面", "冰淇淋", "冷饮"])
            else:
                suggestions.extend(["时令蔬菜", "清爽小菜", "温热汤品"])
            
            # 根据天气状况推荐
            if any(keyword in weather_lower for keyword in ['rain', '雨', 'drizzle', 'shower']):
                suggestions.extend(["热茶", "暖胃粥品", "温补汤品"])
            elif any(keyword in weather_lower for keyword in ['clear', '晴', 'sunny']):
                suggestions.extend(["户外烧烤", "清爽沙拉", "新鲜果汁"])
            elif any(keyword in weather_lower for keyword in ['snow', '雪', 'sleet']):
                suggestions.extend(["热乎火锅", "温热饮品", "滋补炖品"])
            elif any(keyword in weather_lower for keyword in ['cloud', '云', 'overcast']):
                suggestions.extend(["温和汤品", "舒适茶饮", "营养餐点"])
            
        except Exception as e:
            logger.warning(f"生成美食建议失败: {e}")
            suggestions = ["根据天气选择合适的美食", "注意饮食健康"]
        
        return suggestions[:4]  # 返回最多4个建议
    
    def _create_error_result(self, error_msg: str) -> Dict[str, Any]:
        """创建错误结果"""
        return {
            "success": False,
            "display_type": "error",
            "error": error_msg,
            "message": f"天气查询失败: {error_msg}"
        }
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        """获取参数模式"""
        return {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名称（可包含国家代码，如'Beijing,CN'），与经纬度二选一",
                    "default": "Changsha,CN"
                },
                "lat": {
                    "type": "number",
                    "description": "纬度（与city二选一，需同时提供lon）"
                },
                "lon": {
                    "type": "number", 
                    "description": "经度（与city二选一，需同时提供lat）"
                },
                "extensions": {
                    "type": "string",
                    "description": "返回结果类型：base(当前天气) 或 forecast(天气预报)",
                    "enum": ["base", "forecast"],
                    "default": "base"
                }
            },
            "required": []  # 所有参数都有默认值或可选
        }
    
    async def get_weather_by_location(self, longitude: float, latitude: float) -> Dict[str, Any]:
        """
        根据经纬度获取天气信息
        
        Args:
            longitude: 经度
            latitude: 纬度
        """
        try:
            return await self.execute(lat=latitude, lon=longitude)
        except Exception as e:
            logger.error(f"根据坐标获取天气失败: {e}")
            return self._create_error_result(str(e)) 
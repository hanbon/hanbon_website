from fastapi.responses import JSONResponse
import os
import requests
import json
from datetime import datetime
import asyncio

# API 配置
WEATHER_API_ID = os.getenv('WEATHER_API_ID', '10002477')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', '3752609fbeba1c8318a147a8f412bdf3')

async def get_food_image(food_name):
    """
    获取食物图片
    """
    try:
        from .sse import generate_food_image_baidu
        
        # 直接调用函数获取图片URL
        response = await generate_food_image_baidu(food=food_name, page=1, limit=1)
        
        # 从 JSONResponse 中提取数据
        data = response.body.decode()  # 将bytes转换为字符串
        data = json.loads(data)  # 解析JSON字符串
        
        if data.get('code') == 200 and data.get('data'):
            return data['data'][0]  # 返回第一张图片的 URL
        
        return None
    except Exception as e:
        print(f"获取图片失败: {str(e)}")
        return None

def get_weather_data():
    """
    获取长沙天气数据
    """
    try:
        url = f"https://cn.apihz.cn/api/tianqi/tqyb.php"
        params = {
            'id': WEATHER_API_ID,
            'key': WEATHER_API_KEY,
            'sheng': '湖南',
            'place': '长沙'
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if data.get('code') == 200:
            # 天气图标映射
            weather_icons = {
                '晴': '☀️',
                '多云': '⛅',
                '阴': '☁️',
                '小雨': '🌧️',
                '中雨': '🌧️',
                '大雨': '⛈️',
                '暴雨': '⛈️',
                '雷阵雨': '⛈️',
                '小雪': '🌨️',
                '中雪': '🌨️',
                '大雪': '🌨️',
                '雾': '🌫️',
                '霾': '🌫️'
            }
            
            weather = data.get('weather1', '晴朗')
            # 获取天气图标，如果没有对应的图标就使用默认的
            weather_icon = weather_icons.get(weather, '🌤️')
            
            return {
                'city': '长沙',
                'temperature': float(data.get('temperature', 25)),
                'weather': weather,
                'weather_icon': weather_icon,
                'humidity': int(data.get('humidity', 65)),
                'windDirection': data.get('windDirection', ''),
                'windScale': data.get('windScale', '')
            }
        else:
            print(f"天气 API 错误: {data.get('msg', '未知错误')}")
            return {
                'city': '长沙',
                'temperature': 25,
                'weather': '晴朗',
                'weather_icon': '☀️',
                'humidity': 65
            }
    except Exception as e:
        print(f"获取天气数据失败: {str(e)}")
        return {
            'city': '长沙',
            'temperature': 25,
            'weather': '晴朗',
            'weather_icon': '☀️',
            'humidity': 65
        }

def get_recommendations_by_weather(weather_data):
    """
    根据天气数据推荐食物
    """
    recommendations = []
    temp = weather_data['temperature']
    weather = weather_data['weather']
    
    # 根据温度和天气状况推荐食物
    if temp > 30:
        if '雨' in weather:
            recommendations.extend([
                {
                    'name': '酸辣汤',
                    'image': '',
                    'description': '雨天开胃暖身的首选'
                },
                {
                    'name': '冰镇绿豆汤',
                    'image': '',
                    'description': '消暑降火的传统饮品'
                }
            ])
        else:
            recommendations.extend([
                {
                    'name': '清爽凉面',
                    'image': '',
                    'description': '清凉解暑的夏日美食'
                },
                {
                    'name': '水果沙拉',
                    'image': '',
                    'description': '营养清爽的健康美食'
                }
            ])
    elif temp < 15:
        if '雨' in weather or '雪' in weather:
            recommendations.extend([
                {
                    'name': '暖心羊肉汤',
                    'image': '',
                    'description': '温暖身心的养生汤品'
                },
                {
                    'name': '麻辣火锅',
                    'image': '',
                    'description': '驱寒暖身的经典美食'
                }
            ])
        else:
            recommendations.extend([
                {
                    'name': '红烧牛肉面',
                    'image': '',
                    'description': '暖身开胃的美味面食'
                },
                {
                    'name': '姜母鸭',
                    'image': '',
                    'description': '温补养生的美味佳肴'
                }
            ])
    else:
        if '雨' in weather:
            recommendations.extend([
                {
                    'name': '皮蛋瘦肉粥',
                    'image': '',
                    'description': '养胃暖身的美味粥品'
                },
                {
                    'name': '葱油饼',
                    'image': '',
                    'description': '雨天必备的美味小吃'
                }
            ])
        else:
            recommendations.extend([
                {
                    'name': '时令炒菜',
                    'image': '',
                    'description': '应季蔬菜的美味搭配'
                },
                {
                    'name': '营养三明治',
                    'image': '',
                    'description': '均衡营养的快捷美食'
                }
            ])
    
    return recommendations

async def weather_recommendations():
    """
    基于天气获取食物推荐
    """
    try:
        # 获取实时天气数据
        weather_data = get_weather_data()
        
        # 根据天气推荐食物
        recommendations = get_recommendations_by_weather(weather_data)
        
        # 获取每个推荐食物的图片
        for recommendation in recommendations:
            image_url = await get_food_image(recommendation['name'])
            if image_url:
                recommendation['image'] = image_url
        
        return JSONResponse(content={
            'success': True,
            'weather': weather_data,
            'recommendations': recommendations
        })
    except Exception as e:
        return JSONResponse(content={
            'success': False,
            'error': str(e)
        }) 
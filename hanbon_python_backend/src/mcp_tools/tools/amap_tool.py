#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@file: amap_tool.py
@description: 高德地图搜索工具
@author: AI Assistant
@created: 2024
"""

import aiohttp
import logging
from typing import Dict, Any, List, Optional
from ..base_tool import BaseMCPTool

logger = logging.getLogger(__name__)

class AmapTool(BaseMCPTool):
    """高德地图搜索工具"""
    
    def __init__(self, name: str, description: str, api_key: str, **config):
        super().__init__(name, description, **config)
        self.api_key = api_key
        self.base_url = "https://restapi.amap.com/v3"
        self.category = "location"
        
    async def execute(self, **parameters) -> Dict[str, Any]:
        """
        执行高德地图搜索
        
        Args:
            keyword: 搜索关键词
            location: 中心点坐标 (经度,纬度)
            city: 城市名称
            radius: 搜索半径(米)
            type: POI类型
        """
        try:
            keyword = parameters.get('keyword', '')
            location = parameters.get('location', '')
            city = parameters.get('city', '长沙')
            radius = parameters.get('radius', '5000')
            poi_type = parameters.get('type', '')
            
            # 构建搜索参数
            search_params = {
                'key': self.api_key,
                'keywords': keyword,
                'city': city,
                'output': 'json',
                'offset': '20',  # 返回20个结果
                'page': '1',
                'extensions': 'all'  # 返回详细信息
            }
            
            # 如果有坐标，进行周边搜索
            if location:
                search_params['location'] = location
                search_params['radius'] = radius
                endpoint = f"{self.base_url}/place/around"
            else:
                # 关键词搜索
                endpoint = f"{self.base_url}/place/text"
            
            # 如果指定了POI类型
            if poi_type:
                search_params['types'] = poi_type
            
            # 发送请求
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, params=search_params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_search_results(data)
                    else:
                        raise Exception(f"API请求失败: {response.status}")
                        
        except Exception as e:
            logger.error(f"高德地图搜索失败: {e}")
            return {
                "error": str(e),
                "results": []
            }

    async def get_location_by_ip(self, ip_address: Optional[str] = None) -> Dict[str, Any]:
        """
        通过IP地址获取位置信息
        
        Args:
            ip_address: IP地址，如果不提供则自动使用客户端IP
            
        Returns:
            包含位置信息的字典
        """
        try:
            logger.info(f"开始IP定位，IP地址: {ip_address or '自动检测'}")
            
            # 构建IP定位请求参数
            params = {
                'key': self.api_key,
                'output': 'json'
            }
            
            # 如果提供了IP地址，则使用指定IP
            if ip_address:
                params['ip'] = ip_address
            
            endpoint = f"{self.base_url}/ip"
            
            # 发送请求
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_ip_location_result(data)
                    else:
                        raise Exception(f"IP定位请求失败: {response.status}")
                        
        except Exception as e:
            logger.error(f"IP定位失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "IP定位失败"
            }

    def _parse_ip_location_result(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """解析IP定位结果"""
        try:
            if data.get('status') != '1':
                return {
                    "success": False,
                    "error": data.get('info', '未知错误'),
                    "message": "IP定位失败"
                }
            
            province = data.get('province', '')
            city = data.get('city', '')
            adcode = data.get('adcode', '')
            rectangle = data.get('rectangle', '')
            
            # 解析矩形区域范围
            center_coordinates = None
            if rectangle:
                try:
                    # rectangle格式: "左下角经度,左下角纬度;右上角经度,右上角纬度"
                    coords = rectangle.split(';')
                    if len(coords) == 2:
                        left_bottom = coords[0].split(',')
                        right_top = coords[1].split(',')
                        if len(left_bottom) == 2 and len(right_top) == 2:
                            # 计算中心点坐标
                            center_lng = (float(left_bottom[0]) + float(right_top[0])) / 2
                            center_lat = (float(left_bottom[1]) + float(right_top[1])) / 2
                            center_coordinates = [center_lng, center_lat]
                            logger.info(f"IP定位计算中心坐标: 经度={center_lng}, 纬度={center_lat}")
                except Exception as e:
                    logger.warning(f"解析矩形区域失败: {e}")
            
            result = {
                "success": True,
                "location_type": "ip_location",
                "province": province,
                "city": city,
                "adcode": adcode,
                "rectangle": rectangle,
                "center_coordinates": center_coordinates,
                "formatted_address": f"{province}{city}" if province and city else (province or city or "未知位置"),
                "accuracy": "city_level",  # IP定位精度为城市级别
                "message": f"基于IP定位到{province}{city}"
            }
            
            logger.info(f"IP定位成功: {result['formatted_address']}")
            return result
            
        except Exception as e:
            logger.error(f"解析IP定位结果失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "解析IP定位结果失败"
            }
    
    def _parse_search_results(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """解析搜索结果"""
        if data.get('status') != '1':
            return {
                "success": False,
                "display_type": "error",
                "error": data.get('info', '未知错误'),
                "results": []
            }
        
        pois = data.get('pois', [])
        locations = []
        
        for poi in pois:
            # 解析坐标用于地图链接
            location_str = poi.get('location', '')
            logger.info(f"处理POI: {poi.get('name', 'unknown')} - 原始坐标: {location_str}")
            
            coordinates = location_str.split(',') if location_str else ['', '']
            longitude = coordinates[0].strip() if len(coordinates) > 0 else ''
            latitude = coordinates[1].strip() if len(coordinates) > 1 else ''
            
            # 验证坐标格式
            if not longitude or not latitude:
                logger.warning(f"POI {poi.get('name', 'unknown')} 坐标信息不完整: {location_str}")
                continue  # 跳过坐标不完整的POI
            
            try:
                # 验证坐标是否为有效数字
                lng_float = float(longitude)
                lat_float = float(latitude)
                logger.info(f"坐标验证通过: {poi.get('name', 'unknown')} - 经度: {lng_float}, 纬度: {lat_float}")
            except ValueError:
                logger.warning(f"POI {poi.get('name', 'unknown')} 坐标格式无效: 经度={longitude}, 纬度={latitude}")
                continue  # 跳过坐标格式无效的POI
            
            # 生成高德地图链接
            map_url = ""
            if longitude and latitude:
                map_url = f"https://uri.amap.com/marker?position={longitude},{latitude}&name={poi.get('name', '')}"
            
            # 解析评分
            rating = self._parse_rating(poi.get('biz_ext', {}))
            rating_display = f"{rating}" if rating > 0 else "暂无评分"
            
            # 解析距离显示
            distance = poi.get('distance', '')
            distance_display = ""
            if distance and distance != '':
                try:
                    dist_num = float(distance)
                    if dist_num >= 1000:
                        distance_display = f"{dist_num/1000:.1f}km"
                    else:
                        distance_display = f"{int(dist_num)}m"
                except:
                    distance_display = distance
            
            # 解析价格等级
            biz_ext = poi.get('biz_ext', {})
            cost = biz_ext.get('cost', '')
            price_level = ""
            if cost:
                try:
                    cost_num = int(cost)
                    if cost_num <= 30:
                        price_level = "经济实惠"
                    elif cost_num <= 80:
                        price_level = "中等消费"
                    else:
                        price_level = "高档消费"
                except:
                    price_level = f"人均{cost}元"
            
            location_item = {
                "id": poi.get('id'),
                "name": poi.get('name', ''),
                "address": poi.get('address', ''),
                "distance": distance_display,
                "rating": rating_display,
                "price_level": price_level,
                "map_url": map_url,
                "tel": poi.get('tel', ''),
                "type": poi.get('type', ''),
                "location_coords": location_str,  # 确保坐标格式为 "经度,纬度"
                "business_area": poi.get('business_area', ''),
                "tags": biz_ext.get('tag', '').split(';') if biz_ext.get('tag') else []
            }
            
            logger.info(f"成功处理POI: {location_item['name']} - 坐标: {location_item['location_coords']}")
            locations.append(location_item)
        
        logger.info(f"搜索完成，返回 {len(locations)} 个有效位置")
        
        return {
            "success": True,
            "display_type": "location_list",
            "display_data": {
                "total_found": len(locations),
                "locations": locations
            },
            "display_config": {
                "show_map_links": True,
                "show_ratings": True,
                "show_distance": True
            },
            "suggestion": data.get('suggestion', {})
        }
    
    def _parse_rating(self, biz_ext: Dict[str, Any]) -> float:
        """解析评分"""
        try:
            rating = biz_ext.get('rating', '0')
            return float(rating) if rating else 0.0
        except (ValueError, TypeError):
            return 0.0
    
    def _extract_photos(self, photos: List[Dict[str, Any]]) -> List[str]:
        """提取照片URL"""
        photo_urls = []
        for photo in photos[:5]:  # 最多取5张照片
            if 'url' in photo:
                photo_urls.append(photo['url'])
        return photo_urls
    
    def _parse_opening_hours(self, biz_ext: Dict[str, Any]) -> str:
        """解析营业时间"""
        return biz_ext.get('opentime', '营业时间未知')
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        """获取参数模式"""
        return {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "搜索关键词，如'火锅'、'川菜'等"
                },
                "location": {
                    "type": "string",
                    "description": "中心点坐标，格式：经度,纬度",
                    "pattern": r"^[\d.]+,[\d.]+$"
                },
                "city": {
                    "type": "string",
                    "description": "城市名称",
                    "default": "长沙"
                },
                "radius": {
                    "type": "string",
                    "description": "搜索半径（米），默认5000",
                    "default": "5000"
                },
                "type": {
                    "type": "string",
                    "description": "POI类型，如'050000'(餐饮服务)",
                    "enum": [
                        "050000",  # 餐饮服务
                        "050100",  # 中餐厅
                        "050200",  # 外国餐厅
                        "050300",  # 快餐厅
                        "050400",  # 休闲餐饮场所
                        "050500"   # 咖啡厅
                    ]
                }
            },
            "required": ["keyword"]
        }

    async def search_restaurants_by_cuisine(self, cuisine: str, city: str = "长沙") -> Dict[str, Any]:
        """
        按菜系搜索餐厅
        
        Args:
            cuisine: 菜系名称
            city: 城市
        """
        return await self.execute(keyword=cuisine, city=city, type="050000")
    
    async def search_nearby_restaurants(self, longitude: float, latitude: float, radius: int = 2000) -> Dict[str, Any]:
        """
        搜索附近餐厅
        
        Args:
            longitude: 经度
            latitude: 纬度  
            radius: 搜索半径
        """
        location = f"{longitude},{latitude}"
        return await self.execute(
            keyword="餐厅",
            location=location,
            radius=str(radius),
            type="050000"
        )
    
    async def get_restaurant_details(self, poi_id: str) -> Dict[str, Any]:
        """
        获取餐厅详细信息
        
        Args:
            poi_id: POI ID
        """
        try:
            detail_params = {
                'key': self.api_key,
                'id': poi_id,
                'output': 'json',
                'extensions': 'all'
            }
            
            endpoint = f"{self.base_url}/place/detail"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, params=detail_params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_detail_result(data)
                    else:
                        raise Exception(f"获取详情失败: {response.status}")
                        
        except Exception as e:
            logger.error(f"获取餐厅详情失败: {e}")
            return {"error": str(e)}
    
    def _parse_detail_result(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """解析详情结果"""
        if data.get('status') != '1':
            return {"error": data.get('info', '未知错误')}
        
        pois = data.get('pois', [])
        if not pois:
            return {"error": "未找到餐厅信息"}
        
        poi = pois[0]
        
        return {
            "id": poi.get('id'),
            "name": poi.get('name'),
            "type": poi.get('type'),
            "address": poi.get('address'),
            "location": poi.get('location'),
            "tel": poi.get('tel', ''),
            "website": poi.get('website', ''),
            "email": poi.get('email', ''),
            "postcode": poi.get('postcode', ''),
            "business_area": poi.get('business_area', ''),
            "indoor_map": poi.get('indoor_map', False),
            "photos": self._extract_photos(poi.get('photos', [])),
            "children": poi.get('children', []),
            "biz_ext": poi.get('biz_ext', {})
        } 
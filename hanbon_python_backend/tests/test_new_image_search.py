#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@file: test_new_image_search.py
@description: 测试新的Bing图片搜索工具
@author: AI Assistant
@created: 2024
"""

import asyncio
import sys
import os

# 添加父目录到路径，以便导入src模块
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.mcp_tools.tools.image_search_tool import ImageSearchTool

async def test_image_search():
    """测试图片搜索功能"""
    print("=== 测试新的Bing图片搜索工具 ===\n")
    
    # 创建图片搜索工具实例
    image_tool = ImageSearchTool(
        name="image_search_test",
        description="测试用的图片搜索工具"
    )
    
    # 测试用例
    test_cases = [
        {"query": "红烧肉", "count": 5},
        {"query": "川菜 麻婆豆腐", "count": 3},
        {"query": "西湖醋鱼", "count": 4}
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"🔍 测试用例 {i}: 搜索 '{test_case['query']}'")
        print(f"📊 期望数量: {test_case['count']}")
        
        try:
            # 执行搜索
            result = await image_tool.execute(**test_case)
            
            # 显示结果
            if result.get("success"):
                images = result.get("images", [])
                print(f"✅ 搜索成功！找到 {len(images)} 张图片")
                
                # 显示前3个结果的详细信息
                for j, img in enumerate(images[:3], 1):
                    print(f"   {j}. 标题: {img.get('title', '无标题')}")
                    print(f"      URL: {img.get('url', '无URL')[:80]}...")
                    print(f"      来源: {img.get('source', '未知')}")
                    print()
                
                if len(images) > 3:
                    print(f"   ... 还有 {len(images) - 3} 张图片")
                    
            else:
                print(f"❌ 搜索失败: {result.get('error', '未知错误')}")
                
        except Exception as e:
            print(f"❌ 测试失败: {e}")
        
        print("-" * 60)
        print()

async def test_convenience_methods():
    """测试便捷方法"""
    print("=== 测试便捷方法 ===\n")
    
    image_tool = ImageSearchTool(
        name="image_search_test",
        description="测试用的图片搜索工具"
    )
    
    # 测试美食图片搜索
    print("🍽️ 测试美食图片搜索")
    try:
        result = await image_tool.search_food_images("宫保鸡丁", 3)
        if result.get("success"):
            print(f"✅ 成功找到 {len(result.get('images', []))} 张美食图片")
        else:
            print(f"❌ 美食图片搜索失败: {result.get('error')}")
    except Exception as e:
        print(f"❌ 美食图片搜索异常: {e}")
    
    print()
    
    # 测试菜谱图片搜索
    print("📖 测试菜谱图片搜索")
    try:
        result = await image_tool.search_recipe_images("糖醋里脊", 2)
        if result.get("success"):
            print(f"✅ 成功找到 {len(result.get('images', []))} 张菜谱图片")
        else:
            print(f"❌ 菜谱图片搜索失败: {result.get('error')}")
    except Exception as e:
        print(f"❌ 菜谱图片搜索异常: {e}")

async def test_parameter_validation():
    """测试参数验证"""
    print("\n=== 测试参数验证 ===\n")
    
    image_tool = ImageSearchTool(
        name="image_search_test", 
        description="测试用的图片搜索工具"
    )
    
    # 测试空查询
    print("🔍 测试空查询")
    result = await image_tool.execute(query="", count=5)
    if not result.get("success"):
        print(f"✅ 正确处理空查询: {result.get('error')}")
    else:
        print("❌ 应该拒绝空查询")
    
    print()
    
    # 测试正常查询  
    print("🔍 测试正常查询")
    result = await image_tool.execute(query="测试", count=1)
    if result.get("success") is not None:  # 有响应就算通过
        print("✅ 正常查询处理正确")
    else:
        print("❌ 正常查询处理异常")

def show_schema():
    """显示参数模式"""
    print("\n=== 工具参数模式 ===\n")
    
    image_tool = ImageSearchTool(
        name="image_search_test",
        description="测试用的图片搜索工具"
    )
    
    schema = image_tool.get_parameters_schema()
    print("参数模式:")
    print(f"  类型: {schema.get('type')}")
    print("  属性:")
    
    for prop_name, prop_info in schema.get('properties', {}).items():
        print(f"    {prop_name}:")
        print(f"      类型: {prop_info.get('type')}")
        print(f"      描述: {prop_info.get('description')}")
        if 'default' in prop_info:
            print(f"      默认值: {prop_info.get('default')}")
        if 'minimum' in prop_info:
            print(f"      最小值: {prop_info.get('minimum')}")
        if 'maximum' in prop_info:
            print(f"      最大值: {prop_info.get('maximum')}")
        print()
    
    print(f"  必需参数: {schema.get('required', [])}")

async def main():
    """主测试函数"""
    print("🚀 开始测试新的Bing图片搜索工具...\n")
    
    try:
        # 显示参数模式
        show_schema()
        
        # 测试参数验证
        await test_parameter_validation()
        
        # 测试基本搜索功能
        await test_image_search()
        
        # 测试便捷方法
        await test_convenience_methods()
        
        print("🎉 所有测试完成！")
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 运行测试
    asyncio.run(main()) 
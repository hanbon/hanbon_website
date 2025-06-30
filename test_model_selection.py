#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@file: test_model_selection.py
@description: 测试模型选择功能的脚本
@author: AI Assistant
@created: 2024
"""

import requests
import json

def test_available_models():
    """测试获取可用模型列表"""
    print("=== 测试获取可用模型列表 ===")
    
    try:
        response = requests.get("http://localhost:8000/models/available")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 接口调用成功")
            print(f"📊 响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if data.get('models'):
                print(f"🎯 可用模型数量: {len(data['models'])}")
                for model in data['models']:
                    print(f"   - {model['name']} ({model['id']}): {model['description']}")
            else:
                print("⚠️  没有可用的模型（可能是因为API密钥未配置）")
                
            print(f"🔧 默认模型: {data.get('default_model', 'N/A')}")
            
        else:
            print(f"❌ 接口调用失败: HTTP {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")

def test_chat_with_model_selection():
    """测试带模型选择的聊天功能"""
    print("\n=== 测试带模型选择的聊天功能 ===")
    
    test_cases = [
        {
            "message": "你好，请推荐一道简单的家常菜",
            "model": "deepseek",
            "description": "使用DeepSeek模型"
        },
        {
            "message": "请介绍一下川菜的特点",
            "model": "qwen", 
            "description": "使用Qwen模型（如果可用）"
        },
        {
            "message": "营养搭配有什么建议吗？",
            "model": None,  # 使用默认模型
            "description": "使用默认模型"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- 测试用例 {i}: {test_case['description']} ---")
        
        payload = {
            "message": test_case["message"],
            "session_id": f"test_session_{i}",
            "tools_enabled": ["food_recommendation"]
        }
        
        if test_case["model"]:
            payload["model"] = test_case["model"]
        
        try:
            print(f"📤 发送请求: {test_case['message']}")
            print(f"🤖 指定模型: {test_case['model'] or '默认'}")
            
            response = requests.post(
                "http://localhost:8000/chat",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 请求成功")
                print(f"📝 AI回复: {data.get('response', 'N/A')[:100]}...")
                print(f"🛠️ 使用工具: {data.get('tools_used', [])}")
                print(f"💾 记忆更新: {data.get('memory_updated', False)}")
            else:
                print(f"❌ 请求失败: HTTP {response.status_code}")
                print(f"错误信息: {response.text}")
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")

def test_stream_chat_with_model():
    """测试流式聊天与模型选择"""
    print("\n=== 测试流式聊天与模型选择 ===")
    
    payload = {
        "message": "请用流式方式回答：川菜有哪些特色菜？",
        "session_id": "test_stream_session",
        "tools_enabled": ["food_recommendation"],
        "model": "deepseek"
    }
    
    try:
        print(f"📤 发送流式请求: {payload['message']}")
        print(f"🤖 指定模型: {payload['model']}")
        
        response = requests.post(
            "http://localhost:8000/chat/stream",
            headers={"Content-Type": "application/json"},
            json=payload,
            stream=True,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ 流式请求成功，接收数据:")
            chunk_count = 0
            
            for line in response.iter_lines():
                if line:
                    line_text = line.decode('utf-8')
                    if line_text.startswith('data: '):
                        chunk_count += 1
                        data_str = line_text[6:].strip()
                        
                        if data_str and data_str != '[DONE]':
                            try:
                                chunk_data = json.loads(data_str)
                                chunk_type = chunk_data.get('type', 'unknown')
                                content = chunk_data.get('content', '')
                                
                                if chunk_type == 'response_chunk' and content:
                                    print(content, end='', flush=True)
                                elif chunk_type == 'complete':
                                    print(f"\n🎯 完成信号收到，使用工具: {chunk_data.get('content', {}).get('tools_used', [])}")
                                    break
                                elif chunk_type == 'error':
                                    print(f"\n❌ 错误: {content}")
                                    break
                                    
                            except json.JSONDecodeError:
                                pass
                        
                        if chunk_count >= 100:  # 限制输出长度
                            print("\n... (输出被截断)")
                            break
            
            print(f"\n📊 总共接收到 {chunk_count} 个数据块")
        else:
            print(f"❌ 流式请求失败: HTTP {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 流式请求异常: {e}")

if __name__ == "__main__":
    print("🚀 开始测试模型选择功能\n")
    
    # 测试1: 获取可用模型列表
    test_available_models()
    
    # 测试2: 带模型选择的普通聊天
    test_chat_with_model_selection()
    
    # 测试3: 带模型选择的流式聊天
    test_stream_chat_with_model()
    
    print("\n🏁 测试完成！")
    print("\n💡 提示:")
    print("- 如果模型列表为空，请在 .env 文件中配置相应的API密钥")
    print("- 如果聊天请求失败，请检查API密钥是否有效和有余额")
    print("- 可以在前端界面中使用模型选择功能进行可视化测试") 
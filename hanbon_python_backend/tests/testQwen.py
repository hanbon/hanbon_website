import os
import json
import requests
import base64
import time

def check_task_status(task_id: str, api_key: str) -> dict:
    """
    检查任务状态
    """
    url = f'https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}'
    headers = {
        'Authorization': f'Bearer {api_key}',
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def test_generate_food_image():
    """
    @description 测试食物图片生成功能
    @reference https://bailian.console.aliyun.com/ 阿里巴巴 Qwen API
    """
    # API 配置
    api_key = 'sk-c2bdd7333575491e98eb3d804aea7c0a'
    url = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis'

    try:
        # 测试生成红烧肉图片
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'X-DashScope-Async': 'enable'
        }
        
        data = {
            "model": "wanx2.1-t2i-turbo",
            "input": {
                "prompt": "生成一张精美的红烧肉美食图片，要求：1. 高清晰度；2. 专业的美食摄影风格；3. 突出食物的质感和细节；4. 适当的装盘和背景。"
            },
            "parameters": {
                "size": "1024x1024",
                "n": 1,
            }
        }
        
        # 发送请求
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        # 解析响应获取任务ID
        result = response.json()
        task_id = result['output']['task_id']
        print(f"✅ 任务已提交，任务ID: {task_id}")
        
        # 轮询检查任务状态
        max_retries = 30  # 最大重试次数
        retry_interval = 2  # 重试间隔（秒）
        
        for i in range(max_retries):
            print(f"⏳ 正在检查任务状态... ({i + 1}/{max_retries})")
            task_result = check_task_status(task_id, api_key)
            
            if task_result['output']['task_status'] == 'SUCCEEDED':
                # 获取图片URL
                image_url = task_result['output']['results'][0]['url']
                
                # 下载图片
                image_response = requests.get(image_url)
                image_response.raise_for_status()
                
                # 保存图片
                with open("test_generated_food.png", "wb") as f:
                    f.write(image_response.content)
                    
                print("✅ 图片生成测试成功！")
                print("📝 图片已保存为: test_generated_food.png")
                return
            
            elif task_result['output']['task_status'] == 'FAILED':
                raise Exception(f"任务失败: {task_result.get('message', '未知错误')}")
            
            elif task_result['output']['task_status'] in ['PENDING', 'RUNNING']:
                time.sleep(retry_interval)
                continue
            
            else:
                raise Exception(f"未知的任务状态: {task_result['output']['task_status']}")
        
        raise Exception("任务超时")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        raise e

if __name__ == "__main__":
    test_generate_food_image()
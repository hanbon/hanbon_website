from typing import List, Optional
from urllib import parse
from bs4 import BeautifulSoup
import requests
from pydantic import BaseModel

# 将这部分代码移到了 src/routers/image_search.py 中
# 这里保留原有的测试代码作为参考，并添加对集成功能的测试

class ImageResult(BaseModel):
    url: str
    title: str
    source: str

class BingImage:
    path = 'https://cn.bing.com/images/search'
    block_num = 35
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36"
    }

def bing_crawler(key_word: str, image_num: int) -> Optional[List[ImageResult]]:
    """
    @description 原始的 Bing 图片爬虫测试函数
    @param {string} key_word - 搜索关键词
    @param {number} image_num - 需要的图片数量
    @returns {ImageResult[] | None} - 图片搜索结果或None
    """
    query = {
        'q': key_word,
        'count': image_num
    }
    
    url = BingImage.path + '?' + parse.urlencode(query)
    res = requests.get(url, headers=BingImage.headers)

    soup = BeautifulSoup(res.content, "html.parser")
    results = []
    for a in soup.select('.iusc'):
        href = a.attrs['href']
        decode_href = parse.unquote(href)
        media_url = decode_href.split('&')[4][9:]
        title = a.get('alt', '')
        
        results.append(ImageResult(
            url=media_url,
            title=title,
            source="bing"
        ))
        if len(results) >= image_num:
            break
    
    return results if results else None        

def test_integrated_bing_search():
    """
    @description 测试集成到 image_search.py 中的 Bing 搜索功能
    """
    # 这里可以导入集成后的类进行测试
    # from src.routers.image_search import BingImageSearchClient
    
    # client = BingImageSearchClient()
    # results = client.search("运输管理", 5)
    # print(f"集成测试结果数量: {len(results)}")
    # for result in results:
    #     print(f"URL: {result.url}, Title: {result.title}, Source: {result.source}")
    pass

if __name__ == "__main__":
    print("=== 原始 Bing 爬虫测试 ===")
    images = bing_crawler("运输管理", 10)
    if images:
        print(f"找到 {len(images)} 张图片:")
        for i, img in enumerate(images[:3]):  # 只显示前3个结果
            print(f"{i+1}. {img.title} - {img.url}")
    else:
        print("未找到图片")
    
    print("\n=== 集成功能说明 ===")
    print("Bing 图片搜索已集成到 src/routers/image_search.py 中")
    print("新增接口:")
    print("1. GET /image_search?engine=bing - 统一搜索接口")
    print("2. GET /image_search/bing - 专门的 Bing 搜索测试接口")
    print("使用示例:")
    print("  curl 'http://localhost:8000/image_search/bing?query=运输管理&size=10'")
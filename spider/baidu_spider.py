import requests
from bs4 import BeautifulSoup
import urllib.parse


def baidu_spider(keyword: str) -> dict:
    """
    百度搜索爬虫，根据关键词获取搜索结果
    
    Args:
        keyword: 搜索关键词
        
    Returns:
        包含搜索结果的字典，结构为 {"result": [{'title': '标题', 'summary': '概要', 'url': '链接', 'cover_url': '封面链接'}]}
    """
    try:
        # 编码关键词
        encoded_keyword = urllib.parse.quote(keyword)
        url = f"https://www.baidu.com/s?wd={encoded_keyword}"
        
        # 设置请求头，模拟浏览器访问
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,en-GB;q=0.6',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache'
        }
        
        # 发送请求
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # 检查请求是否成功
        
        # 解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取搜索结果
        results = []
        
        # 百度搜索结果通常在id为"content_left"的div中
        content_left = soup.find('div', id='content_left')
        if not content_left:
            return {"result": [], "error": "未找到搜索结果区域"}
        
        # 查找所有搜索结果项
        result_items = content_left.find_all('div', class_='result', recursive=False)
        
        for item in result_items:
            # 提取标题
            title_tag = item.find('h3')
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            
            # 提取链接
            url_tag = title_tag.find('a')
            if not url_tag:
                continue
            url = url_tag.get('href', '')
            
            # 提取概要
            summary_tag = item.find('div', class_='c-abstract')
            if not summary_tag:
                summary_tag = item.find('div', class_='content-right_8Zs40')
            summary = summary_tag.get_text(strip=True) if summary_tag else ''
            
            # 提取封面URL（如果有）
            cover_url = ''
            img_tag = item.find('img')
            if img_tag:
                cover_url = img_tag.get('src', '')
                # 处理相对路径
                if cover_url and not cover_url.startswith(('http://', 'https://')):
                    cover_url = f"https://www.baidu.com{cover_url}"
            
            # 添加到结果列表
            if title and url:
                results.append({
                    'title': title,
                    'summary': summary,
                    'url': url,
                    'cover_url': cover_url
                })
        
        return {"result": results}
        
    except Exception as e:
        return {"result": [], "error": str(e)}


# dify 代码执行规范的入口函数
def main(arg1: str):
    """
    dify 代码执行入口函数
    
    Args:
        arg1: 搜索关键词
        
    Returns:
        包含搜索结果的字典
    """
    return baidu_spider(arg1)


if __name__ == "__main__":
    # 测试代码
    test_keyword = "成都"
    result = baidu_spider(test_keyword)
    print(f"搜索关键词: {test_keyword}")
    print(f"结果数量: {len(result['result'])}")
    print("\n前3条结果:")
    for i, item in enumerate(result['result'][:3], 1):
        print(f"\n结果 {i}:")
        print(f"标题: {item['title']}")
        print(f"概要: {item['summary']}")
        print(f"URL: {item['url']}")
        print(f"封面URL: {item['cover_url']}")

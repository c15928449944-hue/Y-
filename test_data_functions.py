import requests
import json

# 测试登录
login_url = 'http://127.0.0.1:5000/login'
login_data = {
    'username': 'admin',
    'password': 'admin888'
}

with requests.Session() as s:
    # 登录
    response = s.post(login_url, data=login_data)
    print(f'登录状态码: {response.status_code}')
    
    # 测试搜索API
    search_url = 'http://127.0.0.1:5000/api/search'
    search_data = {
        'keyword': '成都'
    }
    response = s.post(search_url, json=search_data)
    search_result = response.json()
    print(f'搜索结果数量: {len(search_result.get("result", []))}')
    
    # 测试保存数据到数据库
    if search_result.get('result'):
        save_url = 'http://127.0.0.1:5000/api/save_results'
        save_data = {
            'keyword': '成都',
            'data': search_result['result']
        }
        response = s.post(save_url, json=save_data)
        print(f'保存状态: {response.json().get("message")}')
    
    # 测试从数据库检索数据
    retrieve_url = 'http://127.0.0.1:5000/api/search_results?keyword=成都'
    response = s.get(retrieve_url)
    retrieve_result = response.json()
    print(f'检索到的数据数量: {len(retrieve_result.get("results", []))}')
    print(f'总数据数量: {retrieve_result.get("total")}')
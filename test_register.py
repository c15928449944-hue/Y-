import requests
import random

# 测试注册功能
def test_register():
    base_url = 'http://127.0.0.1:5000'
    
    # 生成随机用户名避免冲突
    random_username = f'test_user_{random.randint(1000, 9999)}'
    password = 'test_password_123'
    
    print(f"测试注册功能...")
    print(f"用户名: {random_username}")
    print(f"密码: {password}")
    
    # 测试注册
    register_data = {
        'username': random_username,
        'password': password,
        'confirm_password': password
    }
    
    try:
        # 发送注册请求
        register_response = requests.post(f'{base_url}/register', data=register_data)
        print(f"\n注册请求状态码: {register_response.status_code}")
        
        if register_response.status_code == 200:
            # 检查注册是否成功
            if '注册成功' in register_response.text:
                print("✓ 注册成功！")
                
                # 测试登录新注册的账号
                login_data = {
                    'username': random_username,
                    'password': password
                }
                
                login_response = requests.post(f'{base_url}/login', data=login_data, allow_redirects=False)
                print(f"登录请求状态码: {login_response.status_code}")
                
                if login_response.status_code == 302 and login_response.headers.get('Location') == '/dashboard':
                    print("✓ 新注册账号登录成功！")
                    return True
                else:
                    print("✗ 新注册账号登录失败！")
                    return False
            else:
                print("✗ 注册失败！")
                print(f"响应内容: {register_response.text[:500]}...")
                return False
        else:
            print(f"✗ 注册请求失败，状态码: {register_response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ 测试过程中发生错误: {str(e)}")
        return False

# 测试密码不一致情况
def test_register_password_mismatch():
    base_url = 'http://127.0.0.1:5000'
    
    random_username = f'test_user_{random.randint(1000, 9999)}'
    
    print(f"\n测试密码不一致情况...")
    print(f"用户名: {random_username}")
    
    register_data = {
        'username': random_username,
        'password': 'password1',
        'confirm_password': 'password2'  # 密码不一致
    }
    
    try:
        response = requests.post(f'{base_url}/register', data=register_data)
        if response.status_code == 200 and '两次输入的密码不一致' in response.text:
            print("✓ 密码不一致验证成功！")
            return True
        else:
            print("✗ 密码不一致验证失败！")
            return False
    except Exception as e:
        print(f"✗ 测试过程中发生错误: {str(e)}")
        return False

# 测试用户名已存在情况
def test_register_username_exists():
    base_url = 'http://127.0.0.1:5000'
    
    # 使用已知存在的用户名（admin）
    existing_username = 'admin'
    
    print(f"\n测试用户名已存在情况...")
    print(f"用户名: {existing_username}")
    
    register_data = {
        'username': existing_username,
        'password': 'test_password',
        'confirm_password': 'test_password'
    }
    
    try:
        response = requests.post(f'{base_url}/register', data=register_data)
        if response.status_code == 200 and '用户名已存在' in response.text:
            print("✓ 用户名已存在验证成功！")
            return True
        else:
            print("✗ 用户名已存在验证失败！")
            return False
    except Exception as e:
        print(f"✗ 测试过程中发生错误: {str(e)}")
        return False

if __name__ == '__main__':
    print("=== 注册功能测试 ===")
    
    test_results = []
    test_results.append(test_register())
    test_results.append(test_register_password_mismatch())
    test_results.append(test_register_username_exists())
    
    print(f"\n=== 测试结果统计 ===")
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"通过测试: {passed}/{total}")
    
    if passed == total:
        print("🎉 所有测试通过！注册功能正常工作")
    else:
        print("❌ 部分测试失败，请检查注册功能")
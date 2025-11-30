// 加载服务器列表
function loadServers() {
    fetch('/api/servers')
        .then(response => response.json())
        .then(servers => {
            const serverSelect = document.getElementById('server');
            serverSelect.innerHTML = '';
            
            servers.forEach(server => {
                const option = document.createElement('option');
                option.value = server.url;
                option.textContent = server.name;
                serverSelect.appendChild(option);
            });
            
            // 默认选择第一个服务器
            if (servers.length > 0) {
                serverSelect.value = servers[0].url;
            }
        })
        .catch(error => {
            console.error('加载服务器列表失败:', error);
            const serverSelect = document.getElementById('server');
            serverSelect.innerHTML = '<option value="http://localhost:5000">默认服务器</option>';
        });
}

// 验证用户名
function validateUsername(username) {
    const errorElement = document.getElementById('username-error');
    
    if (!username || username.trim() === '') {
        errorElement.textContent = '请输入昵称';
        return false;
    }
    
    if (username.length > 20) {
        errorElement.textContent = '昵称不能超过20个字符';
        return false;
    }
    
    if (username.includes('@') || username.includes('<') || username.includes('>')) {
        errorElement.textContent = '昵称不能包含特殊字符';
        return false;
    }
    
    errorElement.textContent = '';
    return true;
}

// 检查用户名是否已存在
function checkUsernameExists(username) {
    return fetch(`/api/check_username?username=${encodeURIComponent(username)}`)
        .then(response => response.json())
        .then(data => data.exists);
}

// 登录处理
async function handleLogin() {
    const username = document.getElementById('username').value.trim();
    const serverUrl = document.getElementById('server').value;
    const loginBtn = document.getElementById('login-btn');
    
    // 基本验证
    if (!validateUsername(username)) {
        return;
    }
    
    // 检查用户名是否已存在
    loginBtn.disabled = true;
    loginBtn.textContent = '登录中...';
    
    try {
        const exists = await checkUsernameExists(username);
        
        if (exists) {
            document.getElementById('username-error').textContent = '该昵称已被使用';
            loginBtn.disabled = false;
            loginBtn.textContent = '登录';
            return;
        }
        
        // 登录成功，跳转到聊天页面
        window.location.href = `/chat?username=${encodeURIComponent(username)}`;
    } catch (error) {
        console.error('登录失败:', error);
        alert('登录失败，请稍后重试');
        loginBtn.disabled = false;
        loginBtn.textContent = '登录';
    }
}

// 事件监听
function setupEventListeners() {
    // 登录按钮点击事件
    document.getElementById('login-btn').addEventListener('click', handleLogin);
    
    // 输入框回车事件
    document.getElementById('username').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleLogin();
        }
    });
    
    // 输入框输入事件，实时验证
    document.getElementById('username').addEventListener('input', (e) => {
        validateUsername(e.target.value);
    });
}

// 页面加载完成后初始化
window.addEventListener('DOMContentLoaded', () => {
    loadServers();
    setupEventListeners();
});
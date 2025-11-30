// 获取URL参数中的用户名
function getUsername() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('username');
}

// 格式化时间
function formatTime() {
    const now = new Date();
    const hours = now.getHours().toString().padStart(2, '0');
    const minutes = now.getMinutes().toString().padStart(2, '0');
    return `${hours}:${minutes}`;
}

// 创建消息元素
function createMessageElement(message) {
    const div = document.createElement('div');
    div.className = `message ${message.username === username ? 'user' : 'other'}`;
    
    // 添加消息头部
    const header = document.createElement('div');
    header.className = 'message-header';
    header.textContent = message.username;
    div.appendChild(header);
    
    // 添加消息内容
    const content = document.createElement('div');
    content.className = 'message-content';
    
    // 根据消息类型处理内容
    if (message.type === 'normal') {
        content.textContent = message.message;
    } else if (message.type === 'movie') {
        content.textContent = message.message;
        // 添加电影播放卡片
        const movieCard = document.createElement('div');
        movieCard.className = 'movie-card';
        const moviePlayer = document.createElement('div');
        moviePlayer.className = 'movie-player';
        
        // 创建视频iframe
        const iframe = document.createElement('iframe');
        iframe.src = message.movie_url;
        iframe.allowFullscreen = true;
        iframe.title = '电影播放';
        
        moviePlayer.appendChild(iframe);
        movieCard.appendChild(moviePlayer);
        content.appendChild(movieCard);
    } else if (message.type === 'ai_chat') {
        content.textContent = message.message;
        // 添加AI对话和回复
        const aiChat = document.createElement('div');
        aiChat.className = 'ai-chat';
        aiChat.textContent = `向川小农AI提问: ${message.ai_message}`;
        content.appendChild(aiChat);
        
        const aiReply = document.createElement('div');
        aiReply.className = 'ai-reply';
        aiReply.textContent = `川小农回复: ${message.ai_reply}`;
        content.appendChild(aiReply);
    }
    
    div.appendChild(content);
    
    // 添加消息时间
    const time = document.createElement('div');
    time.className = 'message-time';
    time.textContent = message.timestamp || formatTime();
    div.appendChild(time);
    
    return div;
}

// 创建系统消息元素
function createSystemMessageElement(text) {
    const div = document.createElement('div');
    div.className = 'message system';
    const content = document.createElement('div');
    content.className = 'message-content';
    content.textContent = text;
    div.appendChild(content);
    return div;
}

// 添加消息到聊天区域
function addMessage(message) {
    const chatMessages = document.getElementById('chat-messages');
    const messageElement = createMessageElement(message);
    chatMessages.appendChild(messageElement);
    // 滚动到底部
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 添加系统消息
function addSystemMessage(text) {
    const chatMessages = document.getElementById('chat-messages');
    const messageElement = createSystemMessageElement(text);
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 更新用户列表
function updateUserList(users) {
    const userList = document.getElementById('user-list');
    const userCount = document.getElementById('user-count');
    
    userList.innerHTML = '';
    userCount.textContent = users.length;
    
    users.forEach(user => {
        const li = document.createElement('li');
        li.className = 'user-item';
        li.textContent = user;
        userList.appendChild(li);
    });
}

// 发送消息
function sendMessage() {
    const chatInput = document.getElementById('chat-input');
    const message = chatInput.value.trim();
    
    if (!message) return;
    
    const messageData = {
        message: message,
        timestamp: formatTime()
    };
    
    // 通过WebSocket发送消息
    socket.emit('send_message', messageData);
    
    // 清空输入框
    chatInput.value = '';
    chatInput.style.height = 'auto';
}

// 处理退出登录
function handleLogout() {
    if (socket && socket.connected) {
        socket.emit('leave_room');
        socket.disconnect();
    }
    window.location.href = '/';
}

// 调整文本框高度自适应内容
function adjustTextareaHeight() {
    const chatInput = document.getElementById('chat-input');
    chatInput.style.height = 'auto';
    chatInput.style.height = Math.min(chatInput.scrollHeight, 100) + 'px';
}

// 显示/隐藏表情选择器
function toggleEmojiPicker() {
    const emojiPicker = document.getElementById('emoji-picker');
    emojiPicker.style.display = emojiPicker.style.display === 'none' ? 'block' : 'none';
}

// 初始化WebSocket连接
function initSocket() {
    const socket = io();
    
    // 连接成功
    socket.on('connect', () => {
        console.log('WebSocket连接成功');
        // 加入房间
        socket.emit('join_room', { username: username });
    });
    
    // 连接错误
    socket.on('join_error', (data) => {
        alert(data.message);
        window.location.href = '/';
    });
    
    // 加入成功
    socket.on('join_success', (data) => {
        updateUserList(data.online_users);
        addSystemMessage(`您已成功加入聊天室！`);
    });
    
    // 接收新消息
    socket.on('new_message', (message) => {
        addMessage(message);
    });
    
    // 用户加入
    socket.on('user_joined', (data) => {
        addSystemMessage(`${data.username} 加入了聊天室`);
        // 这里会通过其他方式更新用户列表
    });
    
    // 用户离开
    socket.on('user_left', (data) => {
        addSystemMessage(`${data.username} 离开了聊天室`);
    });
    
    // 更新用户列表
    socket.on('update_users', (data) => {
        updateUserList(data.online_users);
    });
    
    // 连接断开
    socket.on('disconnect', () => {
        console.log('WebSocket连接断开');
    });
    
    return socket;
}

// 设置事件监听
function setupEventListeners() {
    // 发送按钮点击事件
    document.getElementById('send-btn').addEventListener('click', sendMessage);
    
    // 输入框回车发送
    document.getElementById('chat-input').addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // 输入框内容变化时调整高度
    document.getElementById('chat-input').addEventListener('input', adjustTextareaHeight);
    
    // 退出按钮点击事件
    document.getElementById('logout-btn').addEventListener('click', handleLogout);
    
    // 表情按钮点击事件
    document.getElementById('emoji-btn').addEventListener('click', toggleEmojiPicker);
    
    // 表情选择器事件
    const emojiPicker = document.getElementById('emoji-picker');
    emojiPicker.addEventListener('emoji-click', (e) => {
        const chatInput = document.getElementById('chat-input');
        chatInput.value += e.detail.unicode;
        chatInput.focus();
        adjustTextareaHeight();
    });
    
    // 点击页面其他地方关闭表情选择器
    document.addEventListener('click', (e) => {
        const emojiBtn = document.getElementById('emoji-btn');
        if (!emojiBtn.contains(e.target) && !emojiPicker.contains(e.target)) {
            emojiPicker.style.display = 'none';
        }
    });
    
    // 页面关闭前发送离开事件
    window.addEventListener('beforeunload', () => {
        if (socket && socket.connected) {
            socket.emit('leave_room');
        }
    });
}

// 主函数
function initChat() {
    // 获取用户名
    username = getUsername();
    if (!username) {
        window.location.href = '/';
        return;
    }
    
    // 初始化WebSocket
    socket = initSocket();
    
    // 设置事件监听
    setupEventListeners();
    
    // 隐藏表情选择器
    document.getElementById('emoji-picker').style.display = 'none';
}

// 全局变量
let username;
let socket;

// 页面加载完成后初始化
window.addEventListener('DOMContentLoaded', initChat);
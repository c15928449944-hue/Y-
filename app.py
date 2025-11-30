from flask import Flask, render_template, request, jsonify, redirect
from flask_socketio import SocketIO, emit, join_room, leave_room
import eventlet
import json
import os

# 使用eventlet作为异步服务器
eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'daipp_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# 存储在线用户信息
online_users = {}
# 存储房间信息
rooms = {}

# 加载配置文件
def load_config():
    config_path = os.path.join('config', 'config.json')
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'servers': [
            {'name': '默认服务器', 'url': 'http://localhost:5000'}
        ]
    }

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/chat')
def chat():
    username = request.args.get('username')
    if not username:
        return redirect('/')
    return render_template('chat.html', username=username)

@app.route('/api/servers')
def get_servers():
    config = load_config()
    return jsonify(config['servers'])

@app.route('/api/check_username')
def check_username():
    username = request.args.get('username')
    if username in online_users.values():
        return jsonify({'exists': True})
    return jsonify({'exists': False})

@socketio.on('connect')
def handle_connect():
    print('客户端连接:', request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    if sid in online_users:
        username = online_users[sid]
        del online_users[sid]
        # 通知其他用户该用户离开
        emit('user_left', {'username': username}, broadcast=True, include_self=False)
        # 广播更新后的用户列表给所有用户
        emit('update_users', {'online_users': list(online_users.values())}, broadcast=True)
        print(f'{username} 离开了聊天室')

@socketio.on('join_room')
def handle_join_room(data):
    username = data['username']
    sid = request.sid
    
    # 检查用户名是否已存在
    if username in online_users.values():
        emit('join_error', {'message': '用户名已存在'})
        return
    
    # 保存用户信息
    online_users[sid] = username
    
    # 加入默认房间
    join_room('default')
    
    # 通知其他用户有新用户加入
    emit('user_joined', {'username': username}, broadcast=True, include_self=False)
    
    # 向新用户发送成功消息和当前在线用户列表
    emit('join_success', {
        'username': username,
        'online_users': list(online_users.values())
    })
    
    # 广播更新后的用户列表给所有用户
    emit('update_users', {'online_users': list(online_users.values())}, broadcast=True)
    
    print(f'{username} 加入了聊天室')

@socketio.on('send_message')
def handle_send_message(data):
    username = online_users.get(request.sid)
    if not username:
        return
    
    message = data['message']
    timestamp = data.get('timestamp', '')
    
    # 构建消息对象
    message_data = {
        'username': username,
        'message': message,
        'timestamp': timestamp,
        'type': 'normal'
    }
    
    # 检查是否包含@命令
    if message.startswith('@'):
        parts = message.split(' ', 1)
        if len(parts) >= 2:
            command = parts[0].lower()
            content = parts[1]
            
            # 处理@电影命令
            if command == '@电影' and content.startswith(('http://', 'https://')):
                message_data['type'] = 'movie'
                message_data['movie_url'] = content
            # 处理@川小农命令
            elif command == '@川小农':
                message_data['type'] = 'ai_chat'
                message_data['ai_message'] = content
                # 实现简单的AI回复逻辑
                message_data['ai_reply'] = get_ai_reply(content)
    
    # 广播消息给所有用户
    emit('new_message', message_data, broadcast=True)

# 简单的AI回复函数
def get_ai_reply(question):
    # 预定义的问答对
    qa_pairs = {
        '你好': '你好！我是川小农AI助手，很高兴为你服务！',
        '你是谁': '我是川小农AI助手，一个简单但实用的聊天机器人。',
        '天气': '抱歉，我暂时无法获取天气信息，但你可以使用天气预报应用查看。',
        '帮助': '我可以回答简单的问题。你可以问我：你好、你是谁、今天怎么样、再见等。',
        '再见': '再见！希望能再次为你服务！',
        '谢谢': '不客气！有什么问题随时问我。',
        '今天怎么样': '今天是个好日子！希望你也有美好的一天！',
        '你会做什么': '我可以回答简单的问题，陪你聊天。你可以试试问我不同的问题！',
        '时间': '当前时间需要你查看设备时钟，我没有实时时钟功能。',
        '名字': '我的名字是川小农AI助手。',
        # 大学位置查询相关
        '四川大学': '四川大学有多个校区，望江校区位于成都市武侯区一环路南一段24号。',
        '电子科技大学': '电子科技大学有清水河校区（成都市郫都区西源大道2006号）和沙河校区（成都市成华区建设北路二段4号）。',
        '西南交通大学': '西南交通大学犀浦校区位于成都市郫都区犀安路999号。',
        '四川农业大学': '四川农业大学有多个校区，成都校区位于成都市温江区惠民路211号。',
        '成都大学': '成都大学位于成都市龙泉驿区成洛大道2025号。',
        # 大学特色相关
        '四川大学特色': '四川大学是国家"双一流"建设高校，学科门类齐全，尤以医学、文学、历史、数学等学科见长。华西医学中心在国内外享有盛誉。',
        '电子科技大学特色': '电子科技大学是电子信息领域的顶尖高校，被誉为"中国电子类院校的排头兵"，在电子科学与技术、信息与通信工程等学科领域全国领先。',
        '西南交通大学特色': '西南交通大学是中国近代土木工程和交通工程教育的发源地，轨道交通学科全国第一，拥有全国唯一的"轨道交通国家实验室"。',
        '四川农业大学特色': '四川农业大学是一所以生物科技为特色，农业科技为优势的综合性大学，动物营养与饲料科学、作物遗传育种等学科在全国具有重要地位。',
        '成都大学特色': '成都大学以应用型学科为主，在计算机科学与技术、软件工程、食品科学与工程等领域具有特色，与成都市产业发展紧密结合。',
        # 大学特色别称，提高匹配率
        '川大特色': '四川大学是国家"双一流"建设高校，学科门类齐全，尤以医学、文学、历史、数学等学科见长。华西医学中心在国内外享有盛誉。',
        '电子科大特色': '电子科技大学是电子信息领域的顶尖高校，被誉为"中国电子类院校的排头兵"，在电子科学与技术、信息与通信工程等学科领域全国领先。',
        '西南交大特色': '西南交通大学是中国近代土木工程和交通工程教育的发源地，轨道交通学科全国第一，拥有全国唯一的"轨道交通国家实验室"。',
        '川农特色': '四川农业大学是一所以生物科技为特色，农业科技为优势的综合性大学，动物营养与饲料科学、作物遗传育种等学科在全国具有重要地位。',
        # 功能介绍相关
        '你有什么功能': '我可以回答简单的问题，包括：1. 打招呼和聊天 2. 大学位置查询 3. 简单的生活建议 4. 基本的信息咨询',
        '你具有哪些功能': '我可以回答简单的问题，包括：1. 打招呼和聊天 2. 大学位置查询 3. 简单的生活建议 4. 基本的信息咨询',
        '你能做什么': '我可以回答简单的问题，陪你聊天，查询部分大学位置信息，提供一些生活建议。',
        '你会什么': '我会回答问题，陪你聊天，查询部分大学位置信息，提供一些生活建议。',
        # 补充更多常用问题
        '你多大了': '我刚刚被创建，还很年轻！',
        '你喜欢什么': '我喜欢帮助用户解决问题，陪用户聊天！',
        '你住在哪里': '我住在互联网的世界里，可以随时为你服务！',
        '开心': '看到你开心我也很开心！希望你每天都有好心情！',
        '难过': '不要难过，一切都会好起来的！有什么可以帮你的吗？',
        '学习': '学习是一件很重要的事情，加油！相信你一定可以的！',
        '工作': '工作要注意劳逸结合，保持良好的工作状态！',
        # 生活建议相关
        '健康饮食': '健康饮食建议：1. 保持饮食多样化 2. 多吃蔬菜水果 3. 控制油盐糖摄入 4. 规律进餐 5. 适量饮水',
        '运动建议': '运动建议：1. 每周至少150分钟中等强度有氧运动 2. 结合力量训练 3. 选择适合自己的运动方式 4. 循序渐进 5. 坚持最重要',
        '学习方法': '有效学习方法：1. 制定明确计划 2. 番茄工作法（25分钟专注+5分钟休息） 3. 主动回忆比重复阅读更有效 4. 教授他人加深理解 5. 定期复习巩固记忆',
        '时间管理': '时间管理技巧：1. 四象限法则（区分紧急重要事项） 2. 设定优先级 3. 避免拖延 4. 学会说"不" 5. 定期复盘优化',
        '压力管理': '压力管理方法：1. 深呼吸放松 2. 适当运动 3. 保证充足睡眠 4. 培养兴趣爱好 5. 与朋友家人倾诉',
        '睡眠建议': '改善睡眠质量：1. 保持规律作息 2. 睡前避免使用电子设备 3. 创造舒适睡眠环境 4. 避免睡前大量进食和饮水 5. 适当进行放松活动',
        '大学生活': '大学生活建议：1. 积极参加社团活动 2. 建立良好人际关系 3. 平衡学习与社交 4. 提前规划职业发展 5. 珍惜时间全面发展',
        '成都美食': '成都特色美食推荐：1. 火锅（如小龙坎、大龙燚） 2. 串串香 3. 担担面 4. 龙抄手 5. 麻辣兔头 6. 三大炮 7. 钟水饺',
        '校园活动': '校园活动建议：1. 参加学术讲座拓宽视野 2. 加入感兴趣的社团 3. 参与志愿者活动 4. 尝试竞赛项目 5. 组织或参与文体活动',
        '友谊维护': '友谊维护技巧：1. 定期联系 2. 真诚倾听 3. 相互支持 4. 包容理解 5. 记住重要日子',
        '目标设定': '有效目标设定：1. SMART原则（具体、可衡量、可实现、相关性、时限性） 2. 分解大目标为小步骤 3. 定期检查进度 4. 及时调整 5. 庆祝成就'
    }
    
    # 将问题转为小写以提高匹配率
    question_lower = question.lower()
    
    # 遍历问答对，寻找匹配项
    for key, answer in qa_pairs.items():
        if key in question_lower:
            return answer
    
    # 常见问候语匹配
    greetings = ['hi', 'hello', '嗨', '嗨喽', '嗨嗨']
    for greeting in greetings:
        if greeting in question_lower:
            return '你好！我是川小农AI助手，有什么可以帮你的吗？'
    
    # 如果没有匹配的问题，返回默认回复
    return '抱歉，我不太理解这个问题。你可以尝试问我其他问题，或者输入"帮助"查看我能回答的问题类型。'

@socketio.on('leave_room')
def handle_leave_room():
    sid = request.sid
    if sid in online_users:
        username = online_users[sid]
        leave_room('default')
        del online_users[sid]
        emit('user_left', {'username': username}, broadcast=True, include_self=False)
        print(f'{username} 离开了聊天室')

if __name__ == '__main__':
    # 确保配置目录存在
    os.makedirs('config', exist_ok=True)
    # 如果配置文件不存在，创建默认配置
    if not os.path.exists(os.path.join('config', 'config.json')):
        default_config = {
            'servers': [
                {'name': '默认服务器', 'url': 'http://localhost:5000'},
                {'name': '备用服务器1', 'url': 'http://localhost:5001'},
                {'name': '备用服务器2', 'url': 'http://localhost:5002'}
            ]
        }
        with open(os.path.join('config', 'config.json'), 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
    
    print('服务器启动在 http://localhost:5000')
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)

import eventlet
# 首先导入并应用eventlet monkey patch，这必须在导入其他模块之前完成
eventlet.monkey_patch()

from flask import Flask, render_template, request, jsonify, redirect
from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
import json
import os
from datetime import datetime
from flask_socketio import ConnectionRefusedError
import sys
import os
# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from commands.command_manager import CommandManager

# 使用eventlet作为异步服务器
eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'daipp_chat_secret_key'
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")

# 初始化命令管理器
command_manager = CommandManager()

# 当前在线用户，使用字典存储：{session_id: nickname}
active_users = {}
# 用户到会话ID的映射：{nickname: session_id}
nickname_to_session = {}
# 会话ID到房间的映射
room_assignments = {}

# 读取配置文件
def read_config():
    config_path = os.path.join(app.root_path, 'config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"读取配置文件失败: {e}")
        # 返回默认配置
        return {
            "servers": [
                {"name": "默认服务器", "url": "http://localhost:5000"}
            ]
        }

# 首页路由（登录页面）
@app.route('/')
def index():
    return render_template('login.html')

# 配置文件路由
@app.route('/config')
def get_config():
    return jsonify(read_config())

# 聊天页面路由
@app.route('/chat')
def chat():
    nickname = request.args.get('nickname')
    server = request.args.get('server')
    
    if not nickname:
        return redirect('/')
    
    return render_template('chat.html', nickname=nickname, server=server)

# WebSocket事件处理
@socketio.on('connect')
def handle_connect():
    # 获取客户端IP地址
    client_ip = request.remote_addr
    print(f"[DEBUG] 新的WebSocket连接: {client_ip}, sid: {request.sid}")
    print(f"[DEBUG] 连接参数: {request.args}")
    # 可以在这里添加连接验证逻辑

@socketio.on('logout')
def handle_logout():
    """处理用户主动退出"""
    session_id = request.sid
    
    # 查找用户昵称
    nickname = None
    for sid, user in active_users.items():
        if sid == session_id:
            nickname = user
            break
    
    room = room_assignments.get(session_id, 'chat_room')
    
    if nickname:
        # 从所有映射中移除用户
        del active_users[session_id]
        del nickname_to_session[nickname]
        
        # 如果用户在房间中，离开房间
        if session_id in room_assignments:
            leave_room(room)
            del room_assignments[session_id]
        
        # 广播用户离开消息
        emit('user_left', {
            'nickname': nickname,
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'online_count': len(active_users)
        }, broadcast=True)
        
        print(f'用户主动退出: {nickname}, 剩余用户: {len(active_users)}')

@socketio.on('disconnect')
def handle_disconnect():
    """处理连接断开（可能是非正常断开）"""
    print(f"[DEBUG] 用户断开连接: {request.sid}")
    session_id = request.sid
    
    # 查找用户昵称
    nickname = None
    for sid, user in active_users.items():
        if sid == session_id:
            nickname = user
            break
    
    if nickname:
        # 检查用户数据是否已被清理（通过logout事件）
        if session_id in active_users:
            # 从所有映射中移除用户
            del active_users[session_id]
            del nickname_to_session[nickname]
            
            # 如果用户在房间中，离开房间
            if session_id in room_assignments:
                room = room_assignments[session_id]
                leave_room(room)
                del room_assignments[session_id]
            
            print(f"[DEBUG] 用户 {nickname} 已从活跃用户列表中移除，当前在线人数: {len(active_users)}")
            print(f"[DEBUG] 更新后活跃用户列表: {active_users}")
            
            # 广播用户离开消息
            broadcast_data = {
                'nickname': nickname,
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'online_count': len(active_users)
            }
            print(f"[DEBUG] 准备广播user_left事件: {broadcast_data}")
            emit('user_left', broadcast_data, broadcast=True)
            print(f"[DEBUG] 已广播user_left事件")
            
            print(f"[DEBUG] 用户断开连接: {nickname}, 剩余用户: {len(active_users)}")
    else:
        print(f"[DEBUG] 未知用户断开连接")

@socketio.on('join')
def handle_join(data):
    print(f"[DEBUG] 接收到join请求: {data}, sid: {request.sid}")
    nickname = data.get('nickname')
    session_id = request.sid
    
    if not nickname:
        print(f"[DEBUG] join失败: 昵称不能为空")
        emit('error', {'message': '昵称不能为空'})
        return
    
    # 验证昵称格式
    if not nickname.strip() or len(nickname) > 20:
        print(f"[DEBUG] join失败: 昵称格式错误")
        emit('error', {'message': '昵称长度不能超过20个字符'})
        return
    
    # 检查昵称是否已存在
    if nickname in nickname_to_session:
        print(f"[DEBUG] join失败: 昵称已存在")
        emit('error', {'message': '昵称已被使用，请选择其他昵称'})
        return
    
    # 添加用户到所有映射中
    active_users[session_id] = nickname
    nickname_to_session[nickname] = session_id
    
    print(f"[DEBUG] 用户映射更新: active_users={active_users}, nickname_to_session={nickname_to_session}")
    print(f"[DEBUG] 用户 {nickname} 已添加到活跃用户列表，当前在线人数: {len(active_users)}")
    
    # 加入聊天室
    room = 'chat_room'
    join_room(room)
    room_assignments[session_id] = room
    
    # 获取在线用户列表
    online_users = list(nickname_to_session.keys())
    print(f"[DEBUG] 在线用户列表: {online_users}")
    
    # 发送成功加入消息，包含当前在线用户列表
    join_response = {
        'nickname': nickname,
        'timestamp': datetime.now().strftime('%H:%M:%S'),
        'online_count': len(active_users),
        'users': online_users
    }
    print(f"[DEBUG] 准备发送join_success给用户 {nickname}: {join_response}")
    emit('join_success', join_response)
    print(f"[DEBUG] 已发送join_success给用户 {nickname}")
    
    # 广播新用户加入消息
    user_joined_data = {
        'nickname': nickname,
        'timestamp': datetime.now().strftime('%H:%M:%S'),
        'online_count': len(active_users)
    }
    print(f"[DEBUG] 准备广播user_joined事件: {user_joined_data}")
    emit('user_joined', user_joined_data, room=room, include_self=False)
    print(f"[DEBUG] 已广播user_joined事件")
    
    print(f"[DEBUG] 用户加入成功: {nickname}, 会话ID: {session_id}, 当前在线: {len(active_users)}")

@socketio.on('send_message')
def handle_message(data):
    print(f"[DEBUG] 接收到send_message请求: {data}, sid: {request.sid}")
    print(f"[DEBUG] 当前活跃用户列表: {active_users}")
    session_id = request.sid
    
    # 验证用户是否已加入
    if session_id not in active_users:
        print(f"[DEBUG] send_message失败: 用户未加入聊天室")
        emit('error', {'message': '请先加入聊天室'})
        return
    
    nickname = active_users[session_id]
    message = data.get('message', '').strip()
    
    print(f"[DEBUG] 用户 {nickname} 发送消息: {message}")
    
    if not message:
        print(f"[DEBUG] send_message失败: 消息为空")
        return
    
    # 消息长度限制
    if len(message) > 500:
        print(f"[DEBUG] 消息过长")
        emit('error', {'message': '消息长度不能超过500个字符'})
        return
    
    # 使用命令管理器处理消息
    user_data = {'nickname': nickname, 'session_id': session_id}
    command_result = command_manager.process_command(message, user_data)
    
    if command_result:
        # 处理命令响应
        if command_result.get('success', True):
            # 根据命令类型进行不同的处理
            if command_result.get('command_name') == '@电影' and 'movie_url' in command_result:
                # 电影命令特殊处理
                message_data = {
                    'nickname': nickname,
                    'message': command_result['message'],
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'is_command': True,
                    'command_type': 'movie',
                    'movie_url': command_result['movie_url']
                }
            elif command_result.get('command_name') == '@川小农' and 'reply' in command_result:
                # 川小农命令特殊处理
                message_data = {
                    'nickname': nickname,
                    'message': command_result['message'],
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'is_command': True,
                    'command_type': 'chuannong',
                    'user_question': command_result.get('user_question', ''),
                    'reply': command_result['reply']
                }
            else:
                # 普通命令处理
                message_data = {
                    'nickname': nickname,
                    'message': command_result['message'],
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'is_command': True
                }
            
            # 广播命令响应到房间
            room = room_assignments.get(session_id, 'chat_room')
            emit('new_message', message_data, room=room)
        else:
            # 命令执行失败，只发送给当前用户
            emit('new_message', {
                'nickname': '系统',
                'message': command_result['message'],
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'is_system': True
            })
    else:
        # 普通聊天消息处理
        message_data = {
            'nickname': nickname,
            'message': message,
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'is_command': False
        }
        
        # 广播消息到房间
        room = room_assignments.get(session_id, 'chat_room')
        print(f"[DEBUG] 准备广播新消息: {message_data}")
        emit('new_message', message_data, room=room)
        print(f"[DEBUG] 已广播新消息，广播给 {len(active_users)} 个用户")
    
    print(f"[DEBUG] 收到消息: {nickname}: {message}")

# 处理命令消息的响应
@socketio.on('command_response')
def handle_command_response(data):
    session_id = request.sid
    
    if session_id not in active_users:
        return
    
    # 添加命令响应的标识和时间戳
    response_data = {
        'message': data.get('message', ''),
        'timestamp': datetime.now().strftime('%H:%M:%S'),
        'is_command': True
    }
    
    # 广播命令响应结果
    room = room_assignments.get(session_id, 'chat_room')
    emit('command_response', response_data, room=room)

# 错误处理
@socketio.on_error_default
def default_error_handler(e):
    print(f'WebSocket错误: {e}')
    # 可以在这里添加更详细的错误处理逻辑

if __name__ == '__main__':
    try:
        # 获取局域网IP地址
        import socket
        def get_local_ip():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(('8.8.8.8', 80))
                ip = s.getsockname()[0]
                s.close()
                return ip
            except:
                return 'localhost'
        
        local_ip = get_local_ip()
        print(f"服务器启动在: http://localhost:5004")
        print(f"局域网地址: http://{local_ip}:5004")
        print(f"[DEBUG] 准备启动Socket.IO服务器，事件处理器已注册")
        
        # 更新配置文件中的局域网服务器地址
        config = read_config()
        updated = False
        for server in config['servers']:
            if server['name'] == '局域网服务器1':
                server['url'] = f"http://{local_ip}:5004"
                updated = True
                break
        
        if updated:
            try:
                with open(os.path.join(app.root_path, 'config.json'), 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=4)
            except Exception as e:
                print(f"更新配置文件失败: {e}")
        
        # 启动Socket.IO服务器
        # 禁用reloader以避免上下文问题
        socketio.run(app, host='0.0.0.0', port=5004, debug=True, use_reloader=False)
    except Exception as e:
        print(f"服务器启动失败: {e}")
        import traceback
        traceback.print_exc()
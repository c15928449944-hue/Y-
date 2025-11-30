import re
from commands.base import CommandHandler

class MovieCommandHandler(CommandHandler):
    """电影命令处理器"""
    
    def get_command_name(self):
        """获取命令名称"""
        return '@电影'
    
    def validate(self, data):
        """验证命令数据"""
        is_valid, error_msg = super().validate(data)
        if not is_valid:
            return is_valid, error_msg
        
        # 验证是否提供了URL
        if not data.get('args'):
            return False, f"用法: {self.command_name} <电影URL>"
        
        # 简单的URL验证
        url = data['args'].strip()
        url_pattern = re.compile(
            r'^(https?://)?'  # 可选的协议
            r'([a-zA-Z0-9.-]+)'  # 域名
            r'(:[0-9]+)?'  # 可选的端口
            r'(/.*)?$'  # 可选的路径
        )
        
        if not url_pattern.match(url):
            return False, "请提供有效的电影URL"
        
        return True, None
    
    def execute(self, data):
        """执行命令"""
        url = data['args'].strip()
        nickname = data['user'].get('nickname', '用户')
        
        # 在实际项目中，这里可以添加更多电影URL处理逻辑
        # 比如解析视频类型、提取缩略图等
        
        # 返回电影播放信息，添加command_type字段以便前端正确识别
        return {
            'message': f'{nickname} 分享了一部电影',
            'movie_url': url,
            'command_name': self.command_name,
            'command_type': 'movie',  # 添加command_type字段
            'nickname': nickname,  # 确保返回发送者昵称
            'user_question': f"{self.command_name} {url}"  # 添加用户原始问题
        }
    
    def format_response(self, message, success=True, **kwargs):
        """格式化响应"""
        response = super().format_response(message, success)
        # 添加电影特定的响应字段
        if success and 'movie_url' in kwargs:
            response['movie_url'] = kwargs['movie_url']
            response['command_type'] = kwargs.get('command_type', 'movie')
            response['nickname'] = kwargs.get('nickname', '')
            response['user_question'] = kwargs.get('user_question', '')
        return response
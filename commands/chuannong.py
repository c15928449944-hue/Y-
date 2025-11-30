from commands.base import CommandHandler
import re

class ChuannongCommandHandler(CommandHandler):
    """川小农命令处理器"""
    
    def __init__(self):
        super().__init__()
        # 简单问答系统的知识库
        self.knowledge_base = {
            # 关于川小农自身能力的问题
            r'.*你(能|会)干什么.*': '我是川小农，一个智能助手！我可以回答简单问题、提供校园信息、帮你查询学校位置等。',
            r'.*你是谁.*': '我是川小农，你的智能聊天助手！',
            r'.*你有什么功能.*': '我可以回答简单的问题，特别是关于校园信息的问题。',
            
            # 学校位置相关问题
            r'.*四川农业大学.*在哪.*': '四川农业大学有三个校区：雅安校区位于四川省雅安市雨城区新康路46号；成都校区位于四川省成都市温江区惠民路211号；都江堰校区位于四川省成都市都江堰市建设路288号。',
            r'.*川农.*在哪.*': '四川农业大学有三个校区：雅安校区位于四川省雅安市雨城区新康路46号；成都校区位于四川省成都市温江区惠民路211号；都江堰校区位于四川省成都市都江堰市建设路288号。',
            r'.*雅安校区.*位置.*': '雅安校区位于四川省雅安市雨城区新康路46号。',
            r'.*成都校区.*位置.*': '成都校区位于四川省成都市温江区惠民路211号。',
            r'.*都江堰校区.*位置.*': '都江堰校区位于四川省成都市都江堰市建设路288号。',
            
            # 其他常见问题
            r'.*你好.*': '你好！很高兴为你服务。',
            r'.*谢谢.*': '不客气！有什么问题随时问我。',
            r'.*再见.*': '再见！祝你有美好的一天！'
        }
    
    def get_command_name(self):
        """获取命令名称"""
        return '@川小农'
    
    def validate(self, data):
        """验证命令数据"""
        is_valid, error_msg = super().validate(data)
        if not is_valid:
            return is_valid, error_msg
        
        # 检查是否提供了提问内容
        if not data.get('args'):
            return False, f"用法: {self.command_name} <你的问题>"
        
        return True, None
    
    def execute(self, data):
        """执行命令"""
        question = data['args'].strip()
        nickname = data['user'].get('nickname', '用户')
        
        # 尝试从知识库中匹配回答
        reply = self._match_answer(question)
        
        # 返回AI回复，包含command_type以便前端正确识别
        return {
            'message': f'{nickname} 向川小农提问：{question}',
            'reply': reply,
            'command_name': self.command_name,
            'user_question': question,
            'command_type': 'chuannong',  # 添加command_type字段
            'nickname': nickname  # 确保返回发送者昵称
        }
    
    def _match_answer(self, question):
        """从知识库中匹配回答"""
        # 遍历知识库，使用正则表达式匹配问题
        for pattern, answer in self.knowledge_base.items():
            if re.search(pattern, question, re.IGNORECASE):
                return answer
        
        # 如果没有匹配到，返回默认回答
        return "抱歉，我现在还不能回答这个问题。如果你有关于学校位置或我的功能的问题，我很乐意为你解答！"
    
    def format_response(self, message, success=True, **kwargs):
        """格式化响应"""
        response = super().format_response(message, success)
        # 添加川小农特定的响应字段
        if success and 'reply' in kwargs:
            response['reply'] = kwargs['reply']
            response['user_question'] = kwargs.get('user_question', '')
            response['command_type'] = kwargs.get('command_type', 'chuannong')
            response['nickname'] = kwargs.get('nickname', '')
        return response
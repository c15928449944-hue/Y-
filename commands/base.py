from abc import ABC, abstractmethod

class CommandHandler(ABC):
    """命令处理器基类"""
    
    def __init__(self):
        self.command_name = self.get_command_name()
    
    @abstractmethod
    def get_command_name(self):
        """获取命令名称，如 '@电影'"""
        pass
    
    @abstractmethod
    def execute(self, data):
        """
        执行命令
        
        Args:
            data: 命令数据，包含用户信息和命令参数
            
        Returns:
            dict: 包含响应消息的字典
        """
        pass
    
    def validate(self, data):
        """
        验证命令数据
        
        Args:
            data: 命令数据
            
        Returns:
            tuple: (是否有效, 错误消息)
        """
        if not data:
            return False, "命令数据为空"
        return True, None
    
    def format_response(self, message, success=True):
        """
        格式化响应消息
        
        Args:
            message: 响应消息内容
            success: 是否成功
            
        Returns:
            dict: 格式化后的响应
        """
        return {
            'message': message,
            'success': success,
            'command_name': self.command_name
        }
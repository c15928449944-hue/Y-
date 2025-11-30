import os
import importlib.util
import sys
import inspect
from commands.base import CommandHandler

class CommandManager:
    """命令管理器"""
    
    def __init__(self):
        self.command_handlers = {}
        self._load_command_handlers()
    
    def _load_command_handlers(self):
        """加载所有命令处理器"""
        # 获取commands目录下的所有Python文件
        import inspect
        import sys
        commands_dir = os.path.dirname(os.path.abspath(__file__))
        for filename in os.listdir(commands_dir):
            if filename.endswith('.py') and filename not in ['__init__.py', 'base.py', 'command_manager.py']:
                module_name = filename[:-3]
                try:
                    # 动态导入模块，使用绝对路径并添加到sys.modules
                    spec = importlib.util.spec_from_file_location(module_name, os.path.join(commands_dir, filename))
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[module_name] = module
                    spec.loader.exec_module(module)
                    
                    # 查找并实例化CommandHandler的子类
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if (issubclass(obj, CommandHandler) and 
                            obj.__name__ != 'CommandHandler' and 
                            obj.__module__ == module_name):
                            handler = obj()
                            self.command_handlers[handler.command_name] = handler
                            print(f"已加载命令处理器: {handler.command_name}")
                except Exception as e:
                    print(f"加载命令处理器 {module_name} 失败: {e}")

    
    def process_command(self, command_text, user_data):
        """
        处理命令
        
        Args:
            command_text: 命令文本，如 '@电影 https://example.com/movie.mp4'
            user_data: 用户数据
            
        Returns:
            dict: 命令执行结果
        """
        if not command_text.startswith('@'):
            return None
        
        # 解析命令名称和参数
        parts = command_text.split(' ', 1)
        command_name = parts[0]
        command_args = parts[1] if len(parts) > 1 else ''
        
        # 检查是否存在对应的命令处理器
        handler = self.command_handlers.get(command_name)
        if not handler:
            return {
                'message': f'未知命令: {command_name}，可用命令: {"、".join(self.command_handlers.keys())}',
                'success': False,
                'is_command': True
            }
        
        # 准备命令数据
        data = {
            'user': user_data,
            'args': command_args,
            'full_text': command_text
        }
        
        # 验证并执行命令
        is_valid, error_msg = handler.validate(data)
        if not is_valid:
            return handler.format_response(error_msg, success=False)
        
        try:
            result = handler.execute(data)
            result['is_command'] = True
            return result
        except Exception as e:
            return handler.format_response(f'执行命令时出错: {str(e)}', success=False)
    
    def get_available_commands(self):
        """
        获取所有可用命令
        
        Returns:
            list: 可用命令列表
        """
        return list(self.command_handlers.keys())
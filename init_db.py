from backend.app import app
from backend.models import init_db

# 初始化数据库
init_db(app)
print("数据库初始化成功！")
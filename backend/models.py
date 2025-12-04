from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# 创建数据库实例
db = SQLAlchemy()


class User(db.Model):
    """用户表模型"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SearchResult(db.Model):
    """搜索结果表模型"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    summary = db.Column(db.Text, nullable=True)
    url = db.Column(db.String(255), nullable=False)
    cover_url = db.Column(db.String(255), nullable=True)
    keyword = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Report(db.Model):
    """报告表模型"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    user = db.relationship('User', backref=db.backref('reports', lazy=True))


def init_db(app):
    """初始化数据库"""
    with app.app_context():
        db.create_all()
        # 创建默认管理员用户
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', password='admin888')
            db.session.add(admin)
            db.session.commit()

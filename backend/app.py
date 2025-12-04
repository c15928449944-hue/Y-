from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from models import db, User, SearchResult, init_db
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 创建Flask应用
app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')

# 配置应用
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database/data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化数据库
db.init_app(app)
init_db(app)


# 登录页面
@app.route('/')
def login():
    return render_template('login.html')

# 注册页面
@app.route('/register')
def register():
    return render_template('register.html')

# 注册验证
@app.route('/register', methods=['POST'])
def register_verify():
    username = request.form['username']
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    
    # 验证密码是否一致
    if password != confirm_password:
        return render_template('register.html', error='两次输入的密码不一致')
    
    # 检查用户名是否已存在
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return render_template('register.html', error='用户名已存在')
    
    try:
        # 创建新用户
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return render_template('register.html', success='注册成功！请登录')
    except Exception as e:
        db.session.rollback()
        return render_template('register.html', error='注册失败：' + str(e))


# 登录验证
@app.route('/login', methods=['POST'])
def login_verify():
    username = request.form['username']
    password = request.form['password']
    
    user = User.query.filter_by(username=username, password=password).first()
    if user:
        session['user_id'] = user.id
        session['username'] = user.username
        return redirect(url_for('dashboard'))
    else:
        return render_template('login.html', error='用户名或密码错误')


# 登出
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


# 后台主页
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'])


# 搜索API
@app.route('/api/search', methods=['POST'])
def search_api():
    if 'user_id' not in session:
        return jsonify({'error': '未登录'}), 401
    
    keyword = request.json.get('keyword')
    if not keyword:
        return jsonify({'error': '请输入关键词'}), 400
    
    try:
        # 导入爬虫模块
        from spider.baidu_spider import baidu_spider
        result = baidu_spider(keyword)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 保存搜索结果到数据库
@app.route('/api/save_results', methods=['POST'])
def save_results_api():
    if 'user_id' not in session:
        return jsonify({'error': '未登录'}), 401
    
    data = request.json.get('data')
    keyword = request.json.get('keyword')
    
    if not data or not keyword:
        return jsonify({'error': '数据或关键词不能为空'}), 400
    
    try:
        # 批量保存数据
        for item in data:
            search_result = SearchResult(
                title=item['title'],
                summary=item['summary'],
                url=item['url'],
                cover_url=item['cover_url'],
                keyword=keyword
            )
            db.session.add(search_result)
        
        db.session.commit()
        return jsonify({'success': True, 'message': '数据保存成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# 获取所有搜索结果
@app.route('/api/search_results', methods=['GET'])
def get_search_results():
    if 'user_id' not in session:
        return jsonify({'error': '未登录'}), 401
    
    try:
        # 获取参数
        keyword = request.args.get('keyword')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # 查询数据
        query = SearchResult.query.order_by(SearchResult.created_at.desc())
        
        if keyword:
            query = query.filter(SearchResult.keyword.like(f'%{keyword}%') | 
                               SearchResult.title.like(f'%{keyword}%') | 
                               SearchResult.summary.like(f'%{keyword}%'))
        
        # 分页
        paginated_results = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # 格式化数据
        results = []
        for item in paginated_results.items:
            results.append({
                'id': item.id,
                'title': item.title,
                'summary': item.summary,
                'url': item.url,
                'cover_url': item.cover_url,
                'keyword': item.keyword,
                'created_at': item.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify({
            'success': True,
            'results': results,
            'total': paginated_results.total,
            'page': page,
            'per_page': per_page,
            'pages': paginated_results.pages
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 数据仓库页面
@app.route('/data_warehouse')
def data_warehouse():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('data_warehouse.html', username=session['username'])


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

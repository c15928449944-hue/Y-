# DaiP智能聊天室

一个基于Python+Flask+WebSocket的局域网多人聊天应用，支持文字消息、emoji表情和@命令功能。

## 功能特性

- 局域网实时聊天
- 用户昵称唯一验证
- 多服务器地址配置
- 支持emoji表情
- @电影命令支持视频分享
- @川小农命令支持AI对话（预留接口）
- 响应式设计，支持移动端

## 技术栈

- 后端：Python 3 + Flask + Flask-SocketIO
- 前端：HTML5 + CSS3 + JavaScript
- WebSocket：实时通信

## 快速开始

### 1. 安装依赖

```bash
# 激活虚拟环境
venv\Scripts\activate  # Windows
# 或
source venv/bin/activate  # Linux/Mac

# 安装依赖包
pip install -r requirements.txt
```

### 2. 配置服务器

编辑 `config/config.json` 文件，可以添加或修改服务器地址：

```json
{
  "servers": [
    {
      "name": "默认服务器",
      "url": "http://localhost:5000"
    },
    {
      "name": "备用服务器1",
      "url": "http://localhost:5001"
    }
  ]
}
```

### 3. 启动服务器

```bash
python app.py
```

服务器将运行在 http://localhost:5000

### 4. 使用方法

1. 打开浏览器，访问 http://localhost:5000
2. 输入昵称，选择服务器，点击登录
3. 在聊天界面可以发送文字消息和emoji表情
4. 使用@电影 URL 可以分享视频
5. 使用@川小农 可以与AI助手对话

## 开发说明

- 项目使用虚拟环境进行开发，请确保在venv中安装依赖
- 前端代码位于 `static/` 目录
- 页面模板位于 `templates/` 目录
- 配置文件位于 `config/` 目录

## 注意事项

- 确保所有用户在同一局域网内
- 昵称必须唯一，不能重复
- 电影播放功能依赖于视频URL的可访问性
- AI对话功能为预留接口，需要后续开发完善

## 许可证

MIT
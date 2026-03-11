#!/usr/bin/env python3
"""
获取微信OpenID的工具脚本
使用说明:
1. 将此脚本部署到公网服务器(或使用ngrok等内网穿透工具)
2. 在微信公众号测试号管理页面配置JS接口安全域名
3. 访问 http://your-server/get_openid
4. 扫码授权后即可获取OpenID
"""

from flask import Flask, request, jsonify, redirect
from config import Config
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <h1>获取微信OpenID</h1>
    <p><a href="/auth">点击此处获取OpenID</a></p>
    '''

@app.route('/auth')
def auth():
    """重定向到微信授权页面"""
    appid = Config.WECHAT_APPID
    redirect_uri = 'http://localhost:5000/callback'
    scope = 'snsapi_userinfo'

    url = f"https://open.weixin.qq.com/connect/oauth2/authorize?appid={appid}&redirect_uri={redirect_uri}&response_type=code&scope={scope}#wechat_redirect"

    return redirect(url)

@app.route('/callback')
def callback():
    """微信回调，获取OpenID"""
    code = request.args.get('code')

    if not code:
        return '授权失败，请重试'

    # 获取access_token
    appid = Config.WECHAT_APPID
    secret = Config.WECHAT_APPSECRET

    token_url = f"https://api.weixin.qq.com/sns/oauth2/access_token?appid={appid}&secret={secret}&code={code}&grant_type=authorization_code"

    response = requests.get(token_url)
    data = response.json()

    if 'openid' in data:
        openid = data['openid']
        return f'''
        <h1>OpenID获取成功！</h1>
        <p><strong>您的OpenID:</strong> {openid}</p>
        <p>请将此OpenID复制到.env文件中的WECHAT_OPENID配置</p>
        '''
    else:
        return f'获取OpenID失败: {data}'

if __name__ == '__main__':
    print("=" * 60)
    print("微信OpenID获取工具")
    print("=" * 60)
    print("\n请按以下步骤操作:")
    print("1. 访问微信公众号测试号管理页面")
    print("2. 在'JS接口安全域名'中填写: http://localhost")
    print("3. 在浏览器中打开: http://localhost:5000")
    print("4. 点击链接，扫码关注测试号")
    print("5. 获取OpenID后，更新.env文件")
    print("\n" + "=" * 60)

    app.run(host='0.0.0.0', port=5000, debug=True)

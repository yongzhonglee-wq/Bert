#!/usr/bin/env python3
"""测试微信模板消息"""
import requests
import json
from config import Config

def test_template():
    # 获取access_token
    token_url = Config.WECHAT_TOKEN_URL
    params = {
        'grant_type': 'client_credential',
        'appid': Config.WECHAT_APPID,
        'secret': Config.WECHAT_APPSECRET
    }

    response = requests.get(token_url, params=params, timeout=10)
    result = response.json()

    if 'access_token' not in result:
        print(f"获取token失败: {result}")
        return

    access_token = result['access_token']
    print(f"获取access_token成功: {access_token}")

    # 测试不同的字段名格式
    test_cases = [
        "keyword3",
        "keyword3: 新闻详情内容",
        "keyword3_新闻详情内容",
    ]

    for field_name in test_cases:
        print(f"\n测试字段名: {field_name}")

        data = {
            "touser": Config.WECHAT_OPENID,
            "template_id": Config.WECHAT_TEMPLATE_ID,
            "data": {
                field_name: {
                    "value": f"测试字段: {field_name}\n这是一条测试消息",
                    "color": "#173177"
                }
            }
        }

        print(f"发送数据: {json.dumps(data, ensure_ascii=False, indent=2)}")

        url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}"
        response = requests.post(
            url,
            data=json.dumps(data, ensure_ascii=False).encode('utf-8'),
            headers={'Content-Type': 'application/json; charset=utf-8'},
            timeout=10
        )

        result = response.json()
        print(f"结果: {result}")

        if result.get('errcode') == 0:
            print(f"✓ 字段 '{field_name}' 测试成功！")
        else:
            print(f"✗ 字段 '{field_name}' 测试失败: {result}")

if __name__ == '__main__':
    test_template()

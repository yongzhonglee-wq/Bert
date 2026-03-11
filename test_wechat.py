#!/usr/bin/env python3
"""测试微信推送功能"""

import sys
from news_fetcher import NewsFetcher
from wechat_notifier import WeChatNotifier
from config import Config
from datetime import datetime

def test_wechat_notification():
    print("=" * 60)
    print("开始测试微信推送功能...")
    print("=" * 60)

    # 1. 获取新闻
    print("\n步骤1: 获取新闻...")
    fetcher = NewsFetcher(Config.NEWS_SOURCES)
    all_news = fetcher.fetch_all_news()

    print(f"获取到新闻:")
    for category, news_list in all_news.items():
        print(f"  {category}: {len(news_list)} 条")

    # 2. 测试获取access_token
    print("\n步骤2: 测试获取微信access_token...")
    try:
        notifier = WeChatNotifier()
        token = notifier.get_access_token()
        print(f"✓ Access Token 获取成功")
        print(f"  Token: {token[:20]}..." if len(token) > 20 else f"  Token: {token}")
    except Exception as e:
        print(f"✗ Access Token 获取失败: {e}")
        return False

    # 3. 测试模板创建
    print("\n步骤3: 测试创建模板消息...")
    try:
        template_id = notifier.create_template()
        print(f"✓ 模板创建成功")
        print(f"  模板ID: {template_id}")
    except Exception as e:
        print(f"✗ 模板创建失败: {e}")
        print("  将使用默认模板")

    # 4. 测试发送消息
    print("\n步骤4: 测试发送新闻推送...")
    try:
        success = notifier.send_news_notification(all_news)
        if success:
            print("✓ 新闻推送成功！请检查您的微信")
        else:
            print("✗ 新闻推送失败")
        return success
    except Exception as e:
        print(f"✗ 新闻推送异常: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    try:
        result = test_wechat_notification()
        print("\n" + "=" * 60)
        if result:
            print("✓ 测试完成！")
        else:
            print("✗ 测试失败")
        print("=" * 60)
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)

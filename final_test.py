#!/usr/bin/env python3
"""完整测试：获取新闻 -> 预览 -> 推送到微信"""

import sys
from news_fetcher import NewsFetcher
from wechat_notifier import WeChatNotifier
from config import Config
from datetime import datetime

def main():
    print("=" * 70)
    print("新闻聚合应用 - 完整测试")
    print("=" * 70)

    # 1. 获取新闻
    print("\n[1/3] 获取新闻...")
    fetcher = NewsFetcher(Config.NEWS_SOURCES)
    all_news = fetcher.fetch_all_news()

    total_news = sum(len(v) for v in all_news.values())
    print(f"✓ 成功获取 {total_news} 条新闻\n")

    # 2. 预览新闻
    print("[2/3] 新闻预览:")
    print("-" * 70)
    for category, news_list in all_news.items():
        if not news_list:
            continue
        print(f"\n【{category}】({len(news_list)}条)")
        for i, news in enumerate(news_list, 1):
            print(f"\n  {i}. {news['title']}")
            print(f"     来源: {news['source']}")
            if news.get('summary'):
                summary = news['summary'][:80] + "..." if len(news['summary']) > 80 else news['summary']
                print(f"     摘要: {summary}")
            print(f"     链接: {news['link']}")
    print("-" * 70)

    # 3. 推送到微信
    print("\n[3/3] 推送到微信...")
    notifier = WeChatNotifier()

    try:
        success = notifier.send_news_notification(all_news)
        if success:
            print("✓ 新闻推送成功！请检查您的微信")
        else:
            print("✗ 新闻推送失败，请检查日志")
    except Exception as e:
        print(f"✗ 推送异常: {e}")
        print("\n提示：")
        print("1. 确保您已关注微信公众号测试号")
        print("2. 确保OpenID配置正确")
        print("3. 测试号客服接口有48小时交互限制，如无法接收请:")
        print("   - 先向测试号发送任意消息")
        print("   - 然后再次运行此脚本")

    print("\n" + "=" * 70)
    print("测试完成")
    print("=" * 70)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)

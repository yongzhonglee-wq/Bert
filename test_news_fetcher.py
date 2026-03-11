#!/usr/bin/env python3
"""测试新闻获取功能"""

import sys
from news_fetcher import NewsFetcher
from config import Config
from datetime import datetime

def test_news_fetch():
    print("=" * 60)
    print("开始测试新闻获取功能...")
    print("=" * 60)

    # 初始化新闻获取器
    fetcher = NewsFetcher(Config.NEWS_SOURCES)

    # 获取所有分类的新闻
    all_news = fetcher.fetch_all_news()

    # 打印结果
    print("\n" + "=" * 60)
    print("新闻获取结果")
    print("=" * 60)

    for category, news_list in all_news.items():
        print(f"\n【{category}】- 共 {len(news_list)} 条新闻\n")
        for i, news in enumerate(news_list, 1):
            print(f"{i}. {news['title']}")
            print(f"   来源: {news['source']}")
            print(f"   链接: {news['link']}")
            print(f"   摘要: {news['summary']}")
            print(f"   时间: {news['published']}")
            print(f"   热度: {news['popularity_score']:.2f}\n")

    print("=" * 60)
    print(f"测试完成！总共获取 {sum(len(v) for v in all_news.values())} 条新闻")
    print("=" * 60)

    return all_news

if __name__ == '__main__':
    try:
        test_news_fetch()
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

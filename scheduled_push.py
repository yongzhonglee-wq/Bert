#!/usr/bin/env python3
"""
定时新闻推送脚本
适合部署到服务器，使用cron定时调用
"""

import sys
import logging
from news_fetcher import NewsFetcher
from wechat_notifier import WeChatNotifier
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """主函数：获取并发送新闻"""
    logger.info("=" * 60)
    logger.info("开始执行新闻推送任务")
    logger.info("=" * 60)

    try:
        # 1. 获取新闻
        logger.info("步骤1: 获取新闻...")
        fetcher = NewsFetcher(Config.NEWS_SOURCES)
        all_news = fetcher.fetch_all_news()

        total_news = sum(len(v) for v in all_news.values())
        logger.info(f"成功获取 {total_news} 条新闻")

        if total_news == 0:
            logger.warning("没有获取到任何新闻，任务结束")
            return

        # 2. 推送到微信
        logger.info("步骤2: 推送到微信...")
        notifier = WeChatNotifier()
        success = notifier.send_news_notification(all_news)

        if success:
            logger.info("✓ 新闻推送成功！")
        else:
            logger.error("✗ 新闻推送失败")

        logger.info("=" * 60)
        logger.info("任务完成")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"任务执行异常: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask配置
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')

    # 微信公众号配置
    WECHAT_APPID = os.getenv('WECHAT_APPID')
    WECHAT_APPSECRET = os.getenv('WECHAT_APPSECRET')
    WECHAT_OPENID = os.getenv('WECHAT_OPENID')
    WECHAT_TEMPLATE_ID = os.getenv('WECHAT_TEMPLATE_ID', '')
    WECHAT_TOKEN_URL = 'https://api.weixin.qq.com/cgi-bin/token'
    WECHAT_TEMPLATE_URL = 'https://api.weixin.qq.com/cgi-bin/message/template/send'

    # 数据库配置
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 5432))
    DB_NAME = os.getenv('DB_NAME', 'news_aggregator')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DATABASE_URL = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

    # Redis配置
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'

    # Celery配置
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL

    # 新闻配置
    NEWS_PER_CATEGORY = int(os.getenv('NEWS_PER_CATEGORY', 5))
    ENABLE_SUMMARY = os.getenv('ENABLE_SUMMARY', 'true').lower() == 'true'
    ENABLE_CLICKABLE_TITLE = os.getenv('ENABLE_CLICKABLE_TITLE', 'false').lower() == 'true'
    ENABLE_MILITARY_NEWS = os.getenv('ENABLE_MILITARY_NEWS', 'false').lower() == 'true'
    ENABLE_SPORTS_NEWS = os.getenv('ENABLE_SPORTS_NEWS', 'false').lower() == 'true'
    ENABLE_WORLD_NEWS = os.getenv('ENABLE_WORLD_NEWS', 'true').lower() == 'true'
    ENABLE_DOMESTIC_NEWS = os.getenv('ENABLE_DOMESTIC_NEWS', 'true').lower() == 'true'
    ENABLE_STOCK_NEWS = os.getenv('ENABLE_STOCK_NEWS', 'true').lower() == 'true'

    # 定时任务配置
    CRON_SCHEDULE = os.getenv('CRON_SCHEDULE', '30 8 * * *')

    # 新闻源配置
    NEWS_SOURCES = {
        'tech': [
            {'url': 'https://www.36kr.com/feed', 'name': '36氪'},
            {'url': 'https://www.ifanr.com/feed', 'name': '爱范儿'},
        ],
        'world': [
            {'url': 'https://news.sina.com.cn/world/', 'name': '新浪国际', 'type': 'web'},
        ],
        'domestic': [
            {'url': 'http://www.people.com.cn/rss/politics.xml', 'name': '人民日报'},
        ],
        'stock': [
            {'url': 'https://finance.sina.com.cn/stock/', 'name': '新浪股市', 'type': 'web'},
        ],
        'military': [
            {'url': 'https://mil.news.sina.com.cn/', 'name': '新浪军事', 'type': 'web'},
        ],
        'sports': [
            {'url': 'https://sports.sina.com.cn/', 'name': '新浪体育', 'type': 'web'},
        ]
    }

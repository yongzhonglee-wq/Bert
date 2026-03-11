import requests
import json
import logging
from typing import Dict, Optional
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WeChatNotifier:
    """微信推送通知类"""

    def __init__(self):
        self.appid = Config.WECHAT_APPID
        self.appsecret = Config.WECHAT_APPSECRET
        self.openid = Config.WECHAT_OPENID
        self.template_id = Config.WECHAT_TEMPLATE_ID
        self.access_token = None

    def get_access_token(self) -> str:
        """获取微信access_token"""
        if self.access_token:
            return self.access_token

        url = Config.WECHAT_TOKEN_URL
        params = {
            'grant_type': 'client_credential',
            'appid': self.appid,
            'secret': self.appsecret
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if 'access_token' in data:
                self.access_token = data['access_token']
                logger.info("获取access_token成功")
                return self.access_token
            else:
                logger.error(f"获取access_token失败: {data}")
                raise Exception(f"获取access_token失败: {data.get('errmsg', '未知错误')}")

        except Exception as e:
            logger.error(f"获取access_token异常: {e}")
            raise

    def send_news_notification(self, all_news: Dict[str, list]) -> bool:
        """发送新闻推送"""
        try:
            # 直接使用客服消息
            success = self.send_composite_news_message(all_news)

            return success

        except Exception as e:
            logger.error(f"发送新闻推送异常: {e}")
            return False

    def send_template_message(self, all_news: Dict[str, list]) -> bool:
        """发送模板消息"""
        # 构建消息内容 - 简化格式
        content = ""
        total_news = 0

        for category, news_list in all_news.items():
            if not news_list:
                continue

            content += f"\n【{category}】\n"

            for i, news in enumerate(news_list, 1):
                title = news.get('title', '').strip()
                # 只显示标题，不显示链接
                content += f"{i}. {title}\n"

            total_news += len(news_list)

        if total_news == 0:
            logger.warning("没有新闻可发送")
            return True

        logger.info(f"模板消息完整内容: {content}")
        logger.info(f"新闻总数: {total_news}, 内容长度: {len(content)}")

        # 模板消息URL
        url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={self.get_access_token()}"

        data = {
            "touser": self.openid,
            "template_id": self.template_id,
            "data": {
                "keyword3: 新闻详情内容": {
                    "value": content,
                    "color": "#173177"
                }
            }
        }

        try:
            response = requests.post(
                url,
                data=json.dumps(data, ensure_ascii=False).encode('utf-8'),
                headers={'Content-Type': 'application/json; charset=utf-8'},
                timeout=10
            )
            response.raise_for_status()
            result = response.json()

            logger.info(f"模板消息发送数据: {data}")
            logger.info(f"模板消息发送结果: {result}")

            if result.get('errcode') == 0:
                logger.info("模板消息推送成功！")
                return True
            else:
                logger.error(f"模板消息推送失败: {result}")
                return False

        except Exception as e:
            logger.error(f"模板消息推送异常: {e}")
            return False

    def send_composite_news_message(self, all_news: Dict[str, list]) -> bool:
        """发送综合新闻消息"""
        # 构建消息内容
        title = "📰 每日新闻推送"
        content = ""

        total_news = 0
        for category, news_list in all_news.items():
            if not news_list:
                continue

            content += f"\n【{category}】\n"

            for i, news in enumerate(news_list, 1):
                title_text = news.get('title', '').strip()
                link = news.get('link', '')

                # 简化格式：标题 + 链接（单独一行）
                content += f"{i}. {title_text}\n"
                if link:
                    content += f"   {link}\n"

            total_news += len(news_list)

        if total_news == 0:
            logger.warning("没有新闻可发送")
            return True

        from datetime import datetime
        from zoneinfo import ZoneInfo
        time = datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M')

        # 使用客服接口发送文本消息
        url = f"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={self.get_access_token()}"

        data = {
            "touser": self.openid,
            "msgtype": "text",
            "text": {
                "content": f"{title}{content}\n\n📅 {time}"
            }
        }

        message_content = f"{title}{content}\n\n📅 {time}"
        logger.info(f"客服消息内容长度: {len(message_content)}")

        try:
            response = requests.post(
                url,
                data=json.dumps(data, ensure_ascii=False).encode('utf-8'),
                headers={'Content-Type': 'application/json; charset=utf-8'},
                timeout=10
            )
            response.raise_for_status()
            result = response.json()

            logger.info(f"客服消息发送结果: {result}")

            if result.get('errcode') == 0:
                logger.info("新闻推送成功！")
                return True
            else:
                logger.error(f"新闻推送失败: {result}")
                return False

        except Exception as e:
            logger.error(f"新闻推送异常: {e}")
            return False

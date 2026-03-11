import requests
import feedparser
import jieba
import jieba.analyse
from datetime import datetime
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NewsFetcher:
    """新闻获取和筛选类"""

    def __init__(self, sources: Dict[str, List[Dict]]):
        self.sources = sources

    def fetch_all_news(self) -> Dict[str, List[Dict]]:
        """获取所有分类的新闻"""
        all_news = {}
        from config import Config

        category_names = {
            'tech': '科技',
            'world': '全球热点',
            'domestic': '国内热点',
            'stock': '股市',
            'military': '军事',
            'sports': '体育'
        }

        for category, source_list in self.sources.items():
            category_name = category_names.get(category, category)

            # 根据配置决定是否获取该类新闻
            if category == 'military' and not Config.ENABLE_MILITARY_NEWS:
                logger.info(f"军事类新闻已禁用，跳过")
                continue
            if category == 'sports' and not Config.ENABLE_SPORTS_NEWS:
                logger.info(f"体育类新闻已禁用，跳过")
                continue
            if category == 'world' and not Config.ENABLE_WORLD_NEWS:
                logger.info(f"全球热点新闻已禁用，跳过")
                continue
            if category == 'domestic' and not Config.ENABLE_DOMESTIC_NEWS:
                logger.info(f"国内热点新闻已禁用，跳过")
                continue
            if category == 'stock' and not Config.ENABLE_STOCK_NEWS:
                logger.info(f"股市新闻已禁用，跳过")
                continue

            logger.info(f"开始获取{category_name}类新闻...")
            news_list = self.fetch_category_news(source_list)
            # 筛选热门高质量新闻
            top_news = self.select_top_news(news_list, top_n=Config.NEWS_PER_CATEGORY)
            if top_news:
                all_news[category_name] = top_news
            logger.info(f"{category_name}类新闻获取完成，共{len(top_news)}条")

        return all_news

    def fetch_category_news(self, source_list: List[Dict]) -> List[Dict]:
        """获取单个分类的新闻"""
        all_news = []
        for source in source_list:
            try:
                # 根据source类型选择获取方式
                if source.get('type') == 'web':
                    news = self.fetch_web_page(source['url'], source['name'])
                else:
                    news = self.fetch_rss_feed(source['url'], source['name'])
                all_news.extend(news)
            except Exception as e:
                logger.error(f"从 {source['name']} 获取新闻失败: {e}")

        return all_news

    def fetch_web_page(self, url: str, source_name: str) -> List[Dict]:
        """从网页获取新闻"""
        logger.info(f"正在从 {source_name} 网页获取新闻...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # 自动检测编码
        if response.encoding == 'ISO-8859-1':
            response.encoding = response.apparent_encoding

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        news_list = []

        # 根据不同的网站使用不同的选择器
        if 'sina' in url and 'sports' in url:
            news_list = self._parse_sina_sports(soup, source_name)
        elif 'sina' in url and 'mil' in url:
            news_list = self._parse_sina_military(soup, source_name)
        elif 'sina' in url and 'world' in url:
            news_list = self._parse_sina_world(soup, source_name)
        elif 'sina' in url and ('roll' in url or 'china' in url):
            news_list = self._parse_sina_china(soup, source_name)
        elif 'sina' in url and 'stock' in url:
            news_list = self._parse_sina_stock(soup, source_name)

        return news_list

    def _parse_sina_world(self, soup, source_name):
        """解析新浪国际页面"""
        news_list = []
        try:
            # 查找所有带href的a标签
            all_links = soup.find_all('a', href=True)

            for link in all_links[:100]:
                title = link.get_text(strip=True)
                href = link.get('href', '')

                # 过滤条件
                if not title or len(title) < 12 or len(title) > 80:
                    continue

                # 过滤掉导航链接
                skip_keywords = ['登录', '注册', '首页', '更多', '查看', '导航', '点击', '新浪', 'SINA', 'English',
                                '产品', '服务', '广告', '合作', '招聘', '法律', '隐私', '联系', '帮助']
                if any(kw in title for kw in skip_keywords):
                    continue

                # 链接必须包含新闻页面的特征
                if 'sina.com.cn' not in href:
                    continue

                # 必须包含年份或日期特征
                if not any(x in href for x in ['/2026/', '/2025/', '/2024/', 'doc-', 'shtml']):
                    continue

                # 完善链接
                if not href.startswith('http'):
                    href = 'https:' + href if href.startswith('//') else 'https://news.sina.com.cn' + href

                news_item = {
                    'title': title,
                    'link': href,
                    'source': source_name,
                    'published': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'summary': '',
                    'popularity_score': self.calculate_popularity_score_from_title(title)
                }
                news_list.append(news_item)
        except Exception as e:
            logger.error(f"解析新浪国际页面失败: {e}")

        return news_list

    def _parse_sina_china(self, soup, source_name):
        """解析新浪国内页面"""
        news_list = []
        try:
            # 查找所有带href的a标签
            all_links = soup.find_all('a', href=True)

            for link in all_links[:200]:
                title = link.get_text(strip=True)
                href = link.get('href', '')

                # 过滤条件
                if not title or len(title) < 10 or len(title) > 80:
                    continue

                # 过滤掉导航链接和非新闻内容
                skip_keywords = ['登录', '注册', '首页', '更多', '查看', '导航', '点击', '新浪', 'SINA', 'English',
                                '产品', '服务', '广告', '合作', '招聘', '法律', '隐私', '联系', '帮助',
                                '图片', '视频', '微博', '博客', '论坛', '评论', '分享', '收藏']
                if any(kw in title for kw in skip_keywords):
                    continue

                # 链接必须包含新闻页面的特征
                if 'sina.com.cn' not in href:
                    continue

                # 必须包含年份或日期特征
                if not any(x in href for x in ['/2026/', '/2025/', '/2024/', 'doc-', 'shtml']):
                    continue

                # 排除finance链接
                if 'finance.sina.com.cn' in href or 'mobile' in href:
                    continue

                # 完善链接
                if not href.startswith('http'):
                    href = 'https:' + href if href.startswith('//') else 'https://news.sina.com.cn' + href

                news_item = {
                    'title': title,
                    'link': href,
                    'source': source_name,
                    'published': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'summary': '',
                    'popularity_score': self.calculate_popularity_score_from_title(title)
                }
                news_list.append(news_item)
        except Exception as e:
            logger.error(f"解析新浪国内页面失败: {e}")

        return news_list

    def _parse_sina_stock(self, soup, source_name):
        """解析新浪股市页面"""
        news_list = []
        try:
            # 查找所有带href的a标签
            all_links = soup.find_all('a', href=True)

            for link in all_links[:200]:
                title = link.get_text(strip=True)
                href = link.get('href', '')

                # 过滤条件
                if not title or len(title) < 10 or len(title) > 80:
                    continue

                # 过滤掉导航链接和非新闻内容
                skip_keywords = ['登录', '注册', '首页', '更多', '查看', '导航', '点击', '新浪', 'SINA', 'English',
                                '产品', '服务', '广告', '合作', '招聘', '法律', '隐私', '联系', '帮助']
                if any(kw in title for kw in skip_keywords):
                    continue

                # 链接必须包含新闻页面的特征
                if 'sina.com.cn' not in href:
                    continue

                # 必须包含年份或日期特征
                if not any(x in href for x in ['/2026/', '/2025/', '/2024/', 'doc-', 'shtml']):
                    continue

                # 完善链接
                if not href.startswith('http'):
                    href = 'https:' + href if href.startswith('//') else 'https://finance.sina.com.cn' + href

                news_item = {
                    'title': title,
                    'link': href,
                    'source': source_name,
                    'published': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'summary': '',
                    'popularity_score': self.calculate_popularity_score_from_title(title)
                }
                news_list.append(news_item)
        except Exception as e:
            logger.error(f"解析新浪股市页面失败: {e}")

        return news_list

    def _parse_sina_sports(self, soup, source_name):
        """解析新浪体育页面"""
        news_list = []
        try:
            # 尝试多种选择器来查找新闻链接
            articles = []

            # 方法1: 查找所有带href的a标签
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                title = link.get_text(strip=True)
                href = link.get('href', '')

                # 过滤: 标题长度合适且链接看起来像新闻
                if (10 <= len(title) <= 100 and
                    ('sports.sina.com.cn' in href or 'sina' in href) and
                    not any(x in title for x in ['登录', '注册', '首页', '更多', '查看'])):
                    articles.append({'title': title, 'link': href})

            # 如果没找到,使用更宽松的条件
            if len(articles) < 5:
                articles = []
                for link in all_links[:50]:
                    title = link.get_text(strip=True)
                    href = link.get('href', '')

                    if (8 <= len(title) <= 80 and
                        not any(x in title for x in ['登录', '注册', '首页', '更多', '查看', '导航'])):
                        articles.append({'title': title, 'link': href})

            # 去重并限制数量
            seen = set()
            for article in articles[:20]:
                if article['title'] not in seen:
                    seen.add(article['title'])
                    link = article['link']
                    if not link.startswith('http'):
                        link = 'https:' + link if link.startswith('//') else 'https://sports.sina.com.cn' + link

                    news_item = {
                        'title': article['title'],
                        'link': link,
                        'source': source_name,
                        'published': datetime.now().strftime('%Y-%m-%d %H:%M'),
                        'summary': self.extract_summary('', article['title']),
                        'popularity_score': self.calculate_popularity_score_from_title(article['title'])
                    }
                    news_list.append(news_item)
        except Exception as e:
            logger.error(f"解析新浪体育页面失败: {e}")

        return news_list

    def _parse_sina_military(self, soup, source_name):
        """解析新浪军事页面"""
        news_list = []
        try:
            # 查找所有带href的a标签
            all_links = soup.find_all('a', href=True)

            for link in all_links[:50]:
                title = link.get_text(strip=True)
                href = link.get('href', '')

                # 过滤标题
                if (8 <= len(title) <= 80 and
                    not any(x in title for x in ['登录', '注册', '首页', '更多', '查看', '导航', '点击'])):

                    # 完善链接
                    if not href.startswith('http'):
                        href = 'https:' + href if href.startswith('//') else 'https://mil.news.sina.com.cn' + href

                    news_item = {
                        'title': title,
                        'link': href,
                        'source': source_name,
                        'published': datetime.now().strftime('%Y-%m-%d %H:%M'),
                        'summary': self.extract_summary('', title),
                        'popularity_score': self.calculate_popularity_score_from_title(title)
                    }
                    news_list.append(news_item)
        except Exception as e:
            logger.error(f"解析新浪军事页面失败: {e}")

        return news_list

    def calculate_popularity_score_from_title(self, title: str) -> float:
        """仅根据标题计算热度分数"""
        score = 0.0
        keywords = jieba.analyse.extract_tags(title, topK=5, withWeight=True)

        for word, weight in keywords:
            score += weight

        # 添加一些随机性
        import random
        score += random.random()

        return score

    def fetch_rss_feed(self, url: str, source_name: str) -> List[Dict]:
        """从RSS源获取新闻"""
        logger.info(f"正在从 {source_name} 获取新闻...")
        feed = feedparser.parse(url)
        news_list = []

        for entry in feed.entries[:20]:  # 只取最新的20条
            try:
                news_item = {
                    'title': entry.title.strip(),
                    'link': entry.link,
                    'source': source_name,
                    'published': self.parse_date(entry.get('published')),
                    'summary': self.extract_summary(entry.get('description', entry.get('summary', '')), entry.title.strip()),
                    'popularity_score': self.calculate_popularity_score(entry)
                }
                news_list.append(news_item)
            except Exception as e:
                logger.error(f"解析新闻项失败: {e}")
                continue

        return news_list

    def parse_date(self, date_str: str) -> str:
        """解析日期"""
        if not date_str:
            return datetime.now().strftime('%Y-%m-%d %H:%M')

        try:
            # feedparser会自动解析日期
            parsed = feedparser.parse(date_str)
            if hasattr(parsed, 'entries') and len(parsed.entries) > 0:
                entry = parsed.entries[0]
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    return datetime(*entry.published_parsed[:6]).strftime('%Y-%m-%d %H:%M')
        except:
            pass

        return datetime.now().strftime('%Y-%m-%d %H:%M')

    def extract_summary(self, description: str, title: str = '') -> str:
        """提取新闻摘要 - 基于关键句提取生成简洁总结"""
        if not description:
            return ""

        # 去除HTML标签
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(description, 'html.parser')
        text = soup.get_text()

        # 清理多余空格和换行
        text = ' '.join(text.split())

        # 如果文本太短,直接返回
        if len(text) <= 100:
            return text

        # 按句子分割
        sentences = []
        for delimiter in ['。', '！', '？', '！', '？', '. ', '! ', '? ']:
            if delimiter in text:
                parts = text.split(delimiter)
                sentences = [s.strip() for s in parts if s.strip()]
                break

        if not sentences:
            sentences = [text]

        # 提取关键句 - 优先选择包含标题关键词的句子
        import jieba
        title_keywords = set(jieba.cut(title)) if title else set()

        scored_sentences = []
        for i, sentence in enumerate(sentences):
            score = 0

            # 句子长度适中(20-80字)得分更高
            length = len(sentence)
            if 20 <= length <= 80:
                score += 2
            elif 80 < length <= 120:
                score += 1

            # 包含标题关键词得分更高
            sentence_words = set(jieba.cut(sentence))
            overlap = len(sentence_words & title_keywords)
            score += overlap * 2

            # 开头和结尾的句子更重要
            if i == 0:
                score += 1
            elif i == len(sentences) - 1:
                score += 0.5

            # 过滤广告和无关内容
            if '欢迎关注' in sentence or '原文链接' in sentence or '微信号' in sentence:
                score -= 10

            scored_sentences.append((score, sentence))

        # 按分数排序,选择前2-3个句子
        scored_sentences.sort(key=lambda x: x[0], reverse=True)
        top_sentences = [s[1] for s in scored_sentences[:2] if s[0] > 0]

        if not top_sentences:
            top_sentences = [sentences[0]]

        # 组合成摘要
        summary = ' '.join(top_sentences)

        # 确保摘要长度在100字以内
        if len(summary) > 100:
            summary = summary[:100] + '...'

        return summary

    def calculate_popularity_score(self, entry) -> float:
        """计算新闻热度分数"""
        score = 0.0

        # 基于标题长度和关键词
        title = entry.title
        keywords = jieba.analyse.extract_tags(title, topK=5, withWeight=True)

        for word, weight in keywords:
            score += weight

        # 基于描述长度
        description = entry.get('description', entry.get('summary', ''))
        if description:
            score += min(len(description) / 100, 2.0)

        # 添加一些随机性模拟热度
        import random
        score += random.random()

        return score

    def select_top_news(self, news_list: List[Dict], top_n: int = 5) -> List[Dict]:
        """筛选热门高质量新闻"""
        if not news_list:
            return []

        # 按热度分数排序
        sorted_news = sorted(news_list, key=lambda x: x['popularity_score'], reverse=True)

        # 去重（基于标题相似度）
        unique_news = []
        seen_titles = set()

        for news in sorted_news:
            # 简单去重：标题太相似的认为是同一新闻
            title_lower = news['title'].lower()
            is_duplicate = False

            for seen_title in seen_titles:
                if self.is_similar_title(title_lower, seen_title):
                    is_duplicate = True
                    break

            if not is_duplicate:
                unique_news.append(news)
                seen_titles.add(title_lower)

            if len(unique_news) >= top_n:
                break

        return unique_news[:top_n]

    def is_similar_title(self, title1: str, title2: str, threshold: float = 0.8) -> bool:
        """判断两个标题是否相似"""
        from difflib import SequenceMatcher

        similarity = SequenceMatcher(None, title1, title2).ratio()
        return similarity > threshold

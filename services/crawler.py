import random
import hashlib
import time
from datetime import datetime, timedelta
from typing import List, Optional
from models.data_models import Account, Article
import config


class CrawlerService:
    def __init__(self, platform: str = "all", use_mock: bool = True):
        self.platform = platform
        self.use_mock = use_mock
        self.fields = config.FIELDS

    def search_accounts_by_keyword(self, keyword: str, limit: int = 20) -> List[Account]:
        if self.use_mock:
            return self._generate_mock_accounts(keyword, limit)
        return self._search_real_accounts(keyword, limit)

    def _generate_mock_accounts(self, keyword: str, limit: int) -> List[Account]:
        accounts = []
        field_count = len(        self.fields)

        for i in range(limit):
            account_id = f"acc_{hashlib.md5(f'{keyword}_{i}_{time.time()}'.encode()).hexdigest()[:8]}"
            account_name = self._generate_account_name(keyword, i)

            articles = self._generate_mock_articles(account_id, account_name,         self.fields[i % field_count])

            account = Account(
                account_id=account_id,
                account_name=account_name,
                account_field=        self.fields[i % field_count],
                articles=articles
            )
            accounts.append(account)

        return accounts

    def _generate_account_name(self, keyword: str, index: int) -> str:
        prefixes = ["", "每日", "最新", "深度", "专业", "独家"]
        suffixes = ["说", "观", "视角", "洞察", "解读", "分析", "聚焦", "观察"]
        templates = [
            "{keyword}{prefix}",
            "{prefix}{keyword}",
            "{keyword}{suffix}",
            "{keyword}研究所",
            "{keyword}研究院",
            "{keyword}频道",
            "{prefix}{keyword}{suffix}"
        ]

        template = random.choice(templates)
        prefix = random.choice(prefixes) if "{prefix}" in template else ""
        suffix = random.choice(suffixes) if "{suffix}" in template else ""

        name = template.format(keyword=keyword, prefix=prefix, suffix=suffix)
        return name if name else f"{keyword}官方"

    def _generate_mock_articles(self, account_id: str, account_name: str, field: str) -> List[Article]:
        articles = []
        base_read = random.randint(5000, 50000)

        for j in range(config.DEFAULT_ARTICLE_COUNT):
            article_id = f"art_{hashlib.md5(f'{account_id}_{j}_{time.time()}'.encode()).hexdigest()[:8]}"

            read_count = base_read + random.randint(-base_read * 3 // 10, base_read * 3 // 10)
            read_count = max(100, read_count)

            like_count = int(read_count * random.uniform(0.01, 0.08))
            comment_count = int(read_count * random.uniform(0.001, 0.02))
            recommend_count = int(read_count * random.uniform(0.1, 0.5))

            days_ago = random.randint(0, 30)
            publish_time = datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23))

            title = self._generate_article_title(field, j)

            article = Article(
                article_id=article_id,
                account_id=account_id,
                account_name=account_name,
                title=title,
                publish_time=publish_time,
                read_count=read_count,
                like_count=like_count,
                comment_count=comment_count,
                recommend_count=recommend_count
            )
            articles.append(article)

        articles.sort(key=lambda x: x.publish_time, reverse=True)
        return articles

    def _generate_article_title(self, field: str, index: int) -> str:
        templates_map = {
            "科技": [
                "{keyword}行业最新趋势揭秘",
                "深度解析{keyword}技术应用",
                "{keyword}如何改变我们的生活",
                "专家解读{keyword}发展前景",
                "关于{keyword}你必须知道的事"
            ],
            "财经": [
                "{keyword}市场分析报告",
                "投资者必看：{keyword}机遇",
                "{keyword}经济影响深度剖析",
                "权威专家谈{keyword}走势",
                "{keyword}投资策略指南"
            ],
            "教育": [
                "{keyword}学习方法大全",
                "家长必读：{keyword}教育",
                "{keyword}培训避坑指南",
                "资深教师推荐{keyword}技巧",
                "{keyword}能力培养之道"
            ],
            "娱乐": [
                "娱乐圈{keyword}最新爆料",
                "明星都在关注的{keyword}",
                "{keyword}圈内幕消息",
                "粉丝必看{keyword}资讯",
                "{keyword}热门话题盘点"
            ],
            "体育": [
                "{keyword}比赛精彩回顾",
                "运动员谈{keyword}训练",
                "{keyword}赛事数据分析",
                "专家预测{keyword}走势",
                "{keyword}热点新闻速递"
            ]
        }

        default_templates = [
            "今日头条：{keyword}最新消息",
            "深度好文：{keyword}全面解读",
            "必读推荐：{keyword}分析报告",
            "热门{keyword}话题讨论",
            "{keyword}相关内容精选"
        ]

        templates = templates_map.get(field, default_templates)
        template = random.choice(templates)
        return template.format(keyword=field)

    def _search_real_accounts(self, keyword: str, limit: int) -> List[Account]:
        raise NotImplementedError("Real crawler not implemented. Use use_mock=True for demo.")


def create_crawler(platform: str = "all", use_mock: bool = True) -> CrawlerService:
    return CrawlerService(platform=platform, use_mock=use_mock)

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class Article:
    article_id: str
    account_id: str
    account_name: str
    title: str
    publish_time: datetime
    read_count: int
    like_count: int
    comment_count: int
    recommend_count: int

    def to_dict(self):
        return {
            "article_id": self.article_id,
            "account_id": self.account_id,
            "account_name": self.account_name,
            "title": self.title,
            "publish_time": self.publish_time.strftime("%Y-%m-%d %H:%M"),
            "read_count": self.read_count,
            "like_count": self.like_count,
            "comment_count": self.comment_count,
            "recommend_count": self.recommend_count
        }


@dataclass
class Account:
    account_id: str
    account_name: str
    account_field: str
    articles: List[Article] = field(default_factory=list)

    avg_read_count: float = 0.0
    avg_like_rate: float = 0.0
    avg_comment_rate: float = 0.0
    article_count: int = 0

    estimated_read: float = 0.0
    estimated_like: float = 0.0
    estimated_comment: float = 0.0
    estimated_recommend: float = 0.0

    price_min: float = 0.0
    price_standard: float = 0.0
    price_max: float = 0.0

    def calculate_stats(self):
        if not self.articles:
            return

        total_read = sum(a.read_count for a in self.articles)
        total_like = sum(a.like_count for a in self.articles)
        total_comment = sum(a.comment_count for a in self.articles)

        self.article_count = len(self.articles)
        self.avg_read_count = total_read / self.article_count
        self.avg_like_rate = total_like / total_read if total_read > 0 else 0
        self.avg_comment_rate = total_comment / total_read if total_read > 0 else 0

    def set_estimates(self, estimated_read, estimated_like, estimated_comment, estimated_recommend):
        self.estimated_read = estimated_read
        self.estimated_like = estimated_like
        self.estimated_comment = estimated_comment
        self.estimated_recommend = estimated_recommend

    def set_prices(self, price_min, price_standard, price_max):
        self.price_min = price_min
        self.price_standard = price_standard
        self.price_max = price_max

    def to_dict(self):
        return {
            "account_id": self.account_id,
            "account_name": self.account_name,
            "account_field": self.account_field,
            "avg_read_count": round(self.avg_read_count, 2),
            "avg_like_rate": round(self.avg_like_rate * 100, 2),
            "avg_comment_rate": round(self.avg_comment_rate * 100, 2),
            "article_count": self.article_count,
            "estimated_read": round(self.estimated_read, 2),
            "price_min": round(self.price_min, 2),
            "price_standard": round(self.price_standard, 2),
            "price_max": round(self.price_max, 2)
        }


@dataclass
class AnalysisResult:
    keyword: str
    accounts: List[Account]
    total_accounts: int
    total_articles: int
    analysis_time: datetime = field(default_factory=datetime.now)

    def to_dataframe_dict(self):
        return [acc.to_dict() for acc in self.accounts]

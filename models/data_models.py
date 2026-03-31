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
    is_headline: bool = True

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
            "recommend_count": self.recommend_count,
            "is_headline": self.is_headline
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
class HeadlineStats:
    account_name: str
    total_reads: int = 0
    avg_reads: float = 0.0
    max_reads: int = 0
    min_reads: int = 0
    article_count: int = 0
    articles: List[Article] = field(default_factory=list)

    def calculate_from_articles(self, articles: List[Article]):
        if not articles:
            return

        self.articles = articles
        self.article_count = len(articles)
        self.total_reads = sum(a.read_count for a in articles)
        self.avg_reads = self.total_reads / self.article_count
        self.max_reads = max(a.read_count for a in articles)
        self.min_reads = min(a.read_count for a in articles)

    def to_dict(self):
        return {
            "account_name": self.account_name,
            "total_reads": self.total_reads,
            "avg_reads": round(self.avg_reads, 2),
            "max_reads": self.max_reads,
            "min_reads": self.min_reads,
            "article_count": self.article_count
        }


@dataclass
class AccountAnalysisResult:
    account_name: str
    stats: HeadlineStats
    analysis_time: datetime = field(default_factory=datetime.now)
    scope_type: str = ""
    scope_value: int = 0

    def to_dict(self):
        return {
            "account_name": self.account_name,
            "stats": self.stats.to_dict(),
            "analysis_time": self.analysis_time.strftime("%Y-%m-%d %H:%M:%S"),
            "scope_type": self.scope_type,
            "scope_value": self.scope_value
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

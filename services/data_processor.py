from typing import List, Tuple, Optional
from datetime import datetime, timedelta
import numpy as np
from models.data_models import Account, Article, HeadlineStats


class DataProcessor:
    @staticmethod
    def remove_outliers(articles: List[Article]) -> List[Article]:
        if not articles:
            return []

        read_counts = [a.read_count for a in articles]
        mean_read = np.mean(read_counts)
        std_read = np.std(read_counts)

        lower_bound = max(100, mean_read * 0.1)
        upper_bound = mean_read * 3 if mean_read > 0 else float('inf')

        filtered = [
            a for a in articles
            if lower_bound <= a.read_count <= upper_bound
        ]

        return filtered if filtered else articles

    @staticmethod
    def calculate_avg_metrics(articles: List[Article]) -> Tuple[float, float, float, float]:
        if not articles:
            return 0.0, 0.0, 0.0, 0.0

        total_read = sum(a.read_count for a in articles)
        total_like = sum(a.like_count for a in articles)
        total_comment = sum(a.comment_count for a in articles)
        total_recommend = sum(a.recommend_count for a in articles)

        count = len(articles)

        avg_read = total_read / count
        avg_like_rate = total_like / total_read if total_read > 0 else 0
        avg_comment_rate = total_comment / total_read if total_read > 0 else 0
        avg_recommend = total_recommend / count

        return avg_read, avg_like_rate, avg_comment_rate, avg_recommend

    @staticmethod
    def process_account(account: Account) -> Account:
        filtered_articles = DataProcessor.remove_outliers(account.articles)

        avg_read, avg_like_rate, avg_comment_rate, avg_recommend = \
            DataProcessor.calculate_avg_metrics(filtered_articles)

        account.articles = filtered_articles
        account.calculate_stats()

        return account

    @staticmethod
    def filter_headline_articles_by_recent(articles: List[Article], count: int = 10) -> List[Article]:
        if not articles:
            return []

        headline_articles = [a for a in articles if a.is_headline]
        headline_articles.sort(key=lambda x: x.publish_time, reverse=True)

        return headline_articles[:count]

    @staticmethod
    def filter_headline_articles_by_year(articles: List[Article], year: int = None) -> List[Article]:
        if not articles:
            return []

        if year is None:
            year = datetime.now().year

        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31, 23, 59, 59)

        headline_articles = [
            a for a in articles
            if a.is_headline and start_date <= a.publish_time <= end_date
        ]

        headline_articles.sort(key=lambda x: x.publish_time, reverse=True)
        return headline_articles

    @staticmethod
    def calculate_headline_stats(articles: List[Article], account_name: str) -> HeadlineStats:
        stats = HeadlineStats(account_name=account_name)
        stats.calculate_from_articles(articles)
        return stats


def create_processor() -> DataProcessor:
    return DataProcessor()

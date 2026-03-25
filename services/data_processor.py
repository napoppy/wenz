from typing import List, Tuple
import numpy as np
from models.data_models import Account, Article


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


def create_processor() -> DataProcessor:
    return DataProcessor()

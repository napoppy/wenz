from typing import Tuple, List
from models.data_models import Account, Article


class Predictor:
    @staticmethod
    def predict_next_article(articles: List[Article]) -> Tuple[float, float, float, float]:
        if not articles:
            return 0.0, 0.0, 0.0, 0.0

        sorted_articles = sorted(articles, key=lambda x: x.publish_time, reverse=True)
        recent_articles = sorted_articles[:10]

        total_read = sum(a.read_count for a in recent_articles)
        total_like = sum(a.like_count for a in recent_articles)
        total_comment = sum(a.comment_count for a in recent_articles)
        total_recommend = sum(a.recommend_count for a in recent_articles)

        count = len(recent_articles)

        est_read = total_read / count
        est_like = total_like / count
        est_comment = total_comment / count
        est_recommend = total_recommend / count

        return est_read, est_like, est_comment, est_recommend

    @staticmethod
    def predict_for_account(account: Account) -> Account:
        est_read, est_like, est_comment, est_recommend = \
            Predictor.predict_next_article(account.articles)

        account.set_estimates(est_read, est_like, est_comment, est_recommend)

        return account


def create_predictor() -> Predictor:
    return Predictor()

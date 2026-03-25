DEFAULT_PRICE_COEFFICIENT = 0.75
MIN_PRICE_COEFFICIENT = 0.5
MAX_PRICE_COEFFICIENT = 1.0

DEFAULT_ARTICLE_COUNT = 10
DEFAULT_CRAWL_LIMIT = 20

PLATFORMS = {
    "wechat": "微信公众号",
    "toutiao": "今日头条",
    "all": "全部平台"
}

FIELDS = [
    "科技", "财经", "教育", "娱乐", "体育",
    "汽车", "房产", "旅游", "美食", "健康",
    "职场", "情感", "军事", "国际", "其他"
]

DATA_DIR = "data"

EXCEL_COLUMNS = [
    "账号ID", "账号名称", "账号领域", "平均阅读量",
    "平均点赞率", "平均评论率", "预估阅读量",
    "最低报价", "标准报价", "最高报价"
]

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

ANTICRAWLER_CONFIG = {
    "use_proxy": False,
    "proxy_list": [],
    "request_delay": 2.0,
    "max_retries": 3,
    "timeout": 30,
    "user_agents": [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    ]
}

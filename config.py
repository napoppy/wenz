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
    "request_delay_min": 2.0,
    "request_delay_max": 5.0,
    "max_retries": 3,
    "timeout": 30,
    "max_articles_per_day": 200,
    "daily_limit_warning": 150,
    "slow_mo": 100,
    "headless": False,
    "user_agents": [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
    ]
}

FONT_DECODER_CONFIG = {
    "cache_dir": "data/font_cache",
    "enable_decode": True,
    "fallback_on_error": True,
}

BEHAVIOR_SIMULATOR_CONFIG = {
    "enable_scroll": True,
    "enable_click": True,
    "enable_mouse_move": True,
    "session_duration_min": 10,
    "session_duration_max": 60,
}

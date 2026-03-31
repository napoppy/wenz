import random
import hashlib
import time
from datetime import datetime, timedelta
from typing import List, Optional
from models.data_models import Account, Article
import config


class CrawlerService:
    def __init__(self, platform: str = "wechat", use_mock: bool = True):
        self.platform = platform
        self.use_mock = use_mock
        self.fields = config.FIELDS

    def search_account_by_name(self, account_name: str) -> Optional[Account]:
        if not account_name or not account_name.strip():
            return None

        account_name = account_name.strip()

        if self.use_mock:
            return self._generate_mock_account(account_name)

        return self._search_real_account(account_name)

    def _generate_mock_account(self, account_name: str) -> Account:
        account_id = f"acc_{hashlib.md5(account_name.encode()).hexdigest()[:12]}"

        field = self.fields[random.randint(0, len(self.fields) - 1)]

        articles = self._generate_mock_headline_articles(account_id, account_name, field)

        account = Account(
            account_id=account_id,
            account_name=account_name,
            account_field=field,
            articles=articles
        )
        account.calculate_stats()

        return account

    def _generate_mock_headline_articles(self, account_id: str, account_name: str, field: str) -> List[Article]:
        articles = []
        base_read = random.randint(8000, 80000)

        for j in range(config.DEFAULT_ARTICLE_COUNT):
            article_id = f"art_{hashlib.md5(f'{account_id}_{j}_{time.time()}'.encode()).hexdigest()[:8]}"

            read_count = base_read + random.randint(-base_read * 4 // 10, base_read * 4 // 10)
            read_count = max(500, read_count)

            like_count = int(read_count * random.uniform(0.015, 0.06))
            comment_count = int(read_count * random.uniform(0.002, 0.015))
            recommend_count = int(read_count * random.uniform(0.1, 0.4))

            days_ago = random.randint(0, 365)
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
                recommend_count=recommend_count,
                is_headline=True
            )
            articles.append(article)

        articles.sort(key=lambda x: x.publish_time, reverse=True)
        return articles

    def _generate_article_title(self, field: str, index: int) -> str:
        templates_map = {
            "科技": [
                "深度解析：行业最新技术趋势",
                "专家解读：技术发展新方向",
                "全面分析：市场技术格局",
                "独家观察：产业发展洞察",
                "趋势报告：技术前沿动态",
                "深度好文：技术应用实践",
                "行业观察：技术变革分析",
                "权威解读：技术发展路径",
                "前沿资讯：技术创新动态",
                "实用指南：技术选型建议"
            ],
            "财经": [
                "市场分析：投资机会解读",
                "深度报告：经济形势研判",
                "专家视角：投资策略建议",
                "数据洞察：市场走势分析",
                "权威解读：财经政策分析",
                "投资指南：风险管理建议",
                "市场观察：行业动态追踪",
                "财经解读：经济数据点评",
                "深度剖析：投资逻辑分析",
                "趋势预判：市场前景展望"
            ],
            "教育": [
                "教育方法：学习技巧分享",
                "深度分析：教育政策解读",
                "实用指南：能力培养方法",
                "专家建议：教育规划策略",
                "行业观察：教育发展趋势",
                "经验分享：高效学习方法",
                "教育洞察：改革方向分析",
                "家长必读：教育避坑指南",
                "教师视角：教学经验总结",
                "深度思考：教育本质探讨"
            ],
            "娱乐": [
                "娱乐热点：话题深度解读",
                "明星动态：最新资讯速递",
                "影视推荐：佳作观赏指南",
                "综艺点评：节目特色分析",
                "音乐分享：优质作品推荐",
                "娱乐观察：行业趋势分析",
                "粉丝必看：偶像最新动态",
                "八卦娱乐：圈内幕幕曝光",
                "文化评论：娱乐现象解读",
                "深度影评：影片全方位解析"
            ],
            "体育": [
                "赛事回顾：精彩瞬间集锦",
                "专家点评：比赛数据分析",
                "球员访谈：训练与备赛分享",
                "战术分析：比赛策略解读",
                "体育观察：行业动态追踪",
                "赛季总结：战绩全面盘点",
                "转会新闻：球员流动分析",
                "运动科普：健康知识普及",
                "深度报道：体育事件真相",
                "趋势分析：体育发展展望"
            ],
            "汽车": [
                "新车测评：性能全面解读",
                "行业分析：市场趋势研判",
                "技术解析：发动机性能对比",
                "购车指南：车型推荐分析",
                "用车知识：保养维护技巧",
                "汽车新闻：行业动态速递",
                "对比评测：同级别车型比较",
                "驾驶体验：实测报告分享",
                "行业观察：新能源发展趋势",
                "深度测评：内饰外观详解"
            ],
            "房产": [
                "楼市分析：房价走势研判",
                "购房指南：选房技巧分享",
                "政策解读：房产调控分析",
                "区域分析：置业板块推荐",
                "装修案例：家居设计灵感",
                "租房攻略：注意事项提醒",
                "房产知识：产权问题解析",
                "市场观察：楼盘项目评测",
                "投资建议：房产配置策略",
                "家居风水：布局设计建议"
            ],
            "旅游": [
                "目的地推荐：景点打卡攻略",
                "旅行体验：游玩心得分享",
                "美食探索：地方特色风味",
                "旅游攻略：出行规划指南",
                "酒店测评：住宿体验报告",
                "小众景点：冷门目的地推荐",
                "旅行摄影：拍摄技巧分享",
                "自驾攻略：路线规划建议",
                "出境游：签证攻略大全",
                "季节推荐：应季旅行目的地"
            ],
            "美食": [
                "食谱分享：家常菜做法教程",
                "餐厅推荐：美味探店指南",
                "美食测评：网红食品体验",
                "烹饪技巧：厨艺提升方法",
                "食材知识：选购储存指南",
                "地方美食：特色小吃推荐",
                "健康饮食：营养搭配建议",
                "烘焙教程：甜品制作指南",
                "美食文化：饮食历史渊源",
                "网红店打卡：排队美食测评"
            ],
            "健康": [
                "养生指南：健康生活习惯",
                "疾病预防：健康知识科普",
                "运动健身：锻炼方法指导",
                "营养饮食：膳食搭配建议",
                "心理健康：情绪管理技巧",
                "医疗科普：疾病知识解析",
                "健康监测：体检指标解读",
                "中医养生：传统保健方法",
                "减肥瘦身：科学减重指南",
                "睡眠改善：优质睡眠建议"
            ],
            "职场": [
                "职场技能：工作效率提升",
                "求职指南：简历面试技巧",
                "职业规划：发展路径建议",
                "沟通技巧：职场人际交往",
                "领导力：管理能力培养",
                "职场心理：压力情绪调节",
                "薪资谈判：薪酬待遇技巧",
                "远程办公：居家工作指南",
                "职场观察：行业趋势分析",
                "技能提升：职业发展建议"
            ],
            "情感": [
                "情感解读：两性关系分析",
                "恋爱技巧：感情升温方法",
                "婚姻经营：家庭和睦之道",
                "心理分析：情感问题解答",
                "成长感悟：人生思考分享",
                "友情维系：朋友相处之道",
                "自我提升：内心成长指南",
                "情感治愈：心灵疗愈方法",
                "脱单攻略：遇见缘分建议",
                "分手疗愈：走出情感困境"
            ],
            "军事": [
                "军事分析：武器装备解读",
                "国际形势：地缘政治分析",
                "防务观察：军事动态追踪",
                "历史战役：经典战例分析",
                "军事科技：前沿技术发展",
                "战略解读：军事思想研究",
                "军工产业：国防工业分析",
                "军事演习：训练情况报道",
                "国际关系：军事合作分析",
                "武器对比：装备性能评测"
            ],
            "国际": [
                "国际新闻：全球大事解读",
                "外交观察：国际关系分析",
                "世界经济：全球经济动态",
                "文化交流：国际文化比较",
                "国际调查：深度报道分析",
                "海外观察：驻外见闻分享",
                "国际评论：热点事件点评",
                "全球趋势：世界发展展望",
                "国际人物：重要人物专访",
                "跨国企业：国际化经营分析"
            ],
            "其他": [
                "热点分析：话题深度解读",
                "实用资讯：生活技巧分享",
                "行业观察：领域动态追踪",
                "趋势报告：发展前景分析",
                "数据洞察：统计分析解读",
                "案例分享：实践经验总结",
                "观点评论：独特视角分析",
                "综合报告：全方位解读",
                "热点追踪：最新动态速递",
                "深度思考：现象本质探讨"
            ]
        }

        default_templates = [
            "深度好文：全方位解读分析",
            "热点追踪：最新消息汇总",
            "实用指南：操作技巧分享",
            "专家观点：专业深度分析",
            "趋势观察：发展前景预判",
            "全面盘点：内容总结梳理",
            "独家报道：内幕消息揭秘",
            "热门话题：讨论度最高内容",
            "值得一看：精选内容推荐",
            "深度思考：现象分析解读"
        ]

        templates = templates_map.get(field, default_templates)
        return templates[index % len(templates)]

    def _search_real_account(self, account_name: str) -> Optional[Account]:
        raise NotImplementedError("Real crawler not implemented. Use use_mock=True for demo.")


def create_crawler(platform: str = "wechat", use_mock: bool = True) -> CrawlerService:
    return CrawlerService(platform=platform, use_mock=use_mock)

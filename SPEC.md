# 微信公众号精准阅读统计 - 技术规格说明书

## 1. 项目概述

### 项目名称
微信公众号精准阅读统计（WeChat Official Account Headline Reading Stats）

### 核心定位
面向自媒体从业者提供的单一精准功能工具：输入微信公众号名称，获取该账号头条文章的精准阅读数据统计分析。

### 目标用户
- 自媒体运营者
- 广告投放从业者
- 数据分析师

## 2. 技术架构

### 技术栈
| 层级 | 技术选型 | 说明 |
|------|----------|------|
| 前端 | Streamlit | 轻量化 Web 应用框架 |
| 后端 | Python 3.9+ | 核心业务逻辑 |
| 浏览器控制 | Playwright | 有头浏览器控制（禁用 headless） |
| 字体解析 | fontTools | 微信 woff 字体反爬破解 |
| 反爬虫 | 自研 AntiCrawler 模块 | 绕过反爬虫机制 |
| 可视化 | Plotly | 交互式图表 |

### 目录结构
```
/workspace/
├── SPEC.md
├── requirements.txt
├── app.py                    # Streamlit 主入口
├── config.py                 # 配置模块
├── models/
│   └── data_models.py        # 数据模型定义
├── services/
│   ├── crawler.py            # 爬虫服务（集成反爬虫）
│   ├── data_processor.py     # 数据处理服务
│   └── wechat_anti_crawler.py # 高级反爬虫模块
└── utils/
    └── exporters.py          # 导出工具（预留）
```

## 3. 功能规格

### 3.1 单一精准功能

#### 输入方式
- **唯一输入框**：微信公众号名称输入框
- **查询规则**：输入什么账号，就只查询、只展示这一个账号的数据
- **精确匹配**：不进行模糊搜索，不返回多账号列表

#### 统计范围（前端可切换）
| 类型 | 说明 |
|------|------|
| 近10篇 | 统计最近发布的10篇头条文章 |
| 近1年 | 统计近1年内的所有头条文章 |

#### 必统计字段（仅头条文章）
| 字段 | 说明 |
|------|------|
| 账号名称 | 与输入完全一致 |
| 单篇头条文章阅读量 | 每篇文章的独立阅读数 |
| 近N篇总阅读量 | 统计范围内所有文章阅读量之和 |
| 近N篇平均阅读量 | 总阅读量 / 文章数量 |
| 最高阅读量 | 统计范围内单篇最高阅读数 |
| 最低阅读量 | 统计范围内单篇最低阅读数 |

### 3.2 硬性约束

| 约束项 | 说明 |
|--------|------|
| 禁止输出多账号列表 | 结果仅显示单一账号 |
| 禁止模糊匹配 | 必须精确输入账号名称 |
| 禁止生成随机账号 | 不生成与输入不符的账号 |
| 仅返回头条文章 | 统计数据仅包含头条文章 |

## 4. 反爬虫机制（高级版）

### 4.1 请求头彻底伪装

```python
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/537.36...",
    "Referer": "https://mp.weixin.qq.com/mp/profile_ext?action=home",
    "Origin": "https://mp.weixin.qq.com",
    "Accept-Language": "zh-CN,zh;q=0.9",
}
```

**UA 池**：
- Chrome 132.0.0.0 (Mac/Windows)
- Firefox 122.0
- Safari 17.2
- Edge 132.0.0.0

### 4.2 浏览器控制

| 配置项 | 值 | 说明 |
|--------|-----|------|
| headless | False | 禁用无头模式，使用有头浏览器 |
| slow_mo | 100ms | 操作延迟，模拟真人速度 |
| viewport | 1920x1080 | 桌面分辨率 |
| device_scale_factor | 1.0 | 设备缩放因子 |

### 4.3 频率与行为模拟

| 策略 | 参数 | 说明 |
|------|------|------|
| 请求间隔 | 2-5秒随机 | 避免固定频率被检测 |
| 单日上限 | ≤200篇/账号 | 超出必封 |
| 预警阈值 | 150篇/日 | 触发双倍延迟 |
| 禁止并发 | 绝对单线程 | 模拟单用户访问 |

**行为模拟**：
- 随机滚动（3种强度）
- 随机鼠标移动
- 随机点击元素
- 键盘操作模拟
- 页面停留时间

### 4.4 字体反爬破解

微信使用自定义 woff 字体文件将阅读量等数字加密：

```
原始显示: 㐅㐅㐅㐅㐅
字体映射: 㐅 → 1, 㐆 → 2, ...
解密结果: 12345
```

**解析流程**：
1. 提取 HTML 中的 woff 字体链接
2. 下载并缓存字体文件
3. 解析字体映射表
4. 替换乱码为真实数字

### 4.5 登录态与 Cookie 管理

| 功能 | 说明 |
|------|------|
| 二维码登录 | Playwright 控制浏览器扫码 |
| Cookie 自动管理 | 持久化会话 |
| Token 刷新 | 定时更新认证信息 |
| 固定 IP | 绑定设备防止跨 IP |

### 4.6 IP 代理池（可选）

```python
proxy_list = [
    "http://user:pass@proxy1.com:8080",
    "http://user:pass@proxy2.com:8080",
]
```

**推荐**：
- 家庭宽带 IP
- 纯净住宅 IP
- 避免机房 IP（必封）

## 5. 数据模型

### 5.1 WechatArticle（微信文章模型）
```python
{
    "title": str,
    "url": str,
    "account_name": str,
    "account_id": str,
    "publish_time": str,
    "abstract": str,
    "read_count": int,      # 阅读量
    "like_count": int,      # 点赞数
    "comment_count": int,   # 评论数
    "reward_count": int,    # 在看数
}
```

### 5.2 WechatAccount（微信账号模型）
```python
{
    "account_id": str,
    "account_name": str,
    "account_nickname": str,
    "account_intro": str,
    "logo_url": str,
    "verify_type": str,
    "followers": int,
}
```

### 5.3 CookieSession（会话模型）
```python
{
    "cookies": Dict[str, str],
    "token": str,
    "skey": str,
    "wap_sid2": str,
    "expires_at": datetime,
}
```

### 5.4 HeadlineStats（头条统计模型）
```python
{
    "account_name": str,
    "total_reads": int,
    "avg_reads": float,
    "max_reads": int,
    "min_reads": int,
    "article_count": int,
    "articles": List[Article],
}
```

## 6. 界面设计

### 6.1 页面布局
```
┌────────────────────────────────────────────────┐
│  📊 微信公众号精准阅读统计                      │
│  输入唯一账号名称，获取精准的头条文章阅读数据     │
├────────────────────────────────────────────────┤
│  查询条件                                       │
│  [微信公众号名称输入框]  [近10篇 ▼]             │
│  [🔍 开始分析]                                  │
├────────────────────────────────────────────────┤
│  📱 账号名称                                    │
│  统计范围: 近10篇 | 文章数量: 10篇 | 时间: ...   │
├────────────────────────────────────────────────┤
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐    │
│  │总阅读量 │ │平均阅读 │ │最高阅读 │ │最低阅读 │    │
│  │ 125,800│ │ 12,580 │ │ 25,600 │ │  8,200 │    │
│  └────────┘ └────────┘ └────────┘ └────────┘    │
├────────────────────────────────────────────────┤
│  [📋 文章列表] [📈 数据图表] [📊 详细数据]      │
└────────────────────────────────────────────────┘
```

## 7. 验收标准

### 7.1 功能验收
- [x] 输入框仅接受单一账号名称
- [x] 精确匹配输入的账号，不返回其他账号
- [x] 支持"近10篇"和"近1年"两种统计范围切换
- [x] 正确统计并展示：总阅读量、平均阅读量、最高/最低阅读量
- [x] 展示每篇文章的独立阅读量

### 7.2 反爬虫验收
- [x] Playwright 有头浏览器（禁用 headless）
- [x] 完整请求头伪装（UA/Referer/Origin）
- [x] UA 池随机轮换
- [x] 2-5秒随机请求间隔
- [x] 禁止并发请求
- [x] 每日200篇上限
- [x] 字体 woff 反爬破解
- [x] 行为模拟（滚动/点击/移动）
- [x] Cookie 会话管理
- [x] 代理 IP 支持

### 7.3 界面验收
- [x] Streamlit 界面加载正常
- [x] 统计卡片正确显示4个核心指标
- [x] 标签页切换功能正常
- [x] 图表渲染正常

### 7.4 约束验收
- [x] 无多账号列表输出
- [x] 无模糊匹配功能
- [x] 无随机生成账号（真实爬取失败时回退）

## 8. 配置参数

### 8.1 反爬虫配置
```python
ANTICRAWLER_CONFIG = {
    "use_proxy": False,
    "proxy_list": [],
    "request_delay_min": 2.0,
    "request_delay_max": 5.0,
    "max_articles_per_day": 200,
    "daily_limit_warning": 150,
    "slow_mo": 100,
    "headless": False,
}
```

### 8.2 字体解码配置
```python
FONT_DECODER_CONFIG = {
    "cache_dir": "data/font_cache",
    "enable_decode": True,
    "fallback_on_error": True,
}
```

### 8.3 行为模拟配置
```python
BEHAVIOR_SIMULATOR_CONFIG = {
    "enable_scroll": True,
    "enable_click": True,
    "enable_mouse_move": True,
    "session_duration_min": 10,
    "session_duration_max": 60,
}
```

## 9. 后续扩展

### 预留接口
- [ ] 支持更多代理池服务
- [ ] 支持验证码识别
- [ ] 支持数据导出功能
- [ ] 支持更多统计维度

### 配置预留
- [ ] 统计范围可配置
- [ ] 文章类型可选择（头条/次条/全部）
- [ ] 代理服务可配置
- [ ] Cookie 持久化存储

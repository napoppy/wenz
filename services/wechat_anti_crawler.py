"""
微信公众号高级反爬虫模块
功能：
1. Playwright 有头浏览器（禁用无头模式）
2. 完整请求头伪装 + Cookie 管理
3. 字体反爬破解（woff 解析）
4. 行为模拟（随机延迟、滚动、点击）
5. 自动登录态维护

数据来源：微信公众平台 mp.weixin.qq.com
"""

import random
import time
import re
import os
import json
import hashlib
import base64
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass, field
from urllib.parse import urljoin, quote
from pathlib import Path
import requests

from playwright.sync_api import sync_playwright, Browser, Page, BrowserContext
from fontTools.ttLib import TTFont


@dataclass
class WechatArticle:
    title: str
    url: str
    account_name: str
    account_id: str
    publish_time: str
    abstract: str
    read_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    reward_count: int = 0


@dataclass
class WechatAccount:
    account_id: str
    account_name: str
    account_nickname: str
    account_intro: str
    logo_url: str
    verify_type: str
    followers: int


@dataclass
class CookieSession:
    cookies: Dict[str, str]
    token: str
    skey: str
    wap_sid2: str
    expires_at: datetime


@dataclass
class FontGlyph:
    glyph_id: int
    unicode_char: str
    name: str


class WechatFontDecoder:
    """
    微信字体反爬破解器
    微信使用自定义 woff 字体文件将数字替换为乱码
    本模块解析字体映射，还原真实数据
    """

    BASE_FONTS_DIR = Path("data/fonts")
    FONT_CACHE_DIR = Path("data/font_cache")

    def __init__(self):
        self.BASE_FONTS_DIR.mkdir(parents=True, exist_ok=True)
        self.FONT_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self.font_mappings: Dict[str, Dict[int, str]] = {}
        self.current_font_mapping: Dict[str, str] = {}

    def download_woff(self, woff_url: str, cache_key: str) -> Optional[Path]:
        try:
            local_path = self.FONT_CACHE_DIR / f"{cache_key}.woff"
            if local_path.exists():
                return local_path

            response = requests.get(
                woff_url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
                    "Referer": "https://mp.weixin.qq.com/"
                },
                timeout=30
            )

            if response.status_code == 200:
                with open(local_path, 'wb') as f:
                    f.write(response.content)
                return local_path
        except Exception:
            pass
        return None

    def parse_woff(self, woff_path: Path) -> Dict[int, str]:
        try:
            font = TTFont(woff_path)
            glyph_map = font.getGlyphMap()

            mapping = {}
            for glyph_id, glyph in glyph_map.items():
                if hasattr(glyph, 'unicode'):
                    mapping[glyph_id] = chr(glyph.unicode)
                elif isinstance(glyph_id, int) and glyph_id > 0:
                    try:
                        mapping[glyph_id] = chr(glyph_id)
                    except:
                        pass

            font.close()
            return mapping
        except Exception:
            return {}

    def decode_text(self, encoded_text: str, font_mapping: Dict[int, str]) -> str:
        if not font_mapping:
            return encoded_text

        result = []
        for char in encoded_text:
            code = ord(char)
            if code in font_mapping:
                result.append(font_mapping[code])
            else:
                result.append(char)

        return ''.join(result)

    def extract_woff_from_html(self, html: str) -> Optional[str]:
        woff_patterns = [
            r'url\([\'"]?([^)\'"]+\.woff[^\)]*)[\'"]?\)',
            r'@font-face[^}]+src:\s*url\([\'"]?([^)\'"]+\.woff[^\)]*)[\'"]?\)',
        ]

        for pattern in woff_patterns:
            match = re.search(pattern, html)
            if match:
                return match.group(1)

        return None

    def build_number_mapping(self, woff_path: Path) -> Dict[str, str]:
        try:
            font = TTFont(woff_path)
            glyph_order = font.getGlyphOrder()

            mapping = {}
            for i, glyph_name in enumerate(glyph_order):
                if glyph_name.startswith('glyph'):
                    uni = font.getUnicode(glyph_name)
                    if uni:
                        mapping[chr(uni)] = str((i - 2) % 10)

            font.close()
            return mapping
        except Exception:
            return {}


class WechatBehaviorSimulator:
    """
    行为模拟器
    模拟真人操作轨迹，降低被检测风险
    """

    SCROLL_PATTERNS = [
        (0.1, 0.3, 0.5),
        (0.2, 0.5, 0.8),
        (0.3, 0.4, 0.6),
        (0.5, 0.7, 1.0),
    ]

    CLICK_PROBABILITIES = {
        'link': 0.4,
        'button': 0.3,
        'area': 0.2,
        'other': 0.1
    }

    def __init__(self, page: Page):
        self.page = page
        self.action_count = 0
        self.start_time = time.time()

    def random_scroll(self, intensity: str = 'medium'):
        patterns = {
            'light': [(0.1, 0.2), (0.3, 0.5)],
            'medium': [(0.2, 0.4), (0.5, 0.7)],
            'heavy': [(0.3, 0.5), (0.6, 0.9)]
        }

        ranges = patterns.get(intensity, patterns['medium'])

        for _ in range(random.randint(1, 3)):
            start = random.uniform(*ranges[0])
            end = random.uniform(*ranges[1])

            self.page.evaluate(f"""
                window.scrollTo(0, document.body.scrollHeight * {start});
            """)

            time.sleep(random.uniform(0.3, 0.8))

            self.page.evaluate(f"""
                window.scrollTo(0, document.body.scrollHeight * {end});
            """)

            time.sleep(random.uniform(0.5, 1.5))

            self.action_count += 1

    def random_mouse_move(self):
        viewport = self.page.viewport_size
        if not viewport:
            return

        start_x = random.randint(100, viewport['width'] - 100)
        start_y = random.randint(100, viewport['height'] - 100)

        self.page.mouse.move(start_x, start_y)

        steps = random.randint(5, 15)
        for _ in range(steps):
            offset_x = random.randint(-50, 50)
            offset_y = random.randint(-30, 30)
            start_x = max(50, min(viewport['width'] - 50, start_x + offset_x))
            start_y = max(50, min(viewport['height'] - 50, start_y + offset_y))

            self.page.mouse.move(start_x, start_y)
            time.sleep(random.uniform(0.05, 0.15))

    def random_click(self):
        elements = self.page.query_selector_all('a, button, [onclick]')

        if elements:
            element = random.choice(elements)
            try:
                box = element.bounding_box()
                if box:
                    x = box['x'] + box['width'] / 2
                    y = box['y'] + box['height'] / 2

                    self.page.mouse.click(x, y)
                    self.action_count += 1

                    time.sleep(random.uniform(0.5, 1.5))

                    self.page.mouse.click(x - 10, y - 10)
            except Exception:
                pass

    def random_keyboard(self):
        keys = ['Tab', 'Enter', 'ArrowDown', 'ArrowUp', 'End', 'Home']
        for _ in range(random.randint(1, 3)):
            key = random.choice(keys)
            self.page.keyboard.press(key)
            time.sleep(random.uniform(0.2, 0.5))

    def stay_on_page(self, min_seconds: float = 2.0, max_seconds: float = 5.0):
        duration = random.uniform(min_seconds, max_seconds)
        time.sleep(duration)

        if random.random() < 0.3:
            self.random_scroll(intensity='light')

    def simulate_session(self, duration_seconds: int = 30):
        end_time = time.time() + duration_seconds

        while time.time() < end_time:
            action = random.choices(
                ['scroll', 'click', 'move', 'keyboard', 'stay'],
                weights=[0.4, 0.2, 0.15, 0.1, 0.15]
            )[0]

            if self.action_count > 20:
                time.sleep(random.uniform(5, 10))
                continue

            if action == 'scroll':
                self.random_scroll(random.choice(['light', 'medium', 'heavy']))
            elif action == 'click':
                self.random_click()
            elif action == 'move':
                self.random_mouse_move()
            elif action == 'keyboard':
                self.random_keyboard()
            else:
                self.stay_on_page()

            time.sleep(random.uniform(1, 3))


class WechatAntiCrawler:
    """
    微信公众号高级反爬虫爬取器

    核心特性：
    1. Playwright 有头浏览器（禁用 headless）
    2. 完整请求头伪装 + Cookie 自动管理
    3. 字体反爬破解
    4. 行为模拟
    5. 自动登录态维护
    """

    USER_AGENTS = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0",
    ]

    BASE_URL = "https://mp.weixin.qq.com"
    SEARCH_URL = "https://weixin.sogou.com/weixin"

    MAX_ARTICLES_PER_DAY = 200
    DAILY_LIMIT_WARNING = 150

    def __init__(
        self,
        use_proxy: bool = False,
        proxy_list: List[str] = None,
        headless: bool = False,
        slow_mo: int = 100,
        user_data_dir: Optional[str] = None
    ):
        self.use_proxy = use_proxy
        self.proxy_list = proxy_list or []
        self.headless = headless
        self.slow_mo = slow_mo
        self.user_data_dir = user_data_dir

        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

        self.font_decoder = WechatFontDecoder()
        self.cookie_session: Optional[CookieSession] = None

        self.daily_article_count = 0
        self.last_request_time = time.time()

        self.request_delay_min = 2.0
        self.request_delay_max = 5.0

    def _get_random_ua(self) -> str:
        return random.choice(self.USER_AGENTS)

    def _get_proxy(self) -> Optional[Dict[str, str]]:
        if self.use_proxy and self.proxy_list:
            proxy = random.choice(self.proxy_list)
            return {"server": proxy}
        return None

    def _get_headers(self) -> Dict[str, str]:
        return {
            "User-Agent": self._get_random_ua(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
            "Referer": "https://mp.weixin.qq.com/mp/profile_ext?action=home",
            "Origin": "https://mp.weixin.qq.com",
        }

    def start_browser(self):
        if self.browser:
            return

        playwright = sync_playwright().start()

        launch_options = {
            "headless": self.headless,
            "slow_mo": self.slow_mo,
        }

        proxy = self._get_proxy()
        if proxy:
            launch_options["proxy"] = proxy

        if self.user_data_dir:
            launch_options["user_data_dir"] = self.user_data_dir

        self.browser = playwright.chromium.launch(**launch_options)

        context_options = {
            "viewport": {"width": 1920, "height": 1080},
            "device_scale_factor": 1.0,
            "is_mobile": False,
            "has_touch": False,
        }

        extra_headers = self._get_headers()
        context_options["extra_http_headers"] = extra_headers

        self.context = self.browser.new_context(**context_options)

        self.page = self.context.new_page()

    def close_browser(self):
        if self.page:
            try:
                self.page.close()
            except:
                pass
            self.page = None

        if self.context:
            try:
                self.context.close()
            except:
                pass
            self.context = None

        if self.browser:
            try:
                self.browser.close()
            except:
                pass
            self.browser = None

    def _random_delay(self):
        delay = random.uniform(self.request_delay_min, self.request_delay_max)

        if self.daily_article_count >= self.DAILY_LIMIT_WARNING:
            delay *= 2

        time.sleep(delay)
        self.last_request_time = time.time()

    def _check_daily_limit(self) -> bool:
        if self.daily_article_count >= self.MAX_ARTICLES_PER_DAY:
            return False
        return True

    def _check_rate_limit(self) -> bool:
        elapsed = time.time() - self.last_request_time
        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)
        return True

    def set_cookies(self, cookies: Dict[str, str]):
        if not self.context:
            return

        for name, value in cookies.items():
            self.context.add_cookies([{
                "name": name,
                "value": value,
                "domain": ".qq.com",
                "path": "/"
            }])

    def get_cookies(self) -> Dict[str, str]:
        if not self.context:
            return {}

        cookies = self.context.cookies()
        return {c["name"]: c["value"] for c in cookies}

    def qrcode_login(self) -> bool:
        """
        二维码登录
        返回 True 表示登录成功
        注意：此方法需要在有头模式下使用
        """
        self.start_browser()

        login_url = f"{self.BASE_URL}/qr_code?appid=wx0d800f5190a08939"

        try:
            self.page.goto(login_url, wait_until="networkidle", timeout=30000)

            qrcode_img = self.page.query_selector('img[class="qrcode"]')
            if qrcode_img:
                qrcode_src = qrcode_img.get_attribute('src')

                qrcode_data = self.page.evaluate('''
                    () => {
                        const img = document.querySelector('img[class="qrcode"]');
                        if (img && img.src) {
                            return img.src;
                        }
                        return null;
                    }
                ''')

                print(f"请扫描二维码登录: {qrcode_data}")

                for _ in range(60):
                    time.sleep(1)

                    is_logged_in = self.page.evaluate('''
                        () => {
                            return document.cookie.includes('wwiet__wwiet__token');
                        }
                    ''')

                    if is_logged_in:
                        print("登录成功")
                        return True

                print("登录超时")
                return False

        except Exception as e:
            print(f"登录失败: {e}")
            return False

        return False

    def check_login_status(self) -> bool:
        """
        检查登录状态
        """
        if not self.page:
            return False

        try:
            self.page.goto(f"{self.BASE_URL}/cgi-bin/home?t=home/index", timeout=10000)
            time.sleep(2)

            title = self.page.title()

            if "profile" in title.lower() or "home" in title.lower():
                return True

            return False

        except Exception:
            return False

    def fetch_article_page(self, url: str) -> Optional[str]:
        """
        获取文章页面 HTML
        """
        if not self._check_daily_limit():
            print(f"已达每日上限 {self.MAX_ARTICLES_PER_DAY} 篇")
            return None

        self._check_rate_limit()
        self._random_delay()

        if not self.browser:
            self.start_browser()

        try:
            self.page.goto(url, wait_until="domcontentloaded", timeout=30000)

            self.page.wait_for_timeout(random.uniform(1000, 2000))

            html = self.page.content()

            self.daily_article_count += 1

            return html

        except Exception as e:
            print(f"获取页面失败: {e}")
            return None

    def parse_article_page(self, html: str, url: str) -> Optional[WechatArticle]:
        """
        解析文章页面，提取关键数据
        """
        try:
            woff_url = self.font_decoder.extract_woff_from_html(html)
            font_mapping = {}

            if woff_url:
                if not woff_url.startswith('http'):
                    woff_url = urljoin(self.BASE_URL, woff_url)

                cache_key = hashlib.md5(woff_url.encode()).hexdigest()[:16]
                woff_path = self.font_decoder.download_woff(woff_url, cache_key)

                if woff_path:
                    font_mapping = self.font_decoder.build_number_mapping(woff_path)

            title_match = re.search(r'<h1[^>]*class="rich_media_title"[^>]*>([^<]+)</h1>', html)
            title = title_match.group(1).strip() if title_match else ""

            account_match = re.search(r'id="js_name"[^>]*>([^<]+)</span>', html)
            account_name = account_match.group(1).strip() if account_match else ""

            account_id_match = re.search(r'var author\s*=\s*["\']([^"\']+)["\']', html)
            account_id = account_id_match.group(1) if account_id_match else ""

            time_match = re.search(r'var publish_time\s*=\s*["\']([^"\']+)["\']', html)
            publish_time = time_match.group(1) if time_match else ""

            read_count_match = re.search(r'var readCount\s*=\s*["\']?(\d+)["\']?', html)
            read_count = int(read_count_match.group(1)) if read_count_match else 0

            like_count_match = re.search(r'var likeCount\s*=\s*["\']?(\d+)["\']?', html)
            like_count = int(like_count_match.group(1)) if like_count_match else 0

            if font_mapping and read_count == 0:
                read_encoded = re.search(r'var readNum\s*=\s*["\']([^"\']+)["\']', html)
                if read_encoded:
                    decoded = self.font_decoder.decode_text(read_encoded.group(1), font_mapping)
                    try:
                        read_count = int(decoded)
                    except:
                        pass

            return WechatArticle(
                title=title,
                url=url,
                account_name=account_name,
                account_id=account_id,
                publish_time=publish_time,
                abstract="",
                read_count=read_count,
                like_count=like_count
            )

        except Exception as e:
            print(f"解析文章失败: {e}")
            return None

    def search_account(self, account_name: str) -> Optional[WechatAccount]:
        """
        搜索微信公众号账号
        """
        if not self.browser:
            self.start_browser()

        encoded_name = quote(account_name)
        search_url = f"{self.SEARCH_URL}?type=1&query={encoded_name}&ie=utf8"

        try:
            self._check_rate_limit()
            self._random_delay()

            self.page.goto(search_url, wait_until="domcontentloaded", timeout=30000)

            self.page.wait_for_selector('.wx-rb', timeout=10000)

            account_elements = self.page.query_selector_all('.wx-rb')

            for element in account_elements:
                name_elem = element.query_selector('.tit')
                if name_elem:
                    name = name_elem.inner_text()

                    if account_name in name or name in account_name:
                        logo_elem = element.query_selector('img')
                        logo = logo_elem.get_attribute('src') if logo_elem else ""

                        verify_elem = element.query_selector('.account_meta')
                        verify = verify_elem.inner_text() if verify_elem else ""

                        return WechatAccount(
                            account_id="",
                            account_name=name,
                            account_nickname=name,
                            account_intro="",
                            logo_url=logo,
                            verify_type=verify,
                            followers=0
                        )

        except Exception as e:
            print(f"搜索账号失败: {e}")

        return None

    def fetch_account_articles(
        self,
        account_name: str,
        limit: int = 10
    ) -> List[WechatArticle]:
        """
        获取账号文章列表
        """
        if not self._check_daily_limit():
            print(f"已达每日上限 {self.MAX_ARTICLES_PER_DAY} 篇")
            return []

        articles = []

        account = self.search_account(account_name)
        if not account:
            print(f"未找到账号: {account_name}")
            return []

        biz_match = re.search(r'biz=([^&]+)', self.page.url)
        biz = biz_match.group(1) if biz_match else ""

        if biz:
            article_list_url = f"{self.BASE_URL}/cgi-bin/appmsg?t=media/appmsg_list_v2&action=list&start=0&count={limit}&appmsgid=&sessionid={int(time.time())}"

            try:
                cookies = self.get_cookies()
                headers = self._get_headers()

                response = requests.post(
                    article_list_url,
                    headers=headers,
                    cookies=cookies,
                    timeout=30
                )

                if response.status_code == 200:
                    data = response.json()

                    if data.get('app_msg_list'):
                        for item in data['app_msg_list']:
                            article = WechatArticle(
                                title=item.get('title', ''),
                                url=item.get('link', ''),
                                account_name=account_name,
                                account_id=biz,
                                publish_time=item.get('digest', ''),
                                abstract=item.get('digest', ''),
                                read_count=item.get('appmsgid', 0)
                            )
                            articles.append(article)

            except Exception as e:
                print(f"获取文章列表失败: {e}")

        if not articles:
            encoded_name = quote(account_name)
            search_url = f"{self.SEARCH_URL}?type=2&query={encoded_name}&ie=utf8"

            try:
                self._check_rate_limit()
                self._random_delay()

                self.page.goto(search_url, wait_until="domcontentloaded", timeout=30000)

                article_links = self.page.query_selector_all('.txt-box h3 a')

                for link_elem in article_links[:limit]:
                    article_url = link_elem.get_attribute('href')

                    if article_url:
                        article_html = self.fetch_article_page(article_url)
                        if article_html:
                            article = self.parse_article_page(article_html, article_url)
                            if article:
                                articles.append(article)

            except Exception as e:
                print(f"搜索文章失败: {e}")

        return articles[:limit]

    def close(self):
        self.close_browser()


def create_wechat_anti_crawler(
    use_proxy: bool = False,
    proxy_list: List[str] = None,
    headless: bool = False,
    slow_mo: int = 100
) -> WechatAntiCrawler:
    return WechatAntiCrawler(
        use_proxy=use_proxy,
        proxy_list=proxy_list,
        headless=headless,
        slow_mo=slow_mo
    )

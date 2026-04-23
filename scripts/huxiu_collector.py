#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
虎嗅AI资讯收集器 - 更新版
"""
import re
import json
import subprocess
import time
import random
from datetime import datetime, timedelta
from bs4 import BeautifulSoup


DEFAULT_URL = "https://www.huxiu.com/ainews/"

# 随机User-Agent池
USER_AGENTS = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
]


def fetch_page(url):
    """使用curl获取网页内容（绕过WAF）"""
    # 随机选择User-Agent
    user_agent = random.choice(USER_AGENTS)
    
    # 随机延时1-3秒
    time.sleep(random.uniform(1, 3))
    
    cmd = [
        'curl', '-s', '-L',
        '-A', user_agent,
        '-H', 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        '-H', 'Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7',
        '-H', 'Accept-Encoding: gzip, deflate, br',
        '-H', 'Referer: https://www.huxiu.com/',
        '-H', 'Sec-Fetch-Dest: document',
        '-H', 'Sec-Fetch-Mode: navigate',
        '-H', 'Sec-Fetch-Site: same-origin',
        '-H', 'Sec-Fetch-User: ?1',
        '-H', 'Upgrade-Insecure-Requests: 1',
        '--compressed',
        url
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return result.stdout


def parse_news_list(html):
    """解析新闻列表 - 新版：直接从HTML提取"""
    news_list = []
    
    # 从 __NUXT_DATA__ 提取JSON数据
    nuxt_match = re.search(r'id="__NUXT_DATA__"[^>]*>([^<]+)<', html)
    if nuxt_match:
        try:
            nuxt_data = json.loads(nuxt_match.group(1))
            # 找到aiNewsList数组
            for item in nuxt_data:
                if isinstance(item, list) and len(item) > 10:
                    # 可能是新闻列表
                    for subitem in item:
                        if isinstance(subitem, dict) and 'ainews_id' in subitem:
                            news_list.append(subitem)
        except:
            pass
    
    # 备用：从HTML直接提取
    if not news_list:
        soup = BeautifulSoup(html, 'html.parser')
        
        # 查找所有新闻卡片
        items = soup.find_all('div', class_='ai-news-item-wrap')
        
        for item in items:
            try:
                # 提取标题
                title_elem = item.find('h3', class_='ai-news-title')
                title = title_elem.get_text(strip=True) if title_elem else ''
                
                # 提取链接
                link = ''
                link_elem = item.find('a', href=True)
                if link_elem:
                    href = link_elem.get('href', '')
                    if href.startswith('/ainews/'):
                        link = f'https://www.huxiu.com{href}'
                
                # 提取时间
                time_elem = item.find('div', class_='bottom-line__time')
                time_ago = time_elem.get_text(strip=True) if time_elem else ''
                
                if title:
                    news_list.append({
                        'title': title,
                        'link': link,
                        'time_ago': time_ago,
                        'source': '虎嗅'
                    })
            except:
                continue
    
    return news_list


def filter_recent_news(news_list, days=2):
    """过滤近N天的新闻"""
    now = datetime.now()
    cutoff = now - timedelta(days=days)
    
    filtered = []
    for news in news_list:
        time_ago = news.get('time_ago', '')
        
        # 解析时间
        hour_match = re.search(r'(\d+)\s*小时', time_ago)
        day_match = re.search(r'(\d+)\s*天', time_ago)
        
        is_recent = True
        if day_match:
            days_ago = int(day_match.group(1))
            is_recent = days_ago <= days
        elif hour_match:
            pass  # 小时前肯定是近期的
        
        if is_recent:
            filtered.append(news)
    
    return filtered


def collect(url=None):
    """主收集函数"""
    if not url:
        url = DEFAULT_URL
    
    print(f"📥 抓取虎嗅AI资讯: {url}")
    
    html = fetch_page(url)
    news_list = parse_news_list(html)
    
    # 过滤近期新闻
    recent_news = filter_recent_news(news_list, days=2)
    
    # 标准化输出
    result = []
    for news in recent_news:
        result.append({
            'title': news.get('title', ''),
            'link': news.get('link', ''),
            'time_ago': news.get('time_ago', ''),
            'source': '虎嗅'
        })
    
    return result


def main():
    import sys
    
    url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
    result = collect(url)
    
    # 输出JSON
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
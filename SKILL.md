---
name: huxiu-collector
description: |
  虎嗅AI资讯数据收集器。抓取虎嗅AI资讯页面的新闻列表，
  返回标准化的JSON数据。
  
  触发场景：
  (1) 需要获取虎嗅AI资讯
  (2) 指定parser为huxiu时调用
---

# 虎嗅AI资讯收集器

## 功能

- 抓取 https://www.huxiu.com/ainews/ 页面的新闻
- 返回标准化JSON格式数据
- 自动过滤近期新闻

## 输出格式

```json
[
  {
    "title": "新闻标题",
    "link": "原文链接",
    "time_ago": "X小时前",
    "source": "虎嗅"
  }
]
```

## 使用方式

```bash
python3 scripts/huxiu_collector.py
# 或指定URL
python3 scripts/huxiu_collector.py https://www.huxiu.com/ainews/
```
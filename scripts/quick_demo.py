#!/usr/bin/env python3
"""
快速日报生成演示 - 每个分类只搜索2个关键词
"""
import os
import sys
import json
import yaml
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.insert(0, str(script_dir))

from searcher import TavilySearcher
from ai_processor import AIProcessor

# 简化的分类配置（每个分类只保留2个查询）
QUICK_CONFIG = {
    "technology": {
        "name": "Technology",
        "name_zh": "技术发布",
        "description": "AI模型、API、开源项目、Agent、Infra",
        "search_queries": [
            "OpenAI GPT-4.1 new model release 2025",
            "Google Gemini AI model update",
        ],
        "days_back": 2
    },
    "product": {
        "name": "Product",
        "name_zh": "产品发布",
        "description": "AI App、工具、浏览器、搜索、Copilot",
        "search_queries": [
            "new AI productivity tool launch 2025",
            "AI browser copilot release",
        ],
        "days_back": 2
    },
    "startup": {
        "name": "Startup",
        "name_zh": "创业融资",
        "description": "AI startup融资、收购、新公司",
        "search_queries": [
            "AI startup funding round 2025",
            "AI company acquisition deal",
        ],
        "days_back": 3
    },
    "bigtech": {
        "name": "BigTech",
        "name_zh": "大厂战略",
        "description": "OpenAI、Google、Apple、Microsoft、Meta、Amazon战略",
        "search_queries": [
            "OpenAI strategy announcement 2025",
            "Google Microsoft AI strategy",
        ],
        "days_back": 2
    },
    "uxtrend": {
        "name": "UX Trend",
        "name_zh": "设计趋势",
        "description": "AI交互方式、Prompt UX、Agent UX、Workflow",
        "search_queries": [
            "AI interaction design pattern UX",
            "Cursor ChatGPT UI UX design",
        ],
        "days_back": 5
    }
}

def collect_data(searcher):
    """收集数据"""
    all_data = {}
    for key, config in QUICK_CONFIG.items():
        print(f"\n{'='*50}")
        print(f"搜索: {config['name_zh']}")
        print(f"{'='*50}")
        
        results = []
        for query in config['search_queries']:
            print(f"\n  查询: {query}")
            try:
                r = searcher.search(
                    query=query,
                    max_results=3,
                    days_back=config['days_back']
                )
                for item in r:
                    item['category'] = config['name']
                results.extend(r)
                print(f"  找到 {len(r)} 条")
            except Exception as e:
                print(f"  错误: {e}")
        
        # 去重
        seen = set()
        unique = []
        for item in results:
            url = item.get('url', '')
            if url and url not in seen:
                seen.add(url)
                unique.append(item)
        
        all_data[key] = unique[:5]  # 每个分类最多5条
        print(f"\n  {config['name_zh']}: 共 {len(all_data[key])} 条")
    
    return all_data

def process_with_ai(processor, all_data):
    """AI处理"""
    processed = {}
    
    for key, items in all_data.items():
        config = QUICK_CONFIG[key]
        print(f"\n{'='*50}")
        print(f"AI处理: {config['name_zh']}")
        print(f"{'='*50}")
        
        processed_items = []
        for i, item in enumerate(items):
            print(f"\n  [{i+1}/{len(items)}] {item.get('title', '')[:40]}...")
            try:
                result = processor.translate_and_summarize(
                    title=item.get('title', ''),
                    content=item.get('content', ''),
                    category=config['name']
                )
                processed_items.append({
                    'title': item.get('title', ''),
                    'title_zh': result['title_zh'],
                    'url': item.get('url', ''),
                    'summary': result['summary'],
                    'problem': result['problem'],
                    'applicable': result['applicable'],
                    'example': result['example'],
                    'category': config['name']
                })
                print(f"       ✓ {result['title_zh'][:40]}...")
            except Exception as e:
                print(f"       ✗ 错误: {e}")
        
        processed[key] = processed_items
    
    return processed

def generate_markdown(processed, date_str):
    """生成Markdown"""
    docs_dir = project_root / "docs"
    daily_dir = docs_dir / "daily"
    daily_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成各分类文件
    for key, items in processed.items():
        config = QUICK_CONFIG[key]
        filename = f"{date_str}-{key}.md"
        filepath = daily_dir / filename
        
        content = f"""---
date: {date_str}
category: {config['name']}
---

# {config['name_zh']} - {date_str}

> {config['description']}

---

"""
        for i, item in enumerate(items, 1):
            content += f"""### {i}. {item['title_zh']}

**原文标题**: [{item['title']}]({item['url']})

**一句话摘要**: {item['summary']}

**能解决什么问题**: {item['problem']}

**产品应用**: {item['applicable']}

**示例场景**: {item['example']}

---

"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  生成: {filepath}")
    
    # 生成汇总文件
    summary_file = docs_dir / f"{date_str}-summary.md"
    summary_content = f"""---
date: {date_str}
type: summary
---

# AI Daily Report - {date_str}

## 📋 今日AI领域动态

"""
    
    for key, items in processed.items():
        config = QUICK_CONFIG[key]
        if not items:
            continue
        
        summary_content += f"""## {config['name_zh']}

> {config['description']}

| # | 标题 | 核心看点 |
|---|------|----------|
"""
        for i, item in enumerate(items[:5], 1):
            title = item['title_zh'][:35] + "..." if len(item['title_zh']) > 35 else item['title_zh']
            summary = item['summary'][:40] + "..." if len(item['summary']) > 40 else item['summary']
            summary_content += f"| {i} | [{title}](./daily/{date_str}-{key}.md) | {summary} |\n"
        
        summary_content += "\n---\n\n"
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary_content)
    print(f"  生成汇总: {summary_file}")

def main():
    print("\n" + "="*60)
    print("AI Daily Report - 快速生成演示")
    print("="*60)
    
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"\n日期: {today}")
    
    # 初始化
    searcher = TavilySearcher()
    processor = AIProcessor()
    
    # 收集数据
    print("\n" + "="*60)
    print("Step 1: 收集数据")
    print("="*60)
    all_data = collect_data(searcher)
    
    total = sum(len(items) for items in all_data.values())
    print(f"\n共收集到 {total} 条原始数据")
    
    # AI处理
    print("\n" + "="*60)
    print("Step 2: AI处理（翻译+摘要）")
    print("="*60)
    processed = process_with_ai(processor, all_data)
    
    # 生成Markdown
    print("\n" + "="*60)
    print("Step 3: 生成Markdown文件")
    print("="*60)
    generate_markdown(processed, today)
    
    print("\n" + "="*60)
    print("✅ 日报生成完成！")
    print("="*60)
    print(f"\n查看文件:")
    print(f"  - docs/{today}-summary.md (日报汇总)")
    print(f"  - docs/daily/{today}-*.md (各分类详情)")

if __name__ == "__main__":
    main()

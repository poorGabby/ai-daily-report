#!/usr/bin/env python3
"""
快速测试脚本 - 只测试Technology分类
"""
import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加脚本目录到路径
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from searcher import TavilySearcher
from ai_processor import AIProcessor

def test_search():
    """测试搜索功能"""
    print("="*60)
    print("测试 Tavily 搜索")
    print("="*60)
    
    searcher = TavilySearcher()
    
    # 只测试一个查询
    query = "OpenAI new model release GPT"
    print(f"\n搜索: {query}")
    
    results = searcher.search(
        query=query,
        max_results=3,
        days_back=1
    )
    
    print(f"找到 {len(results)} 条结果")
    
    for i, r in enumerate(results, 1):
        print(f"\n{i}. {r['title']}")
        print(f"   URL: {r['url']}")
        print(f"   内容: {r['content'][:150]}...")
    
    return results

def test_ai_processing(results):
    """测试AI处理"""
    print("\n" + "="*60)
    print("测试 Kimi AI 处理")
    print("="*60)
    
    if not results:
        print("没有搜索结果，跳过AI处理测试")
        return
    
    processor = AIProcessor()
    
    # 只处理第一条
    item = results[0]
    print(f"\n处理: {item['title'][:50]}...")
    
    result = processor.translate_and_summarize(
        title=item['title'],
        content=item['content'],
        category="Technology"
    )
    
    print(f"\n中文标题: {result['title_zh']}")
    print(f"摘要: {result['summary']}")
    print(f"解决问题: {result['problem']}")
    print(f"产品应用: {result['applicable']}")
    print(f"示例: {result['example']}")
    
    return result

def main():
    try:
        # 测试搜索
        results = test_search()
        
        # 测试AI处理
        if results:
            ai_result = test_ai_processing(results)
        
        print("\n" + "="*60)
        print("测试完成！API正常工作")
        print("="*60)
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

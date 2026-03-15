#!/usr/bin/env python3
"""
Tavily搜索模块 - 使用Tavily API搜索新闻
"""
import os
from typing import List, Dict, Any
from tavily import TavilyClient
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class TavilySearcher:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY is required")
        self.client = TavilyClient(api_key=self.api_key)
    
    def search(
        self,
        query: str,
        max_results: int = 5,
        search_depth: str = "advanced",
        include_domains: List[str] = None,
        days_back: int = 1
    ) -> List[Dict[str, Any]]:
        """
        执行搜索
        
        Args:
            query: 搜索关键词
            max_results: 最大结果数
            search_depth: 搜索深度 (basic/advanced)
            include_domains: 限定域名
            days_back: 搜索最近N天的内容
        """
        try:
            # 构建搜索参数
            search_params = {
                "query": query,
                "max_results": max_results,
                "search_depth": search_depth,
                "include_answer": False,
            }
            
            if include_domains:
                search_params["include_domains"] = include_domains
            
            # 执行搜索
            response = self.client.search(**search_params)
            
            results = []
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            for item in response.get("results", []):
                # 解析发布日期
                published_date = self._parse_date(item.get("published_date", ""))
                
                # 只保留指定时间范围内的结果
                if published_date and published_date < cutoff_date:
                    continue
                
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "content": item.get("content", ""),
                    "published_date": published_date.isoformat() if published_date else None,
                    "score": item.get("score", 0),
                    "source": "tavily"
                })
            
            return results
            
        except Exception as e:
            print(f"Tavily search error for query '{query}': {e}")
            return []
    
    def search_category(
        self,
        category_config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        根据分类配置执行多个搜索
        
        Args:
            category_config: 分类配置字典
        """
        all_results = []
        queries = category_config.get("search_queries", [])
        include_domains = category_config.get("include_domains", [])
        days_back = category_config.get("days_back", 1)
        max_results = category_config.get("max_results_per_query", 5)
        
        print(f"Searching category: {category_config.get('name', 'Unknown')}")
        print(f"Queries: {queries}")
        
        for query in queries:
            print(f"  Query: {query}")
            results = self.search(
                query=query,
                max_results=max_results,
                include_domains=include_domains if include_domains else None,
                days_back=days_back
            )
            
            for result in results:
                result["category"] = category_config.get("name", "")
                result["query"] = query
            
            all_results.extend(results)
            print(f"  Found {len(results)} results")
        
        # 去重（基于URL）
        seen_urls = set()
        unique_results = []
        for result in all_results:
            url = result.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
        
        print(f"Total unique results: {len(unique_results)}")
        return unique_results
    
    def _parse_date(self, date_str: str) -> datetime:
        """解析日期字符串"""
        if not date_str:
            return None
        
        formats = [
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%a, %d %b %Y %H:%M:%S %Z",
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        # 如果无法解析，返回当前时间
        return datetime.now()

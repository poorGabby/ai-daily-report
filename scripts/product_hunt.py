#!/usr/bin/env python3
"""
Product Hunt 数据获取模块
"""
import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any


class ProductHuntClient:
    """Product Hunt API 客户端"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("PRODUCT_HUNT_API_KEY")
        if not self.api_key:
            print("Warning: PRODUCT_HUNT_API_KEY not set, using fallback search")
        
        self.base_url = "https://api.producthunt.com/v2/api/graphql"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def get_trending_posts(self, days: int = 1) -> List[Dict[str, Any]]:
        """
        获取 Product Hunt 热门产品
        """
        if not self.api_key:
            # 如果没有 API Key，返回空列表，依赖 Tavily 搜索
            return []
        
        # 计算日期范围
        since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        query = """
        query GetPosts($since: DateTime!) {
            posts(order: RANKING, postedAfter: $since, first: 20) {
                edges {
                    node {
                        id
                        name
                        tagline
                        description
                        url
                        votesCount
                        commentsCount
                        featuredAt
                        topics {
                            edges {
                                node {
                                    name
                                }
                            }
                        }
                        thumbnail {
                            url
                        }
                        user {
                            name
                        }
                    }
                }
            }
        }
        """
        
        variables = {"since": since}
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json={"query": query, "variables": variables},
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"Product Hunt API error: {response.status_code}")
                return []
            
            data = response.json()
            
            if "errors" in data:
                print(f"Product Hunt GraphQL error: {data['errors']}")
                return []
            
            posts = data.get("data", {}).get("posts", {}).get("edges", [])
            
            results = []
            for edge in posts:
                node = edge.get("node", {})
                
                # 只保留 AI 相关的产品
                topics = [t.get("node", {}).get("name", "").lower() 
                         for t in node.get("topics", {}).get("edges", [])]
                
                ai_keywords = ["ai", "artificial intelligence", "machine learning", 
                              "gpt", "llm", "chatbot", "automation", "agent"]
                
                is_ai_related = any(keyword in " ".join(topics) or 
                                   keyword in node.get("tagline", "").lower() or
                                   keyword in node.get("description", "").lower()
                                   for keyword in ai_keywords)
                
                if is_ai_related:
                    results.append({
                        "title": node.get("name", ""),
                        "tagline": node.get("tagline", ""),
                        "description": node.get("description", ""),
                        "url": node.get("url", ""),
                        "votes": node.get("votesCount", 0),
                        "comments": node.get("commentsCount", 0),
                        "topics": topics,
                        "featured_at": node.get("featuredAt", ""),
                        "thumbnail": node.get("thumbnail", {}).get("url", ""),
                        "maker": node.get("user", {}).get("name", "")
                    })
            
            # 按投票数排序
            results.sort(key=lambda x: x.get("votes", 0), reverse=True)
            
            return results[:10]  # 返回前10个
            
        except Exception as e:
            print(f"Error fetching Product Hunt data: {e}")
            return []
    
    def get_search_queries(self) -> List[str]:
        """
        返回用于 Tavily 搜索的 Product Hunt 相关查询
        """
        return [
            "Product Hunt AI product today",
            "Product Hunt trending AI",
            "Product Hunt launch AI tool",
            "Product Hunt top products artificial intelligence"
        ]


if __name__ == "__main__":
    client = ProductHuntClient()
    posts = client.get_trending_posts(days=1)
    print(f"Found {len(posts)} AI-related products on Product Hunt")
    for post in posts[:5]:
        print(f"- {post['title']} ({post['votes']} votes): {post['tagline'][:60]}...")

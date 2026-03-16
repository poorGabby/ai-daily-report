#!/usr/bin/env python3
"""
AI处理模块 - 使用Kimi API翻译和生成摘要
"""
import os
import json
from typing import List, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class AIProcessor:
    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key or os.getenv("KIMI_API_KEY")
        if not self.api_key:
            raise ValueError("KIMI_API_KEY is required")
        
        # Kimi API配置
        self.base_url = base_url or "https://api.moonshot.cn/v1"
        self.model = "moonshot-v1-128k"
        self.temperature = 0.3
        self.max_tokens = 8000
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def translate_and_summarize(
        self,
        title: str,
        content: str,
        category: str
    ) -> Dict[str, str]:
        """
        翻译并生成结构化摘要
        
        Returns:
            {
                "title_zh": "中文标题",
                "summary": "一句话摘要",
                "problem": "能解决什么问题",
                "applicable": "是否可以用在产品里",
                "example": "示例"
            }
        """
        prompt = f"""请分析以下{category}领域的文章，并按要求输出：

原标题：{title}

内容：
{content[:3000]}

请输出以下JSON格式（不要包含markdown代码块标记）：
{{
    "title_zh": "翻译成简洁准确的中文标题",
    "summary": "用一句话概括核心内容（30字以内）",
    "problem": "这项技术/产品能解决什么问题（50字以内）",
    "applicable": "是否可以应用到实际产品中，如何应用（50字以内）",
    "example": "给出一个具体的使用场景示例（30字以内）"
}}

要求：
1. 标题翻译要专业、简洁
2. 所有字段用中文回答
3. 内容要准确反映原文
4. 只输出JSON，不要其他内容"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的AI领域分析师，擅长翻译和技术内容分析。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            content = response.choices[0].message.content.strip()
            print(f"AI raw response: {content[:200]}...")
            
            # 清理可能的markdown代码块
            if content.startswith("```json"):
                content = content[7:]
            elif content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            # 清理其他可能的包裹
            content = content.strip()
            if content.startswith('"') and content.endswith('"'):
                content = content[1:-1]
            
            # 尝试解析JSON
            try:
                result = json.loads(content)
            except json.JSONDecodeError as je:
                print(f"JSON parse error: {je}, trying to extract JSON...")
                # 尝试从文本中提取JSON
                import re
                json_match = re.search(r'\{[\s\S]*\}', content)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    raise je
            
            return result
            
        except Exception as e:
            print(f"AI processing error: {e}")
            print(f"Raw content: {content[:200] if 'content' in locals() else 'N/A'}")
            # 返回默认结构
            return {
                "title_zh": title,
                "summary": f"内容解析失败: {str(e)[:50]}",
                "problem": "解析失败",
                "applicable": "解析失败",
                "example": "解析失败"
            }
    
    def generate_category_summary(
        self,
        category_name: str,
        items: List[Dict[str, Any]]
    ) -> str:
        """
        生成分类汇总摘要
        """
        if not items:
            return "今日暂无相关资讯。"
        
        # 构建输入
        items_text = "\n\n".join([
            f"{i+1}. {item.get('title_zh', item.get('title', ''))}\n   {item.get('summary', '')}"
            for i, item in enumerate(items[:5])  # 只取前5条
        ])
        
        prompt = f"""请为以下{category_name}领域的今日资讯写一个简短的汇总（100字以内）：

{items_text}

要求：
1. 概括今日主要动态
2. 指出最值得关注的1-2个点
3. 用中文简洁表达"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的AI领域分析师。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Category summary error: {e}")
            return f"今日{category_name}领域有{len(items)}条重要资讯。"
    
    def generate_daily_summary(
        self,
        all_categories: Dict[str, List[Dict[str, Any]]]
    ) -> str:
        """
        生成日报总览
        """
        # 构建输入
        summary_parts = []
        for category, items in all_categories.items():
            if items:
                titles = [item.get('title_zh', item.get('title', ''))[:30] + "..." 
                         for item in items[:3]]
                summary_parts.append(f"{category}: {', '.join(titles)}")
        
        content = "\n".join(summary_parts)
        
        prompt = f"""请根据以下今日AI领域资讯，写一个日报总览（200字以内）：

{content}

要求：
1. 用一段话概括今日AI领域的主要动态
2. 突出最重要的2-3个趋势或事件
3. 语气专业、简洁
4. 用中文表达"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的AI领域分析师，擅长撰写行业日报。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=800
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Daily summary error: {e}")
            total = sum(len(items) for items in all_categories.values())
            return f"今日共收集到{total}条AI领域重要资讯，涵盖技术发布、产品动态、融资等多个维度。"

#!/usr/bin/env python3
"""
日报生成器 - 主流程
"""
import os
import sys
import json
import yaml
from datetime import datetime
from pathlib import Path

from searcher import TavilySearcher
from ai_processor import AIProcessor


class DailyReportGenerator:
    def __init__(self):
        self.config = self._load_config()
        self.searcher = TavilySearcher()
        self.processor = AIProcessor()
        
        # 确保目录存在（基于项目根目录）
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        self.data_dir = project_root / "data"
        self.raw_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self) -> dict:
        """加载配置文件"""
        # 从脚本所在目录向上找到项目根目录
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        config_path = project_root / "config" / "sources.yaml"
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def run(self):
        """运行日报生成流程"""
        today = datetime.now().strftime("%Y-%m-%d")
        print(f"\n{'='*60}")
        print(f"开始生成 {today} 的AI日报")
        print(f"{'='*60}\n")
        
        # Step 1: 收集所有分类的原始数据
        print("Step 1: 收集原始数据...")
        raw_data = self._collect_raw_data()
        
        # 保存原始数据
        raw_file = self.raw_dir / f"{today}.json"
        with open(raw_file, 'w', encoding='utf-8') as f:
            json.dump(raw_data, f, ensure_ascii=False, indent=2)
        print(f"原始数据已保存: {raw_file}\n")
        
        # Step 2: AI处理（翻译、摘要）
        print("Step 2: AI处理内容...")
        processed_data = self._process_with_ai(raw_data)
        
        # Step 3: 生成汇总
        print("Step 3: 生成汇总...")
        summary = self._generate_summaries(processed_data)
        
        # Step 4: 保存处理后的数据
        processed_file = self.processed_dir / f"{today}.json"
        final_data = {
            "date": today,
            "generated_at": datetime.now().isoformat(),
            "daily_summary": summary["daily_summary"],
            "categories": processed_data,
            "category_summaries": summary["category_summaries"]
        }
        with open(processed_file, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)
        print(f"处理后的数据已保存: {processed_file}\n")
        
        # Step 5: 生成Markdown文件
        print("Step 4: 生成Markdown文件...")
        self._generate_markdown(final_data, today)
        
        print(f"\n{'='*60}")
        print(f"日报生成完成！")
        print(f"{'='*60}\n")
        
        return final_data
    
    def _collect_raw_data(self) -> dict:
        """收集原始数据"""
        categories = self.config.get("categories", {})
        raw_data = {}
        
        for key, category_config in categories.items():
            print(f"\n收集分类: {category_config.get('name_zh', key)}")
            results = self.searcher.search_category(category_config)
            raw_data[key] = results
            print(f"  共 {len(results)} 条")
        
        return raw_data
    
    def _process_with_ai(self, raw_data: dict) -> dict:
        """使用AI处理数据"""
        processed = {}
        
        for category_key, items in raw_data.items():
            category_name = self.config["categories"][category_key].get("name", category_key)
            category_name_zh = self.config["categories"][category_key].get("name_zh", category_key)
            
            print(f"\n处理分类: {category_name_zh}")
            processed_items = []
            
            for i, item in enumerate(items):
                print(f"  处理 {i+1}/{len(items)}: {item.get('title', '')[:50]}...")
                
                # AI处理
                ai_result = self.processor.translate_and_summarize(
                    title=item.get("title", ""),
                    content=item.get("content", ""),
                    category=category_name
                )
                
                processed_item = {
                    "title": item.get("title", ""),
                    "title_zh": ai_result.get("title_zh", ""),
                    "url": item.get("url", ""),
                    "summary": ai_result.get("summary", ""),
                    "problem": ai_result.get("problem", ""),
                    "applicable": ai_result.get("applicable", ""),
                    "example": ai_result.get("example", ""),
                    "published_date": item.get("published_date"),
                    "source": item.get("source", ""),
                    "score": item.get("score", 0)
                }
                
                processed_items.append(processed_item)
            
            # 按分数排序
            processed_items.sort(key=lambda x: x.get("score", 0), reverse=True)
            
            # 限制数量
            max_items = self.config.get("report", {}).get("max_items_per_category", 10)
            processed[category_key] = processed_items[:max_items]
        
        return processed
    
    def _generate_summaries(self, processed_data: dict) -> dict:
        """生成汇总"""
        category_summaries = {}
        
        for category_key, items in processed_data.items():
            category_name = self.config["categories"][category_key].get("name_zh", category_key)
            summary = self.processor.generate_category_summary(category_name, items)
            category_summaries[category_key] = summary
        
        daily_summary = self.processor.generate_daily_summary(processed_data)
        
        return {
            "category_summaries": category_summaries,
            "daily_summary": daily_summary
        }
    
    def _generate_markdown(self, data: dict, date: str):
        """生成Markdown文件"""
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        docs_dir = project_root / "docs"
        daily_dir = docs_dir / "daily"
        daily_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成分类文件
        for category_key, items in data["categories"].items():
            category_config = self.config["categories"][category_key]
            self._generate_category_md(
                date=date,
                category_key=category_key,
                category_config=category_config,
                items=items,
                summary=data["category_summaries"].get(category_key, ""),
                output_dir=daily_dir
            )
        
        # 生成日报汇总文件
        self._generate_summary_md(data, date, docs_dir)
        
        # 更新索引
        self._update_index(data, date, docs_dir)
    
    def _generate_category_md(
        self,
        date: str,
        category_key: str,
        category_config: dict,
        items: list,
        summary: str,
        output_dir: Path
    ):
        """生成分类Markdown文件"""
        filename = f"{date}-{category_key}.md"
        filepath = output_dir / filename
        
        content = f"""---
date: {date}
category: {category_config.get('name', category_key)}
---

# {category_config.get('name_zh', category_key)} - {date}

> {category_config.get('description', '')}

## 今日概览

{summary}

---

"""
        
        for i, item in enumerate(items, 1):
            content += f"""### {i}. {item.get('title_zh', item.get('title', ''))}

**原文标题**: [{item.get('title', '')}]({item.get('url', '')})

**一句话摘要**: {item.get('summary', '')}

**能解决什么问题**: {item.get('problem', '')}

**产品应用**: {item.get('applicable', '')}

**示例场景**: {item.get('example', '')}

---

"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  生成: {filepath}")
    
    def _generate_summary_md(self, data: dict, date: str, output_dir: Path):
        """生成日报汇总文件"""
        filename = f"{date}-summary.md"
        filepath = output_dir / filename
        
        categories = self.config.get("categories", {})
        
        content = f"""---
date: {date}
type: summary
---

# AI Daily Report - {date}

## 📋 今日总览

{data.get('daily_summary', '')}

---

"""
        
        for category_key, category_config in categories.items():
            items = data["categories"].get(category_key, [])
            if not items:
                continue
            
            category_summary = data["category_summaries"].get(category_key, "")
            
            content += f"""## {category_config.get('name_zh', category_key)}

> {category_config.get('description', '')}

{category_summary}

| # | 标题 | 核心看点 |
|---|------|----------|
"""
            for i, item in enumerate(items[:5], 1):
                title = item.get('title_zh', item.get('title', ''))[:40]
                summary = item.get('summary', '')[:50]
                content += f"| {i} | [{title}](./daily/{date}-{category_key}.md) | {summary}... |\n"
            
            content += "\n---\n\n"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  生成汇总: {filepath}")
    
    def _update_index(self, data: dict, date: str, output_dir: Path):
        """更新索引文件"""
        index_file = output_dir / "index.md"
        
        content = f"""---
layout: home
---

# AI Daily Report

每日自动收集AI领域最新资讯，生成结构化日报。

## 📅 最新日报

### [{date}](./{date}-summary.md)

{data.get('daily_summary', '')}

---

## 📂 历史归档

"""
        
        # 列出所有历史日报
        summary_files = sorted(
            [f for f in output_dir.glob("*-summary.md") if f.name != "index.md"],
            reverse=True
        )
        
        for f in summary_files[:30]:  # 最近30天
            d = f.stem.replace("-summary", "")
            content += f"- [{d}](./{f.name})\n"
        
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  更新索引: {index_file}")


if __name__ == "__main__":
    generator = DailyReportGenerator()
    generator.run()

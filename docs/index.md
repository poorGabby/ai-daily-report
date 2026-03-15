# AI Daily Report

每日自动收集AI领域最新资讯，生成结构化日报。

## 📋 日报分类

| 分类 | 说明 |
|------|------|
| **Technology** | AI模型、API、开源项目、Agent、Infra |
| **Product** | AI App、工具、浏览器、搜索、Copilot |
| **Startup** | 融资、收购、新公司 |
| **BigTech** | OpenAI、Google、Apple、Microsoft、Meta、Amazon战略 |
| **UX Trend** | 交互方式、Prompt UX、Agent UX、Workflow |

## 📅 最新日报

<LatestReport />

## 📂 关于

本项目使用 GitHub Actions 每日自动运行：

1. **数据收集** - 通过 Tavily API 搜索各领域最新资讯
2. **AI处理** - 使用 Kimi API 翻译、摘要、结构化
3. **站点生成** - 生成 VitePress 静态站点
4. **自动发布** - 部署到 GitHub Pages

---

*最后更新: {{ new Date().toLocaleDateString('zh-CN') }}*

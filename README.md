# AI Daily Report

每日自动收集AI领域最新资讯，生成结构化日报并发布到GitHub Pages。

## 📋 日报分类

1. **Technology** - AI/技术发布（新模型、API、开源项目、Agent、Infra）
2. **Product** - AI产品发布（App、工具、浏览器、搜索、Copilot）
3. **Startup** - 创业/融资（融资、收购、新公司）
4. **BigTech** - 大厂战略（OpenAI、Google、Apple、Microsoft、Meta、Amazon）
5. **UX Trend** - 产品设计趋势（交互方式、Prompt UX、Agent UX、Workflow）

## 🌐 在线访问

https://yourusername.github.io/ai-daily-report

## 🚀 本地开发

```bash
# 安装依赖
pip install -r requirements.txt
npm install

# 运行日报生成
python scripts/generate_daily.py

# 本地预览站点
npm run docs:dev
```

## 🔧 配置

复制 `.env.example` 为 `.env`，填入你的API密钥：

```bash
TAVILY_API_KEY=your_tavily_key
KIMI_API_KEY=your_kimi_key
```

## 📁 项目结构

```
ai-daily-report/
├── .github/workflows/daily.yml   # GitHub Actions 定时任务
├── scripts/                      # 数据抓取和处理脚本
├── docs/                         # VitePress 站点内容
├── data/                         # 生成的日报数据
└── config/                       # 配置文件
```

## 📝 License

MIT

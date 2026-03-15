import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'AI Daily Report',
  description: '每日AI领域资讯日报',
  base: '/ai-daily-report/',
  
  themeConfig: {
    nav: [
      { text: '首页', link: '/' },
      { text: '今日日报', link: '/latest' },
      { text: '历史归档', link: '/archive' }
    ],
    
    sidebar: {
      '/': [
        {
          text: '日报',
          items: [
            { text: '最新日报', link: '/latest' },
            { text: '历史归档', link: '/archive' }
          ]
        },
        {
          text: '分类',
          items: [
            { text: 'Technology', link: '/categories/technology' },
            { text: 'Product', link: '/categories/product' },
            { text: 'Startup', link: '/categories/startup' },
            { text: 'BigTech', link: '/categories/bigtech' },
            { text: 'UX Trend', link: '/categories/uxtrend' }
          ]
        }
      ]
    },
    
    socialLinks: [
      { icon: 'github', link: 'https://github.com/yourusername/ai-daily-report' }
    ],
    
    footer: {
      message: '自动生成于每日北京时间8:00',
      copyright: 'Copyright © 2024'
    }
  },
  
  head: [
    ['link', { rel: 'icon', href: '/favicon.ico' }],
    ['meta', { name: 'theme-color', content: '#3c3c3c' }]
  ]
})

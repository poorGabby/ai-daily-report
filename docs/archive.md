# 历史归档

<script setup>
import { ref, onMounted } from 'vue'

const reports = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    // 这里可以通过 API 获取所有历史日报列表
    // 暂时使用静态列表
    const response = await fetch('/ai-daily-report/data/processed/index.json')
    if (response.ok) {
      const data = await response.json()
      reports.value = data.reports || []
    }
  } catch (e) {
    console.error('Failed to load reports:', e)
  } finally {
    loading.value = false
  }
})
</script>

<div v-if="loading">加载中...</div>
<div v-else-if="reports.length > 0">

## 📂 所有日报

<div v-for="report in reports" :key="report.date">

### {{ report.date }}

{{ report.summary }}

[查看详情 →](./{{ report.date }}-summary.md)

---

</div>

</div>
<div v-else>

暂无历史数据。

</div>

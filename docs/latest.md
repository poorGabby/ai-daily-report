# 最新日报

<script setup>
import { ref, onMounted } from 'vue'

const latestDate = ref('')
const summary = ref('')
const loading = ref(true)

onMounted(async () => {
  try {
    // 获取最新的日报数据
    const response = await fetch('/ai-daily-report/data/processed/latest.json')
    if (response.ok) {
      const data = await response.json()
      latestDate.value = data.date
      summary.value = data.daily_summary
    }
  } catch (e) {
    console.error('Failed to load latest report:', e)
  } finally {
    loading.value = false
  }
})
</script>

<div v-if="loading">加载中...</div>
<div v-else-if="latestDate">

## 📅 {{ latestDate }}

{{ summary }}

[查看完整日报 →](./{{ latestDate }}-summary.md)

</div>
<div v-else>

暂无日报数据。请等待首次运行或查看 [历史归档](./archive.md)。

</div>

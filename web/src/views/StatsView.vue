<template>
  <div>
    <n-grid :cols="4" :x-gap="16">
      <n-gi>
        <n-card title="总项目数" hoverable>
          <span style="font-size: 36px; font-weight: 700; color: #1a1a2e;">{{ stats.total_projects }}</span>
        </n-card>
      </n-gi>
      <n-gi>
        <n-card title="进行中" hoverable>
          <span style="font-size: 36px; font-weight: 700; color: #1976d2;">{{ stats.active_projects }}</span>
        </n-card>
      </n-gi>
      <n-gi>
        <n-card title="已完成" hoverable>
          <span style="font-size: 36px; font-weight: 700; color: #388e3c;">{{ stats.completed_projects }}</span>
        </n-card>
      </n-gi>
      <n-gi>
        <n-card title="逾期项目" hoverable>
          <span style="font-size: 36px; font-weight: 700; color: #d32f2f;">{{ stats.overdue_projects }}</span>
        </n-card>
      </n-gi>
    </n-grid>

    <n-card style="margin-top: 16px;">
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <span style="font-size: 15px; font-weight: 600;">逾期任务总数</span>
        <span style="font-size: 24px; font-weight: 700; color: #d32f2f;">{{ stats.total_overdue_tasks }}</span>
      </div>
    </n-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { getOverview } from '../api/index.js'

const message = useMessage()
const stats = ref({
  total_projects: 0,
  active_projects: 0,
  completed_projects: 0,
  overdue_projects: 0,
  total_overdue_tasks: 0,
})

async function loadStats() {
  try {
    stats.value = await getOverview()
  } catch {
    message.error('加载统计失败')
  }
}

onMounted(loadStats)
</script>

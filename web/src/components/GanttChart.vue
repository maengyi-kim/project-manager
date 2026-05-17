<template>
  <div>
    <n-empty v-if="ganttData.length === 0" description="暂无可显示的任务（需要设置开始和截止日期）" />
    <div v-else class="gantt-wrapper">
      <div class="gantt-header" :style="{ width: ganttTotalWidth + 'px' }">
        <div v-for="(h, i) in ganttHeaders" :key="i" class="gantt-header-cell" :style="{ width: dayWidth + 'px' }">
          <div class="header-date">{{ h.day }}</div>
          <div class="header-weekday">{{ h.weekday }}</div>
        </div>
      </div>
      <div v-for="item in ganttData" :key="item.id" class="gantt-row" :style="{ paddingLeft: (item.depth || 0) * 16 + 'px' }">
        <span class="gantt-task-name">{{ item.title }}</span>
        <div class="gantt-track" :style="{ width: ganttTotalWidth + 'px' }">
          <div
            class="gantt-bar"
            :class="{ done: item.status === 'completed', overdue: item.is_overdue }"
            :style="{ left: item.barLeft + 'px', width: item.barWidth + 'px' }"
          >
            <div class="gantt-bar-progress" :style="{ width: item.progress + '%' }"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { getGanttData } from '../api/index.js'

const props = defineProps({
  projectId: Number,
})

const ganttData = ref([])
const ganttHeaders = ref([])
const ganttTotalWidth = ref(0)
const dayWidth = ref(36)

async function loadData() {
  try {
    const raw = await getGanttData(props.projectId)
    const tasks = raw.tasks || []
    if (tasks.length === 0) {
      ganttData.value = []
      return
    }

    let minDate = null, maxDate = null
    tasks.forEach(t => {
      if (t.start_date && (!minDate || t.start_date < minDate)) minDate = t.start_date
      if (t.deadline && (!maxDate || t.deadline > maxDate)) maxDate = t.deadline
    })

    const start = new Date(minDate)
    const end = new Date(maxDate)
    const totalDays = Math.ceil((end - start) / (1000 * 60 * 60 * 24)) + 1
    const dw = dayWidth.value

    const headers = []
    for (let i = 0; i < totalDays; i++) {
      const d = new Date(start)
      d.setDate(d.getDate() + i)
      headers.push({
        day: `${d.getMonth() + 1}/${d.getDate()}`,
        weekday: ['日','一','二','三','四','五','六'][d.getDay()],
      })
    }

    const data = tasks.map(t => {
      const tStart = t.start_date ? new Date(t.start_date) : start
      const tEnd = t.deadline ? new Date(t.deadline) : end
      const leftDays = Math.max(0, Math.ceil((tStart - start) / (1000 * 60 * 60 * 24)))
      const spanDays = Math.max(1, Math.ceil((tEnd - tStart) / (1000 * 60 * 60 * 24)) + 1)
      return {
        ...t,
        barLeft: leftDays * dw,
        barWidth: spanDays * dw,
      }
    })

    ganttData.value = data
    ganttHeaders.value = headers
    ganttTotalWidth.value = Math.max(totalDays * dw + 200, 600)
  } catch {
    // 静默失败
  }
}

watch(() => props.projectId, loadData)
onMounted(loadData)
</script>

<style scoped>
.gantt-wrapper { overflow-x: auto; }
.gantt-header { display: flex; border-bottom: 1px solid #eee; }
.gantt-header-cell { text-align: center; padding: 4px 0; font-size: 11px; }
.header-date { font-size: 12px; font-weight: 500; }
.header-weekday { font-size: 11px; color: #999; }
.gantt-row {
  display: flex;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f5f5f5;
  min-height: 36px;
}
.gantt-task-name {
  font-size: 12px; color: #555;
  min-width: 120px; max-width: 160px;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  flex-shrink: 0;
}
.gantt-track { position: relative; height: 24px; }
.gantt-bar {
  position: absolute; height: 20px; top: 2px;
  background: #e3f2fd; border: 1px solid #90caf9; border-radius: 4px; overflow: hidden;
}
.gantt-bar.done { background: #e8f5e9; border-color: #81c784; }
.gantt-bar.overdue { background: #ffebee; border-color: #ef9a9a; }
.gantt-bar-progress { height: 100%; background: #42a5f5; opacity: 0.6; }
</style>

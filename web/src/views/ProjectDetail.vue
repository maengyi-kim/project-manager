<template>
  <div>
    <n-button text @click="router.push('/projects')" style="margin-bottom: 12px;">
      ← 返回项目列表
    </n-button>

    <!-- 项目头部 -->
    <n-card>
      <div style="display: flex; justify-content: space-between; align-items: start;">
        <div>
          <div style="display: flex; align-items: center; gap: 8px;">
            <h2 style="margin: 0;">{{ project.name }}</h2>
            <n-tag v-if="project.overdue_count > 0" type="error" size="small">逾期 {{ project.overdue_count }}</n-tag>
          </div>
          <p v-if="project.description" style="color: #888; font-size: 13px;">{{ project.description }}</p>
        </div>
      </div>
      <n-progress type="line" :percentage="Math.round(project.progress)" :height="8" :rail-color="'#ee ee'" />
      <div style="display: flex; gap: 16px; margin-top: 8px; font-size: 12px; color: #999;">
        <span>任务: {{ project.task_count || 0 }}</span>
        <span v-if="project.start_date">{{ project.start_date }} ~ {{ project.end_date || '待定' }}</span>
      </div>
    </n-card>

      <!-- 融合视图：任务信息 + 甘特时间轴 -->
    <n-card style="margin-top: 16px;" content-style="padding:0;" :seg="{content:true}">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 16px 16px 0;">
          <span style="font-weight: 600;">任务分解与时间规划</span>
          <n-button size="small" @click="openEditor(null, null, true)">+ 添加任务</n-button>
        </div>
      </template>

      <n-empty v-if="tasks.length === 0" description="还没有任务，点击上方添加" />

      <!-- 固定日期头 + 滚动内容区 -->
      <div class="gantt-viewport">
        <!-- 日期头（固定） -->
        <div v-if="ganttHeaders.length > 0" class="gantt-header" :style="{ width: ganttTotalWidth + 'px' }">
          <div v-for="(h, i) in ganttHeaders" :key="i" class="gantt-header-cell" :style="{ width: dayWidth + 'px' }">
            <div class="header-date" :class="{ 'mark-day': h.day.endsWith('/1') || h.day.endsWith('/5') || h.day.endsWith('/10') || h.day.endsWith('/15') || h.day.endsWith('/20') || h.day.endsWith('/25') }">{{ h.day }}</div>
            <div class="header-weekday">{{ h.weekday }}</div>
          </div>
        </div>

        <!-- 任务行（可滚动） -->
        <div class="task-gantt-scroll">
          <div v-for="t in tasks" :key="t.id" class="task-gantt-row">
            <!-- 左侧任务信息 -->
            <div
              class="task-info"
              :class="[
                t.depth === 0 ? 'task-root' : 'task-child',
                'depth-' + t.depth,
                t.progress === 100 ? 'task-completed' : '',
                t.priority === 0 ? 'task-p0' : '',
                t.priority === 1 ? 'task-p1' : '',
              ]"
              :style="{ paddingLeft: ((t.depth || 0) * 16 + 8) + 'px' }"
              @click="openEditor(t.id, null, false)"
            >
            <div class="task-check" :class="{ done: t.progress === 100 }" @click.stop>
              <span v-if="t.progress === 100">✓</span>
              <span v-else-if="t.status === 'in_progress'">◉</span>
              <span v-else>○</span>
            </div>
            <div class="task-content">
              <div class="task-title-row">
                <span class="task-title" :class="{ done: t.progress === 100 }">{{ t.title }}</span>
                <n-tag v-if="t.is_overdue" size="tiny" type="error">逾期</n-tag>
              </div>
              <div class="task-meta">
                <span v-if="t.assignee">{{ t.assignee }}</span>
                <span v-if="t.start_date">{{ t.start_date }}</span>
                <span v-if="t.deadline">~ {{ t.deadline }}</span>
              </div>
            </div>
            <span class="task-progress">{{ Math.round(t.progress) }}%</span>
          </div>

          <!-- 右侧甘特条 -->
          <div class="gantt-area" :style="{ width: ganttTotalWidth + 'px' }">
            <!-- 标记竖线 -->
            <div
              v-for="(line, li) in markerLines"
              :key="'line-' + li"
              class="marker-line"
              :style="{ left: line + 'px' }"
            ></div>
            <div
              v-if="ganttMap[t.id]"
              class="gantt-bar"
              :class="{ done: ganttMap[t.id].status === 'completed', overdue: ganttMap[t.id].is_overdue }"
              :style="{
                left: ganttMap[t.id].barLeft + 'px',
                width: ganttMap[t.id].barWidth + 'px',
              }"
            >
              <div class="gantt-bar-progress" :style="{ width: ganttMap[t.id].progress + '%' }"></div>
            </div>
          </div>
        </div>
      </div>
    </n-card>

    <!-- 任务编辑器 -->
    <TaskEditor
      v-model:show="showEditor"
      :project-id="projectId"
      :task-id="editingTaskId"
      :parent-id="editingParentId"
      :is-new="isNewTask"
      @saved="onTaskSaved"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { getProject, getGanttData } from '../api/index.js'
import TaskEditor from '../components/TaskEditor.vue'

const route = useRoute()
const router = useRouter()
const message = useMessage()

const projectId = ref(parseInt(route.params.id))
const project = ref({})
const tasks = ref([])
const dayWidth = ref(36)
const ganttTotalWidth = ref(0)
const ganttHeaders = ref([])
const ganttData = ref([])
const ganttMap = ref({})
const markerLines = ref([])

const showEditor = ref(false)
const editingTaskId = ref(null)
const editingParentId = ref(null)
const isNewTask = ref(false)

function buildTaskTree(rawTasks) {
  const map = {}
  rawTasks.forEach(t => map[t.id] = t)
  function getDepth(id) {
    let d = 0, cur = map[id]
    while (cur && cur.parent_id) {
      d++
      cur = map[cur.parent_id]
      if (!cur || d >= 2) break
    }
    return d
  }
  const roots = rawTasks.filter(t => t.parent_id === null)
  const result = []
  function addWithChildren(items) {
    for (const item of items) {
      const depth = getDepth(item.id)
      result.push({ ...item, depth })
      const children = rawTasks.filter(t => t.parent_id === item.id)
      children.sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0))
      for (const child of children) {
        const childDepth = getDepth(child.id)
        result.push({ ...child, depth: childDepth })
        const gchildren = rawTasks.filter(t => t.parent_id === child.id)
        gchildren.sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0))
        for (const g of gchildren) {
          result.push({ ...g, depth: getDepth(g.id) })
        }
      }
    }
  }
  roots.sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0))
  addWithChildren(roots)
  return result
}

async function loadProject() {
  try {
    const p = await getProject(projectId.value)
    project.value = p
    tasks.value = buildTaskTree(p.tasks || [])
    await loadGantt()
  } catch {
    message.error('加载项目失败')
  }
}

async function loadGantt() {
  try {
    const raw = await getGanttData(projectId.value)
    const items = raw.tasks || []
    if (items.length === 0) {
      ganttTotalWidth.value = 400
      return
    }
    let minDate = null, maxDate = null
    items.forEach(t => {
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

    const map = {}
    const data = items.map(t => {
      const tStart = t.start_date ? new Date(t.start_date) : start
      const tEnd = t.deadline ? new Date(t.deadline) : end
      const leftDays = Math.max(0, Math.ceil((tStart - start) / (1000 * 60 * 60 * 24)))
      const spanDays = Math.max(1, Math.ceil((tEnd - tStart) / (1000 * 60 * 60 * 24)) + 1)
      const bar = { ...t, barLeft: leftDays * dw, barWidth: spanDays * dw }
      map[t.id] = bar
      return bar
    })

    ganttData.value = data
    ganttMap.value = map
    ganttHeaders.value = headers
    ganttTotalWidth.value = Math.max(totalDays * dw, 300)

    // 计算标记竖线位置（1,5,10,15,20,25日）
    const markDays = [1, 5, 10, 15, 20, 25]
    const lines = []
    for (let i = 0; i < totalDays; i++) {
      const d = new Date(start)
      d.setDate(d.getDate() + i)
      if (markDays.includes(d.getDate())) {
        lines.push(i * dw)
      }
    }
    markerLines.value = lines
  } catch {
    ganttTotalWidth.value = 400
  }
}

function openEditor(taskId, parentId, isNew) {
  editingTaskId.value = taskId || null
  editingParentId.value = parentId || null
  isNewTask.value = !!isNew
  showEditor.value = true
}

function onTaskSaved() {
  showEditor.value = false
  loadProject()
}

onMounted(loadProject)
</script>

<style scoped>
/* 甘特视口：日期头固定，任务行可滚动 */
.gantt-viewport {
  overflow: hidden;
  padding: 0 16px 16px;
}

/* 日期头（固定在顶部） */
.gantt-header {
  display: flex;
  border-bottom: 1px solid #eee;
  margin-left: 380px;
  position: sticky;
  top: 0;
  background: #fff;
  z-index: 1;
}

/* 任务行容器（可垂直+水平滚动） */
.task-gantt-scroll {
  overflow-x: auto;
  overflow-y: auto;
  max-height: 500px;
}

.task-gantt-row {
  display: flex;
  align-items: stretch;
  border-bottom: 1px solid #f0f0f0;
  min-height: 44px;
}
.task-gantt-row:last-child { border-bottom: none; }

/* 左侧任务信息 */
.task-info {
  display: flex;
  align-items: center;
  width: 380px;
  min-width: 380px;
  padding: 8px 8px;
  cursor: pointer;
  box-sizing: border-box;
  border-right: 1px solid #eee;
}
.task-info:active { opacity: 0.7; }

.task-root { border-left: 4px solid #1a1a2e; }
.task-root .task-title { font-weight: 600; }
.task-child { border-left: 3px solid #90caf9; }
.task-child .task-title { color: #555; }

.task-check {
  width: 22px; height: 22px;
  border: 2px solid #ccc;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 8px;
  font-size: 12px;
  color: #4caf50;
  flex-shrink: 0;
}
.task-check.done { border-color: #4caf50; background: #e8f5e9; }

.task-content { flex: 1; min-width: 0; }
.task-title-row { display: flex; align-items: center; gap: 4px; }
.task-title { font-size: 13px; color: #333; }
.task-title.done { text-decoration: line-through; color: #999; }
.task-meta { font-size: 11px; color: #999; margin-top: 1px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.task-progress { font-size: 12px; color: #666; margin-left: 6px; min-width: 32px; text-align: right; flex-shrink: 0; }

/* 右侧甘特区 */
.gantt-area {
  position: relative;
  flex-shrink: 0;
}

.gantt-header-cell { text-align: center; padding: 3px 0; font-size: 11px; flex-shrink: 0; position: relative; }
.header-date { font-size: 11px; font-weight: 500; }
.header-weekday { font-size: 10px; color: #999; }
.mark-day { font-weight: 700; color: #1a1a2e; }

/* 标记竖线 */
.marker-line {
  position: absolute;
  top: 0;
  width: 1px;
  height: 100%;
  background: #e0e0e0;
  z-index: 0;
  pointer-events: none;
}

.gantt-bar {
  position: absolute;
  height: 20px;
  top: 50%;
  transform: translateY(-50%);
  background: #e3f2fd;
  border: 1px solid #90caf9;
  border-radius: 4px;
  overflow: hidden;
}
.gantt-bar.done { background: #e8f5e9; border-color: #81c784; }
.gantt-bar.overdue { background: #ffebee; border-color: #ef9a9a; }
.gantt-bar-progress { height: 100%; background: #42a5f5; opacity: 0.6; }

/* 颜色 */
.task-completed { background: #e8f5e9 !important; }
.task-completed .task-title { color: #2e7d32; }
.task-p0 { background: #fff5f5 !important; }
.task-p0 .task-title { color: #c62828; font-weight: 500; }
.task-p1 { background: #fff8e1 !important; }
.task-p1 .task-title { color: #e65100; font-weight: 500; }
</style>

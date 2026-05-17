<template>
  <n-drawer :show="show" :width="520" placement="right" @update:show="val => emit('update:show', val)">
    <n-drawer-content :title="isNew ? '新建任务' : '编辑任务'" closable>
      <n-form v-if="task" label-placement="top">
        <n-form-item label="任务名称">
          <n-input v-model:value="task.title" placeholder="输入任务名称" />
        </n-form-item>
        <n-form-item label="负责人">
          <n-input v-model:value="task.assignee" placeholder="负责人姓名" />
        </n-form-item>
        <n-space style="width: 100%;">
          <n-form-item label="开始日期" style="flex: 1;">
            <n-date-picker v-model:value="task.startDateTs" type="date" placeholder="请选择" clearable style="width: 100%;" />
          </n-form-item>
          <n-form-item label="截止日期" style="flex: 1;">
            <n-date-picker v-model:value="task.deadlineTs" type="date" placeholder="请选择" clearable style="width: 100%;" />
          </n-form-item>
        </n-space>
        <n-form-item label="优先级">
          <n-radio-group v-model:value="task.priority">
            <n-radio-button v-for="p in priorities" :key="p.value" :value="p.value" :disabled="p.disabled">{{ p.label }}</n-radio-button>
          </n-radio-group>
        </n-form-item>
        <n-form-item label="进度: {{ Math.round(task.progress) }}%">
          <n-slider v-model:value="task.progress" :min="0" :max="100" :step="5" />
          <n-space style="margin-top: 8px; width: 100%;">
            <n-button v-for="p in [0, 25, 50, 75, 100]" :key="p" size="tiny" @click="task.progress = p">{{ p }}%</n-button>
          </n-space>
        </n-form-item>
        <n-form-item label="备注">
          <n-input v-model:value="task.remark" type="textarea" placeholder="更新进度说明、遇到的问题等" />
        </n-form-item>

        <!-- 子任务列表 -->
        <n-form-item v-if="children.length > 0" label="子任务">
          <n-list>
            <n-list-item v-for="c in children" :key="c.id" clickable @click="$emit('edit-child', c.id)">
              <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
                <div style="display: flex; align-items: center; gap: 8px;">
                  <span :style="{ textDecoration: c.progress === 100 ? 'line-through' : 'none', color: c.progress === 100 ? '#999' : '#333' }">{{ c.title }}</span>
                </div>
                <span style="font-size: 12px; color: #888;">{{ Math.round(c.progress) }}%</span>
              </div>
            </n-list-item>
          </n-list>
        </n-form-item>
        <n-form-item v-else-if="!isNew && taskDepth < 2" label="子任务">
          <n-button size="small" dashed @click="$emit('add-subtask')">+ 添加子任务</n-button>
        </n-form-item>
        <div v-else-if="!isNew && taskDepth >= 2" style="font-size: 13px; color: #bbb; text-align: center; padding: 16px;">
          已达到最大深度，不再支持添加子任务
        </div>
      </n-form>

      <template #footer>
        <n-space justify="space-between">
          <n-button v-if="!isNew" type="error" @click="handleDelete">删除任务</n-button>
          <n-space>
            <n-button @click="show = false">取消</n-button>
            <n-button type="primary" :loading="saving" @click="handleSave">保存</n-button>
          </n-space>
        </n-space>
      </template>
    </n-drawer-content>
  </n-drawer>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useMessage, useDialog } from 'naive-ui'
import { createTask, updateTask, deleteTask, getTaskTree } from '../api/index.js'

const props = defineProps({
  show: Boolean,
  projectId: Number,
  taskId: [Number, null],
  parentId: [Number, null],
  isNew: Boolean,
})
const emit = defineEmits(['update:show', 'saved', 'edit-child', 'add-subtask'])

const message = useMessage()
const dialog = useDialog()

const saving = ref(false)
const task = ref(null)
const children = ref([])
const taskDepth = ref(0)

const priorities = [
  { label: 'P0-急', value: 0 },
  { label: 'P1-高', value: 1 },
  { label: 'P2-中', value: 2 },
  { label: 'P3-低', value: 3 },
]

function initTask() {
  return {
    title: '',
    assignee: '',
    startDateTs: null,
    deadlineTs: null,
    priority: 2,
    progress: 0,
    remark: '',
  }
}

function tsToDate(ts) {
  if (!ts) return null
  const d = new Date(ts)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

function dateToTs(dateStr) {
  if (!dateStr) return null
  return new Date(dateStr).getTime()
}

async function loadTask(taskId) {
  try {
    const tasks = await getTaskTree(props.projectId)
    const t = tasks.find(t => t.id === taskId)
    if (t) {
      const taskData = {
        title: t.title,
        assignee: t.assignee || '',
        startDateTs: dateToTs(t.start_date),
        deadlineTs: dateToTs(t.deadline),
        priority: t.priority,
        progress: t.progress,
        remark: t.remark || '',
      }
      task.value = taskData
      children.value = tasks.filter(c => c.parent_id === taskId)
      // 计算深度
      taskDepth.value = calcDepth(taskId, tasks)
    }
  } catch {
    message.error('加载任务失败')
  }
}

function calcDepth(id, tasks) {
  const map = {}
  tasks.forEach(t => map[t.id] = t)
  let d = 0, cur = map[id]
  while (cur && cur.parent_id) {
    d++
    cur = map[cur.parent_id]
    if (!cur || d >= 2) break
  }
  return d
}

watch(() => props.show, (val) => {
  if (val) {
    if (props.isNew) {
      task.value = initTask()
      children.value = []
      taskDepth.value = 0
    } else if (props.taskId) {
      loadTask(props.taskId)
    }
  }
})

async function handleSave() {
  if (!task.value.title) {
    message.warning('请输入任务名称')
    return
  }
  saving.value = true
  try {
    const data = {
      project_id: props.projectId,
      parent_id: props.isNew ? (props.parentId || null) : undefined,
      title: task.value.title,
      assignee: task.value.assignee,
      start_date: tsToDate(task.value.startDateTs),
      deadline: tsToDate(task.value.deadlineTs),
      priority: task.value.priority,
      progress: task.value.progress,
      remark: task.value.remark,
    }
    if (props.isNew) {
      await createTask(data)
      message.success('创建成功')
    } else {
      await updateTask(props.taskId, data)
      message.success('保存成功')
    }
    emit('saved')
  } catch {
    message.error('保存失败')
  } finally {
    saving.value = false
  }
}

function handleDelete() {
  dialog.warning({
    title: '确认删除',
    content: '子任务也会一起删除',
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await deleteTask(props.taskId)
        message.success('已删除')
        emit('saved')
      } catch {
        message.error('删除失败')
      }
    },
  })
}
</script>

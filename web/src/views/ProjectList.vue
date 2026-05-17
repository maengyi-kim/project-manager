<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
      <h2 style="margin: 0;">项目列表</h2>
      <n-button type="primary" @click="showNewModal = true">+ 新建项目</n-button>
    </div>

    <n-grid :cols="1" :x-gap="16" :y-gap="16">
      <n-gi v-for="p in projects" :key="p.id">
        <ProjectCard :project="p" @click="router.push(`/projects/${p.id}`)" @delete="handleDelete(p.id)" />
      </n-gi>
    </n-grid>

    <!-- 新建项目弹窗 -->
    <n-modal v-model:show="showNewModal" title="新建项目" preset="card" style="width: 480px;" :mask-closable="false">
      <n-form ref="formRef" :model="newProject" :rules="rules" label-placement="top">
        <n-form-item label="项目名称" path="name">
          <n-input v-model:value="newProject.name" placeholder="输入项目名称" />
        </n-form-item>
        <n-form-item label="项目描述">
          <n-input v-model:value="newProject.description" type="textarea" placeholder="可选" />
        </n-form-item>
        <n-form-item label="开始日期">
          <n-date-picker v-model:value="newProject.startDateTs" type="date" placeholder="可选" clearable />
        </n-form-item>
        <n-form-item label="结束日期">
          <n-date-picker v-model:value="newProject.endDateTs" type="date" placeholder="可选" clearable />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showNewModal = false">取消</n-button>
          <n-button type="primary" :loading="saving" @click="handleCreate">创建</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage, useDialog } from 'naive-ui'
import { getProjects, createProject, deleteProject } from '../api/index.js'
import ProjectCard from '../components/ProjectCard.vue'

const router = useRouter()
const message = useMessage()
const dialog = useDialog()

const projects = ref([])
const showNewModal = ref(false)
const saving = ref(false)

const newProject = ref({
  name: '',
  description: '',
  startDateTs: null,
  endDateTs: null,
})

const rules = {
  name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
}

function tsToDate(ts) {
  if (!ts) return null
  const d = new Date(ts)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

async function loadProjects() {
  try {
    projects.value = await getProjects()
  } catch {
    message.error('加载项目列表失败')
  }
}

async function handleCreate() {
  saving.value = true
  try {
    await createProject({
      name: newProject.value.name,
      description: newProject.value.description,
      start_date: tsToDate(newProject.value.startDateTs),
      end_date: tsToDate(newProject.value.endDateTs),
    })
    message.success('创建成功')
    showNewModal.value = false
    newProject.value = { name: '', description: '', startDateTs: null, endDateTs: null }
    await loadProjects()
  } catch {
    message.error('创建失败')
  } finally {
    saving.value = false
  }
}

function handleDelete(id) {
  dialog.warning({
    title: '确认删除',
    content: '删除后所有任务也会被删除，不可恢复',
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await deleteProject(id)
        message.success('已删除')
        await loadProjects()
      } catch {
        message.error('删除失败')
      }
    },
  })
}

onMounted(loadProjects)
</script>

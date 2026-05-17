import axios from 'axios'

// 后端 API 基地址
const BASE_URL = 'https://pm.maengyi.top'

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
})

// 项目
export const getProjects = () => api.get('/api/projects').then(r => r.data)
export const getProject = (id) => api.get(`/api/projects/${id}`).then(r => r.data)
export const createProject = (data) => api.post('/api/projects', data).then(r => r.data)
export const updateProject = (id, data) => api.put(`/api/projects/${id}`, data).then(r => r.data)
export const deleteProject = (id) => api.delete(`/api/projects/${id}`).then(r => r.data)
export const shareProject = (id) => api.get(`/api/projects/${id}/share`).then(r => r.data)

// 任务
export const getTaskTree = (projectId) => api.get(`/api/tasks/tree/${projectId}`).then(r => r.data)
export const getGanttData = (projectId) => api.get(`/api/tasks/gantt/${projectId}`).then(r => r.data)
export const createTask = (data) => api.post('/api/tasks', data).then(r => r.data)
export const updateTask = (id, data) => api.put(`/api/tasks/${id}`, data).then(r => r.data)
export const deleteTask = (id) => api.delete(`/api/tasks/${id}`).then(r => r.data)

// 统计
export const getOverview = () => api.get('/api/stats/overview').then(r => r.data)

export default api

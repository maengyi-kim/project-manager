<template>
  <n-card :title="project.name" hoverable :seg="{
    content: true,
  }" :style="{
    borderLeft: project.overdue_count > 0 ? '4px solid #e53935' : project.progress === 100 ? '4px solid #43a047' : '4px solid #1a1a2e',
    cursor: 'pointer',
  }" @click="$emit('click')">
    <template #header-extra>
      <n-tag v-if="project.overdue_count > 0" type="error" size="small">逾期 {{ project.overdue_count }}</n-tag>
      <n-tag v-else-if="project.progress === 100" type="success" size="small">已完成</n-tag>
    </template>

    <p v-if="project.description" style="color: #888; font-size: 13px; margin: 0 0 12px;">{{ project.description }}</p>

    <n-progress
      type="line"
      :percentage="Math.round(project.progress)"
      :color="project.overdue_count > 0 ? '#e53935' : undefined"
      :height="8"
      :rail-color="'#eee'"
    />

    <div style="display: flex; gap: 16px; margin-top: 10px; font-size: 12px; color: #999;">
      <span>任务: {{ project.task_count || 0 }}</span>
      <span v-if="project.start_date">{{ project.start_date }} ~ {{ project.end_date || '待定' }}</span>
    </div>

    <template #action>
      <n-space justify="end">
        <n-button text type="error" size="small" @click.stop="$emit('delete')">删除</n-button>
      </n-space>
    </template>
  </n-card>
</template>

<script setup>
defineProps({ project: { type: Object, required: true } })
defineEmits(['click', 'delete'])
</script>

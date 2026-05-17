<template>
  <div>
    <n-empty v-if="tasks.length === 0" description="还没有任务，点击上方添加" />

    <!-- 任务列表 -->
    <div v-for="t in tasks" :key="t.id" class="task-item" :style="{ paddingLeft: ((t.depth || 0) * 20 + 12) + 'px' }">
      <div
        class="task-inner"
        :class="[
          t.depth === 0 ? 'task-root' : 'task-child',
          'depth-' + t.depth,
          t.progress === 100 ? 'task-completed' : '',
          t.priority === 0 ? 'task-p0' : '',
          t.priority === 1 ? 'task-p1' : '',
        ]"
        @click="$emit('edit-task', t.id, null, false)"
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
            <span v-if="t.start_date">开始 {{ t.start_date }}</span>
            <span v-if="t.deadline">截止 {{ t.deadline }}</span>
          </div>
          <n-progress v-if="t.child_count > 0" type="line" :percentage="Math.round(t.progress)" :height="4" :rail-color="'#eee'" />
        </div>
        <span class="task-progress">{{ Math.round(t.progress) }}%</span>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  projectId: Number,
  tasks: Array,
})
defineEmits(['refresh', 'edit-task'])
</script>

<style scoped>
.task-item { margin-bottom: 6px; }
.task-inner {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.task-inner:active { opacity: 0.7; }

.task-root {
  background: #fff;
  border-left: 4px solid #1a1a2e;
  box-shadow: 0 2px 6px rgba(0,0,0,0.06);
}
.task-root .task-title { font-weight: 600; }

.task-child {
  background: #fff;
  border-left: 3px solid #90caf9;
  border-radius: 8px 4px 4px 8px;
}
.task-child .task-title { color: #555; }

.task-check {
  width: 24px; height: 24px;
  border: 2px solid #ccc;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 10px;
  font-size: 14px;
  color: #4caf50;
  flex-shrink: 0;
}
.task-check.done { border-color: #4caf50; background: #e8f5e9; }

.task-content { flex: 1; min-width: 0; }
.task-title-row { display: flex; align-items: center; gap: 6px; }
.task-title { font-size: 14px; color: #333; }
.task-title.done { text-decoration: line-through; color: #999; }
.task-meta { font-size: 11px; color: #999; margin-top: 2px; display: flex; gap: 8px; }
.task-progress { font-size: 13px; color: #666; margin-left: 10px; min-width: 36px; text-align: right; }

/* 已完成 */
.task-completed { background: #e8f5e9 !important; border-color: #a5d6a7 !important; }
.task-completed .task-title { color: #2e7d32; }
.task-completed .task-meta { color: rgba(46,125,50,0.6); }
.task-completed .task-progress { color: #388e3c; }

/* P0 */
.task-p0 { background: #fff5f5 !important; border-color: #ffcdd2 !important; }
.task-p0 .task-title { color: #c62828; font-weight: 500; }
.task-p0 .task-meta { color: rgba(198,40,40,0.6); }
.task-p0 .task-progress { color: #d32f2f; }

/* P1 */
.task-p1 { background: #fff8e1 !important; border-color: #ffe082 !important; }
.task-p1 .task-title { color: #e65100; font-weight: 500; }
.task-p1 .task-meta { color: rgba(230,81,0,0.6); }
.task-p1 .task-progress { color: #ff8f00; }

.depth-2 { border-left-color: #64b5f6; border-right: 3px solid #e3f2fd; }
.depth-3 { border-left-color: #42a5f5; border-right: 3px solid #bbdefb; }
</style>

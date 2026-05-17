<template>
  <div>
    <n-empty v-if="filtered.length === 0" description="暂无可显示的任务（需要设置开始和截止日期）" />
    <div v-for="item in filtered" :key="item.id" class="simple-item" :style="{ paddingLeft: ((item.depth || 0) * 20 + 12) + 'px' }">
      <div class="simple-bar" :class="{ done: item.status === 'completed', overdue: item.is_overdue }">
        <div class="simple-title">{{ item.title }}</div>
        <div class="simple-dates">{{ item.start_date || '--' }} → {{ item.deadline || '--' }}</div>
        <div class="simple-progress">
          <n-progress type="line" :percentage="Math.round(item.progress)" :height="6" :rail-color="'#eee'" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  tasks: Array,
})

const filtered = computed(() => {
  return (props.tasks || []).filter(t => t.start_date || t.deadline)
})
</script>

<style scoped>
.simple-item { margin-bottom: 6px; }
.simple-bar {
  background: #fff; border-radius: 8px; padding: 10px 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  border-left: 3px solid #42a5f5;
}
.simple-bar.done { border-left-color: #66bb6a; }
.simple-bar.overdue { border-left-color: #ef5350; }
.simple-title { font-size: 14px; font-weight: 500; color: #333; }
.simple-dates { font-size: 12px; color: #888; margin: 4px 0; }
.simple-progress { margin-top: 4px; }
</style>

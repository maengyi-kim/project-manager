<template>
  <n-message-provider>
    <n-dialog-provider>
      <n-notification-provider>
        <n-config-provider :theme-overrides="themeOverrides">
          <n-layout position="absolute">
            <n-layout-header bordered style="height: 56px; padding: 0 48px; display: flex; align-items: center; justify-content: space-between;">
              <div style="display: flex; align-items: center; gap: 40px; white-space: nowrap;">
                <router-link to="/projects" style="text-decoration: none; white-space: nowrap;">
                  <span style="font-size: 18px; font-weight: 700; color: #1a1a2e; letter-spacing: 1px;">项目管家</span>
                </router-link>
                <n-menu mode="horizontal" :value="activeMenu" :options="menuOptions" />
              </div>
            </n-layout-header>
            <n-layout-content style="height: calc(100vh - 56px); padding: 24px 48px; background: #f5f6fa; overflow-y: auto;">
                <router-view />
            </n-layout-content>
          </n-layout>
        </n-config-provider>
      </n-notification-provider>
    </n-dialog-provider>
  </n-message-provider>
</template>

<script setup>
import { computed, h } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NIcon } from 'naive-ui'
import { ListOutline, BarChartOutline } from '@vicons/ionicons5'

const route = useRoute()
const router = useRouter()

const activeMenu = computed(() => {
  if (route.path.startsWith('/projects')) return 'projects'
  if (route.path.startsWith('/stats')) return 'stats'
  return null
})

const menuOptions = [
  {
    label: () => '项目列表',
    key: 'projects',
    icon: () => h(NIcon, null, { default: () => h(ListOutline) }),
    onClick: () => router.push('/projects'),
  },
  {
    label: () => '统计',
    key: 'stats',
    icon: () => h(NIcon, null, { default: () => h(BarChartOutline) }),
    onClick: () => router.push('/stats'),
  },
]

const themeOverrides = {
  common: {
    primaryColor: '#1a1a2e',
    primaryColorHover: '#2d2d4e',
    primaryColorPressed: '#0f0f1e',
  },
}
</script>

<style>
body { margin: 0; }
a { color: inherit; }
</style>

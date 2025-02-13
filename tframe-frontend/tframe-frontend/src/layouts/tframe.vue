<script setup lang="ts">
import { ref } from 'vue'
import {
  Expand,
  Fold,
  Menu as IconMenu,
  Message as IconMessage,
  Setting as IconSetting,
  Moon,
  Sunny
} from '@element-plus/icons-vue'
import { useDark, useToggle } from '@vueuse/core'

defineProps<{
  title: string
}>()

const isCollapse = ref(false)
const isDark = useDark()
const toggleDark = useToggle(isDark)
</script>

<template>
  <div class="layout">
    <!-- 顶部标题栏 -->
    <el-header class="header">
      <div class="header-left">
        <el-button
          class="collapse-btn"
          text
          @click="isCollapse = !isCollapse"
        >
          <el-icon :size="20">
            <component :is="isCollapse ? Expand : Fold" />
          </el-icon>
        </el-button>
        <h2>{{ title }}</h2>
      </div>
      <div class="header-right">
        <el-dropdown>
          <el-avatar size="small" src="https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png" />
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item>个人信息</el-dropdown-item>
              <el-dropdown-item>退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <el-button
          class="theme-switch"
          text
          @click="toggleDark()"
        >
          <el-icon :size="20">
            <Moon v-if="!isDark" />
            <Sunny v-else />
          </el-icon>
        </el-button>
      </div>
    </el-header>
    
    <div class="container">
      <!-- 左侧菜单 -->
      <el-menu
        class="sidebar"
        :collapse="isCollapse"
        default-active="1"
      >
        <el-menu-item index="1">
          <el-icon><IconMessage /></el-icon>
          <template #title>导航一</template>
        </el-menu-item>
        
        <el-sub-menu index="2">
          <template #title>
            <el-icon><IconMenu /></el-icon>
            <span>导航二</span>
          </template>
          <el-menu-item index="2-1">选项1</el-menu-item>
          <el-menu-item index="2-2">选项2</el-menu-item>
        </el-sub-menu>
        
        <el-menu-item index="3">
          <el-icon><IconSetting /></el-icon>
          <template #title>导航三</template>
        </el-menu-item>
      </el-menu>
      
      <!-- 右侧内容区 -->
      <el-main class="content">
        <slot></slot>
      </el-main>
    </div>
  </div>
</template>

<style scoped>
.layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--el-border-color-light);
  background-color: var(--el-bg-color);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-left h2 {
  margin: 0;
}

.container {
  display: flex;
  flex: 1;
}

.sidebar {
  border-right: 1px solid var(--el-border-color-light);
}

.sidebar:not(.el-menu--collapse) {
  width: 200px;
}

.content {
  flex: 1;
  background-color: var(--el-bg-color-page);
  transition: background-color 0.3s ease;
}

.collapse-btn {
  height: 40px;
  width: 40px;
  padding: 0;
  border: none;
  color: var(--el-text-color-primary);
}

.collapse-btn:hover {
  background-color: var(--el-fill-color-light);
}

.collapse-btn .el-icon {
  color: var(--el-text-color-primary);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-direction: row-reverse;
}

.theme-switch {
  height: 40px;
  width: 40px;
  padding: 0;
  border: none;
  color: var(--el-text-color-primary);
  margin-right: 8px;
}

.theme-switch:hover {
  background-color: var(--el-fill-color-light);
  border-radius: 4px;
}

.theme-switch .el-icon {
  color: var(--el-text-color-primary);
}
</style>
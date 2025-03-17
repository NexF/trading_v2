<script setup lang="ts">
import tframe from './layouts/tframe.vue'
</script>

<template>
  <tframe title="K线图应用">
    <!-- 这里是主要内容 -->
    <div class="main-content">
      <router-view />
    </div>
  </tframe>
</template>

<style scoped>
.main-content {
  padding: 1rem;
  height: calc(100vh - 60px); /* 减去头部导航的高度 */
  box-sizing: border-box;
}
</style>

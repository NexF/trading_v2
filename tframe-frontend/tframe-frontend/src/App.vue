<script setup lang="ts">
import HelloWorld from './components/HelloWorld.vue'
import tframe from './layouts/tframe.vue'
</script>

<template>
  <tframe title="我的应用">
    <!-- 这里是主要内容 -->
    <div class="main-content">
      <h2>欢迎使用</h2>
      <p>这是主要内容区域</p>
    </div>
  </tframe>
</template>

<style scoped>
.main-content {
  padding: 1rem;
}
</style>

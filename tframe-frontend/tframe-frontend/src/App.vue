<script setup lang="ts">
import HelloWorld from './components/HelloWorld.vue'
import tframe from './layouts/tframe.vue'
import KLine from './components/KLine.vue'
</script>

<template>
  <tframe title="我的应用">
    <!-- 这里是主要内容 -->
    <div class="main-content">
      <KLine />
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

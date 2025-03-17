import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/kline-demo'
  },
  {
    path: '/kline-demo',
    name: 'KlineDemo',
    component: () => import('../views/KlineDemo.vue'),
    meta: {
      title: 'K线图演示'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - TFrame` : 'TFrame'
  next()
})

export default router 
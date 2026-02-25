import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/nav_page',
      name: 'navigation',
      component: () => import('../views/NavigationView.vue'),
    },
    {
      path: '/doctor_page',
      name: 'medical',
      component: () => import('../views/MedicalView.vue'),
    },
    {
      path: '/chat',
      redirect: '/nav_page',
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('../views/SettingsView.vue'),
    },
  ],
})

// 全局前置守卫：设置页面切换动画为淡入淡出
router.beforeEach((to, from) => {
  // 所有页面切换都使用淡入淡出动画
  to.meta.transition = 'fade'
  return true
})

export default router

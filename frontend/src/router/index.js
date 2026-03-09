// frontend/src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login'
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/login.vue') // 注意：确保这里的文件名大小写与你实际文件一致
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/Register.vue')
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('../views/Dashboard.vue'),
      children: [
        {
          path: '', 
          name: 'welcome',
          component: () => import('../views/Welcome.vue')
        },
        {
          path: 'assets',
          name: 'assets',
          component: () => import('../views/AssetList.vue')
        },
        {
          path: 'sniff',
          name: 'host-sniff',
          component: () => import('../views/HostSniff.vue')
        },
        {
          path: 'scan/web',
          name: 'web-scan',
          component: () => import('../views/WebScan.vue')
        },
        {
          path: 'reports',
          name: 'reports',
          component: () => import('../views/Report.vue')
        },
        {
          path: 'scan/host',
          name: 'host-scan',
          component: () => import('../views/HostScan.vue')
        },
        {
          path: 'ai',
          name: 'ai-chat',
          component: () => import('../views/AiChat.vue')
        },
      ]
    }
  ]
})

export default router
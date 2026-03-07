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
      component: () => import('../views/Login.vue')
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
      // 使用 children 定义嵌套路由（子路由）
      children: [
        {
          // 当路径是 /dashboard 时，默认匹配这个空路径，展示 Welcome 组件
          path: '', 
          name: 'welcome',
          component: () => import('../views/Welcome.vue')
        },
        // 我们后续开发的资产管理、漏洞扫描页面，都会加在这里面！
        // 例如: { path: 'assets', component: AssetList }
        {
          path: 'assets',
          name: 'assets',
          component: () => import('../views/AssetList.vue')
        },
        {
          path: 'reports',
          name: 'reports',
          component: () => import('../views/Report.vue')
        },
        {
          path: 'assets',
          name: 'assets',
          component: () => import('../views/AssetList.vue')
        },
        // --- 新增下面这段 ---
        {
          path: 'scan/web',
          name: 'web-scan',
          component: () => import('../views/WebScan.vue')
        },
        // -------------------
        {
          path: 'reports',
          name: 'reports',
          component: () => import('../views/Report.vue')
        }
      ]
    }
  ]
})

export default router
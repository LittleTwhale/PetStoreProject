import { createRouter, createWebHistory } from 'vue-router'
import LoginPage from '../views/LoginPage.vue'
import ProfilePage from '../views/ProfilePage.vue'
import AdminPage from '../views/AdminPage.vue'
import MainLayout from '../layout/MainLayout.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: LoginPage,
      meta: { requiresAuth: false },
    },
    {
      path: '/',
      component: MainLayout,
      redirect: '/dashboard',
      children: [
        {
          path: 'dashboard',
          name: 'Dashboard',
          component: ProfilePage, // 暂时复用，后续可替换为独立 Dashboard
          meta: { title: '数据工作台' },
        },
        {
          path: 'profile',
          name: 'Profile',
          component: ProfilePage,
          meta: { title: '个人中心' },
        },
        {
          path: 'admin',
          name: 'Admin',
          component: AdminPage,
          meta: { title: '用户管理', requiresAdmin: true },
        },
      ],
    },
  ],
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')

  // 未登录只能访问登录页
  if (to.path !== '/login' && !token) {
    next('/login')
    return
  }

  // 已登录访问登录页 → 跳转首页
  if (to.path === '/login' && token) {
    next('/dashboard')
    return
  }

  next()
})

export default router

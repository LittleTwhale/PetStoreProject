// router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import LoginPage from '../views/LoginPage.vue' //[cite: 1]
import ProfilePage from '../views/ProfilePage.vue' //[cite: 1]
import MainLayout from '../layout/MainLayout.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL), //[cite: 1]
  routes: [
    {
      path: '/login', //[cite: 1]
      name: 'Login', //[cite: 1]
      component: LoginPage, //[cite: 1]
      meta: { requiresAuth: false },
    },
    {
      path: '/', //[cite: 1]
      component: MainLayout, // 嵌套路由的核心：指向 Layout
      redirect: '/dashboard', //[cite: 1]
      children: [
        {
          path: 'dashboard',
          name: 'Dashboard',
          // 你可以之后建一个 Dashboard 页面，这里先复用 Profile 作为占位
          component: ProfilePage,
        },
        {
          path: 'profile', //[cite: 1]
          name: 'Profile', //[cite: 1]
          component: ProfilePage, //[cite: 1]
        },
      ],
    },
  ],
})

// 路由守卫：防止未登录访问后台
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.path !== '/login' && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router //[cite: 1]

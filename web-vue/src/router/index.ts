import { createRouter, createWebHistory } from 'vue-router'
// 引入视图组件
import LoginPage from '../views/LoginPage.vue'
import ProfilePage from '../views/ProfilePage.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      // 访问根目录时，默认跳转到登录页
      path: '/',
      redirect: '/login',
    },
    {
      path: '/login',
      name: 'Login',
      component: LoginPage,
    },
    {
      path: '/profile',
      name: 'Profile',
      component: ProfilePage,
    },
  ],
})

export default router

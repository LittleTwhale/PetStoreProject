import { ref } from 'vue'
import { defineStore } from 'pinia'
import { authApi } from '@/api'

export interface UserInfo {
  id: number
  nickname: string
  avatar: string | null
  role: string
  position_desc: string | null
  permissions: unknown
  is_active: boolean
  created_at: string
  updated_at: string
  identifier: string | null
}

export const useUserStore = defineStore('user', () => {
  const user = ref<UserInfo | null>(null)
  const isLoggedIn = ref(false)

  async function fetchUser() {
    try {
      const res = await authApi.getMe()
      user.value = res.data
      isLoggedIn.value = true
    } catch {
      user.value = null
      isLoggedIn.value = false
      throw new Error('获取用户信息失败')
    }
  }

  function logout() {
    localStorage.removeItem('token')
    user.value = null
    isLoggedIn.value = false
  }

  return { user, isLoggedIn, fetchUser, logout }
})

import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

// 请求拦截器 — 自动附加 Token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器 — 统一错误处理
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      router.push('/login')
      ElMessage.error('登录已过期，请重新登录')
    }
    return Promise.reject(error)
  },
)

export default api

// ==================== 认证 API ====================
export const authApi = {
  login: (data: { identifier: string; password: string }) =>
    api.post('/auth/login', data),

  register: (data: { identifier: string; password: string; nickname: string }) =>
    api.post('/auth/register', data),

  getMe: () => api.get('/auth/me'),

  updateMe: (data: { nickname?: string; position_desc?: string }) =>
    api.put('/auth/me', data),

  uploadAvatar: (file: Blob, filename: string) => {
    const formData = new FormData()
    formData.append('file', file, filename)
    return api.post('/auth/me/avatar', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  changePassword: (data: { old_password: string; new_password: string }) =>
    api.put('/auth/me/password', data),
}

// ==================== 管理员 API ====================
export const adminApi = {
  listUsers: () => api.get('/auth/admin/users'),

  createUser: (data: {
    identifier: string
    password: string
    nickname: string
    role: string
    position_desc?: string
  }) => api.post('/auth/admin/users', data),

  updateUser: (
    userId: number,
    data: {
      nickname?: string
      role?: string
      position_desc?: string
      is_active?: boolean
      permissions?: unknown
    },
  ) => api.put(`/auth/admin/users/${userId}`, data),

  deleteUser: (userId: number) => api.delete(`/auth/admin/users/${userId}`),
}

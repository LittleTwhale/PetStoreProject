// api/store.ts — 门店管理 API
import api from './index'

export interface Store {
  id: number
  name: string
  code: string
  address: string | null
  phone: string | null
  manager_id: number | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface UserStore {
  id: number
  user_id: number
  store_id: number
  is_primary: boolean
  created_at: string
}

export interface StoreUser {
  user_id: number
  store_id: number
  is_primary: boolean
  nickname: string
  role: string
  position_desc: string | null
}

export const storeApi = {
  /** 获取门店列表（admin看全部） */
  list: (params?: { search?: string; skip?: number; limit?: number }) =>
    api.get('/stores/', { params }),

  /** 获取当前用户绑定的门店（staff返回自己的，admin返回全部） */
  my: () => api.get('/stores/my'),

  /** 获取门店详情 */
  get: (id: number) => api.get(`/stores/${id}`),

  /** 创建门店 */
  create: (data: {
    name: string
    code: string
    address?: string
    phone?: string
    manager_id?: number
  }) => api.post('/stores/', data),

  /** 更新门店 */
  update: (id: number, data: {
    name?: string
    code?: string
    address?: string
    phone?: string
    manager_id?: number
    is_active?: boolean
  }) => api.put(`/stores/${id}`, data),

  /** 停用门店 */
  delete: (id: number) => api.delete(`/stores/${id}`),

  /** 绑定用户到门店 */
  bindUser: (storeId: number, data: { user_id: number; is_primary?: boolean }) =>
    api.post(`/stores/${storeId}/users`, data),

  /** 解绑用户 */
  unbindUser: (storeId: number, userId: number) =>
    api.delete(`/stores/${storeId}/users/${userId}`),

  /** 获取门店绑定用户列表 */
  getUsers: (storeId: number) => api.get(`/stores/${storeId}/users`),
}

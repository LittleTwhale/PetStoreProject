// api/customer.ts — 客户档案管理 API
import api from './index'

export interface CustomerProfile {
  id: number
  user_id: number | null
  store_id: number | null
  real_name: string | null
  phone: string | null
  address: string | null
  membership_level: string
  points: number
  balance: number
  pets: unknown[] // 嵌套的宠物列表
}

export const customerApi = {
  /** 获取客户列表，支持搜索、门店过滤和分页 */
  list: (params?: { search?: string; store_id?: number; skip?: number; limit?: number }) =>
    api.get('/customers/', { params }),

  /** 获取单个客户详情 */
  get: (id: number) => api.get(`/customers/${id}`),

  /** 创建客户档案（user_id 可选，未注册顾客可不传） */
  create: (data: {
    user_id?: number
    real_name?: string
    phone?: string
    address?: string
    membership_level?: string
    points?: number
    balance?: number
    store_id?: number
  }) => api.post('/customers/', data),

  /** 更新客户档案 */
  update: (
    id: number,
    data: {
      real_name?: string
      phone?: string
      address?: string
      membership_level?: string
      points?: number
      balance?: number
    },
  ) => api.put(`/customers/${id}`, data),

  /** 删除客户档案 */
  delete: (id: number) => api.delete(`/customers/${id}`),
}

// api/service.ts — 服务管理 API
import api from './index'

export interface Service {
  id: number
  store_id: number
  name: string
  category: string
  price: number
  duration_minutes: number
  description: string | null
  is_active: boolean
  created_at: string
  updated_at: string
  store_name: string | null
}

export const serviceApi = {
  list: (params?: {
    store_id?: number
    category?: string
    search?: string
    skip?: number
    limit?: number
  }) => api.get('/services/', { params }),

  getById: (id: number) => api.get(`/services/${id}`),

  create: (data: {
    store_id: number
    name: string
    category?: string
    price?: number
    duration_minutes?: number
    description?: string
  }) => api.post('/services/', data),

  update: (id: number, data: {
    store_id?: number
    name?: string
    category?: string
    price?: number
    duration_minutes?: number
    description?: string
    is_active?: boolean
  }) => api.put(`/services/${id}`, data),

  delete: (id: number) => api.delete(`/services/${id}`),
}

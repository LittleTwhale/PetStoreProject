// api/product.ts — 商品管理 API
import api from './index'

export interface Product {
  id: number
  store_id: number
  name: string
  product_type: string
  pet_id: number | null
  inventory_item_id: number | null
  price: number
  cost_price: number | null
  stock: number
  description: string | null
  cover_image: string | null
  is_active: boolean
  created_at: string
  updated_at: string
  pet_name: string | null
  inventory_item_name: string | null
  store_name: string | null
}

export const productApi = {
  list: (params?: {
    store_id?: number
    product_type?: string
    search?: string
    skip?: number
    limit?: number
  }) => api.get('/products/', { params }),

  getById: (id: number) => api.get(`/products/${id}`),

  create: (data: {
    store_id: number
    name: string
    product_type?: string
    pet_id?: number | null
    inventory_item_id?: number | null
    price?: number
    cost_price?: number | null
    stock?: number
    description?: string
    cover_image?: string
  }) => api.post('/products/', data),

  update: (id: number, data: {
    store_id?: number
    name?: string
    product_type?: string
    pet_id?: number | null
    inventory_item_id?: number | null
    price?: number
    cost_price?: number | null
    stock?: number
    description?: string
    cover_image?: string
    is_active?: boolean
  }) => api.put(`/products/${id}`, data),

  delete: (id: number) => api.delete(`/products/${id}`),
}

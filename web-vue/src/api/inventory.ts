// api/inventory.ts — 库存管理 API
import api from './index'

export interface InventoryCategory {
  id: number
  name: string
  description: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface InventoryItem {
  id: number
  category_id: number
  store_id: number
  name: string
  sku: string
  unit: string
  quantity: number
  safety_stock: number
  unit_price: number | null
  selling_price: number | null
  supplier: string | null
  is_active: boolean
  created_at: string
  updated_at: string
  category_name: string | null
}

export interface InventoryLog {
  id: number
  item_id: number
  store_id: number
  change_type: string
  quantity_change: number
  quantity_after: number
  operator_id: number | null
  remark: string | null
  created_at: string
  item_name: string | null
  item_sku: string | null
}

export const inventoryApi = {
  // ==================== 分类 ====================
  listCategories: (params?: { search?: string; skip?: number; limit?: number }) =>
    api.get('/inventory/categories/', { params }),

  createCategory: (data: { name: string; description?: string }) =>
    api.post('/inventory/categories/', data),

  updateCategory: (id: number, data: { name?: string; description?: string; is_active?: boolean }) =>
    api.put(`/inventory/categories/${id}`, data),

  deleteCategory: (id: number) => api.delete(`/inventory/categories/${id}`),

  // ==================== 物品 ====================
  listItems: (params?: {
    store_id?: number
    category_id?: number
    search?: string
    low_stock_only?: boolean
    skip?: number
    limit?: number
  }) => api.get('/inventory/items/', { params }),

  getItem: (id: number) => api.get(`/inventory/items/${id}`),

  createItem: (data: {
    category_id: number
    store_id: number
    name: string
    sku: string
    unit?: string
    quantity?: number
    safety_stock?: number
    unit_price?: number
    selling_price?: number
    supplier?: string
  }) => api.post('/inventory/items/', data),

  updateItem: (id: number, data: {
    category_id?: number
    name?: string
    sku?: string
    unit?: string
    safety_stock?: number
    unit_price?: number
    selling_price?: number
    supplier?: string
    is_active?: boolean
  }) => api.put(`/inventory/items/${id}`, data),

  deleteItem: (id: number) => api.delete(`/inventory/items/${id}`),

  // ==================== 出入库 ====================
  stockIn: (data: { item_id: number; quantity: number; unit_price?: number; remark?: string }) =>
    api.post('/inventory/items/stock-in', data),

  stockOut: (data: { item_id: number; quantity: number; remark?: string }) =>
    api.post('/inventory/items/stock-out', data),

  // ==================== 流水 ====================
  getLogs: (params?: {
    store_id?: number
    item_id?: number
    change_type?: string
    operator_id?: number
    start_time?: string
    end_time?: string
    skip?: number
    limit?: number
  }) => api.get('/inventory/logs/', { params }),
}

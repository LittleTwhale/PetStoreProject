// api/order.ts — 订单管理 API
import api from './index'

export interface OrderItem {
  id: number
  order_id: number
  item_type: string
  product_id: number | null
  service_id: number | null
  quantity: number
  unit_price: number
  subtotal: number
  staff_id: number | null
  product_name: string | null
  service_name: string | null
  staff_name: string | null
}

export interface Order {
  id: number
  order_no: string
  store_id: number
  order_type: string
  customer_id: number | null
  total_amount: number
  discount_amount: number
  final_amount: number
  payment_method: string
  status: string
  operator_id: number | null
  remark: string | null
  created_at: string
  updated_at: string
  customer_name: string | null
  operator_name: string | null
  store_name: string | null
  item_count?: number
  items?: OrderItem[]
}

export interface OrderCreateItem {
  item_type: string
  product_id?: number | null
  service_id?: number | null
  quantity: number
  unit_price: number
  subtotal: number
  staff_id?: number | null
}

export interface OrderCreate {
  store_id: number
  order_type: string
  customer_id?: number | null
  discount_amount?: number
  payment_method?: string
  operator_id?: number | null
  remark?: string | null
  items: OrderCreateItem[]
}

export const orderApi = {
  list: (params?: {
    store_id?: number
    order_type?: string
    status?: string
    search?: string
    start_date?: string
    end_date?: string
    customer_id?: number
    skip?: number
    limit?: number
  }) => api.get('/orders/', { params }),

  getById: (id: number) => api.get(`/orders/${id}`),

  create: (data: OrderCreate) => api.post('/orders/', data),

  update: (id: number, data: {
    order_type?: string
    customer_id?: number | null
    discount_amount?: number
    payment_method?: string
    remark?: string
  }) => api.put(`/orders/${id}`, data),

  updateStatus: (id: number, data: {
    status: string
    remark?: string
  }) => api.put(`/orders/${id}/status`, data),
}

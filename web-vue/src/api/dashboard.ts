// api/dashboard.ts — 数据面板 API
import api from './index'

export interface DailyTrend {
  date: string
  order_count: number
  revenue: number
}

export interface InventoryAlert {
  id: number
  name: string
  sku: string
  quantity: number
  safety_stock: number
  unit: string
}

export interface TopItem {
  id: number
  name: string
  count: number
  revenue: number
}

export interface RecentOrder {
  id: number
  order_no: string
  order_type: string
  final_amount: number
  status: string
  customer_name: string | null
  created_at: string
}

export interface DashboardData {
  today_revenue: number
  today_orders: number
  month_revenue: number
  month_orders: number
  pending_orders: number
  low_stock_count: number
  daily_trend: DailyTrend[]
  inventory_alerts: InventoryAlert[]
  top_products: TopItem[]
  top_services: TopItem[]
  recent_orders: RecentOrder[]
}

export const dashboardApi = {
  getSummary: (store_id?: number) =>
    api.get('/dashboard/summary', { params: store_id ? { store_id } : {} }),
}

<script setup lang="ts">
// views/OrderPage.vue — 订单管理
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, Search, EditPen, Document, Coin, CreditCard, RefreshRight } from '@element-plus/icons-vue'
import { orderApi, type Order, type OrderItem } from '@/api/order'
import { useUserStore } from '@/stores/user'
import { useStoreStore } from '@/stores/store'

const router = useRouter()
const userStore = useUserStore()
const storeStore = useStoreStore()
const isAdmin = computed(() => userStore.user?.role === 'admin')

// ========== 数据 ==========
const orders = ref<Order[]>([])
const isLoading = ref(false)
const searchText = ref('')
const filterType = ref<string | null>(null)
const filterStatus = ref<string | null>(null)
const dateRange = ref<[string, string] | null>(null)

const totalCount = computed(() => orders.value.length)
const saleCount = computed(() => orders.value.filter(o => o.order_type === 'sale').length)
const serviceCount = computed(() => orders.value.filter(o => o.order_type === 'service').length)
const totalRevenue = computed(() =>
  orders.value
    .filter(o => o.status !== 'cancelled' && o.status !== 'refunded')
    .reduce((sum, o) => sum + o.final_amount, 0),
)

// ========== 状态编辑弹窗 ==========
const statusDialogVisible = ref(false)
const statusLoading = ref(false)
const statusForm = reactive({ status: '', remark: '' })
const statusOrderId = ref<number | null>(null)
const statusOrderName = ref('')

const openStatusDialog = (order: Order) => {
  statusOrderId.value = order.id
  statusOrderName.value = order.order_no
  statusForm.status = order.status
  statusForm.remark = ''
  statusDialogVisible.value = true
}

const handleStatusUpdate = async () => {
  if (statusOrderId.value === null) return
  statusLoading.value = true
  try {
    await orderApi.updateStatus(statusOrderId.value, {
      status: statusForm.status,
      remark: statusForm.remark || undefined,
    })
    ElMessage.success('状态已更新')
    statusDialogVisible.value = false
    await fetchOrders()
  } catch (err: unknown) {
    ElMessage.error(
      (err as { response?: { data?: { detail?: string } } }).response?.data?.detail || '更新失败',
    )
  } finally { statusLoading.value = false }
}

// ========== 详情弹窗 ==========
const detailDialogVisible = ref(false)
const detailOrder = ref<Order | null>(null)

const openDetailDialog = async (order: Order) => {
  try {
    const res = await orderApi.getById(order.id)
    detailOrder.value = res.data
    detailDialogVisible.value = true
  } catch {
    ElMessage.error('获取订单详情失败')
  }
}

// ========== 加载 ==========
const fetchOrders = async () => {
  isLoading.value = true
  try {
    const params: Record<string, string | number | undefined> = {
      limit: 200,
      store_id: storeStore.currentStoreId ?? undefined,
      order_type: filterType.value ?? undefined,
      status: filterStatus.value ?? undefined,
      search: searchText.value || undefined,
    }
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    const res = await orderApi.list(params)
    orders.value = res.data
  } catch {
    ElMessage.error('获取订单列表失败')
  } finally { isLoading.value = false }
}

onMounted(() => { fetchOrders() })

// 监听门店切换自动刷新
watch(() => storeStore.currentStoreId, () => { fetchOrders() })

// ========== 支付 ==========
const handlePay = async (order: Order) => {
  try {
    await orderApi.updateStatus(order.id, {
      status: 'paid',
      remark: '确认收款',
    })
    ElMessage.success('已确认收款')
    await fetchOrders()
  } catch { /* ignore */ }
}

// ========== 工具函数 ==========
const typeLabel = (type: string) => type === 'sale' ? '销售' : '服务'
const typeTag = (type: string) => type === 'sale' ? 'success' : 'warning'

const statusLabelMap: Record<string, string> = {
  pending: '待支付', paid: '已支付', completed: '已完成', cancelled: '已取消', refunded: '已退款',
}
const statusTagMap: Record<string, string> = {
  pending: 'warning', paid: 'info', completed: 'success', cancelled: '', refunded: 'danger',
}
const statusLabel = (s: string) => statusLabelMap[s] || s
const statusTag = (s: string) => statusTagMap[s] || ''

const payMethodMap: Record<string, string> = {
  cash: '现金', wechat: '微信', alipay: '支付宝', card: '刷卡', balance: '余额',
}
const payMethodLabel = (m: string) => payMethodMap[m] || m

const formatDate = (d: string) => {
  if (!d) return ''
  return new Date(d).toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}
</script>

<template>
  <div class="page-root">
    <div class="page-header">
      <div>
        <h2 class="page-title">订单管理</h2>
        <p class="page-subtitle">管理销售订单与服务订单</p>
      </div>
      <el-button type="primary" :icon="Plus" size="large" @click="router.push('/orders/create')">
        创建订单
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-icon" style="background:#ecf5ff;color:#409eff"><el-icon :size="22"><Document /></el-icon></div>
        <div class="stat-body"><span class="stat-num">{{ totalCount }}</span><span class="stat-label">订单总数</span></div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background:#f0f9eb;color:#67c23a"><el-icon :size="22"><Coin /></el-icon></div>
        <div class="stat-body"><span class="stat-num">{{ saleCount }}</span><span class="stat-label">销售订单</span></div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background:#fdf6ec;color:#e6a23c"><el-icon :size="22"><CreditCard /></el-icon></div>
        <div class="stat-body"><span class="stat-num">{{ serviceCount }}</span><span class="stat-label">服务订单</span></div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background:#fef0f0;color:#f56c6c"><el-icon :size="22"><Coin /></el-icon></div>
        <div class="stat-body"><span class="stat-num">¥{{ totalRevenue.toFixed(2) }}</span><span class="stat-label">有效营收</span></div>
      </div>
    </div>

    <!-- 筛选 -->
    <div class="toolbar">
      <div class="filter-group">
        <el-input v-model="searchText" placeholder="搜索订单号..." :prefix-icon="Search" clearable class="search-input" @change="fetchOrders" />
        <el-select v-model="filterType" placeholder="订单类型" clearable class="filter-select" @change="fetchOrders">
          <el-option label="销售订单" value="sale" />
          <el-option label="服务订单" value="service" />
        </el-select>
        <el-select v-model="filterStatus" placeholder="订单状态" clearable class="filter-select" @change="fetchOrders">
          <el-option label="待支付" value="pending" />
          <el-option label="已支付" value="paid" />
          <el-option label="已完成" value="completed" />
          <el-option label="已取消" value="cancelled" />
          <el-option label="已退款" value="refunded" />
        </el-select>
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          class="date-picker"
          @change="fetchOrders"
        />
      </div>
      <el-button :icon="RefreshRight" @click="fetchOrders">刷新</el-button>
    </div>

    <!-- 表格 -->
    <div class="table-card">
      <el-table :data="orders" v-loading="isLoading" stripe style="width:100%">
        <el-table-column label="订单号" width="180">
          <template #default="{ row }">
            <span style="font-weight:600;font-size:13px">{{ row.order_no }}</span>
          </template>
        </el-table-column>
        <el-table-column label="类型" width="70">
          <template #default="{ row }">
            <el-tag :type="typeTag(row.order_type)" size="small">{{ typeLabel(row.order_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="客户" min-width="100">
          <template #default="{ row }">{{ row.customer_name || '散客' }}</template>
        </el-table-column>
        <el-table-column label="金额" width="120">
          <template #default="{ row }">
            <span style="font-weight:600">¥{{ Number(row.final_amount).toFixed(2) }}</span>
            <span v-if="row.discount_amount > 0" style="font-size:12px;color:#909399;text-decoration:line-through;margin-left:4px">
              ¥{{ Number(row.total_amount).toFixed(2) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="支付方式" width="80">
          <template #default="{ row }">{{ payMethodLabel(row.payment_method) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作人" width="90">
          <template #default="{ row }">{{ row.operator_name || '—' }}</template>
        </el-table-column>
        <el-table-column label="时间" width="110">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link :icon="EditPen" @click="openDetailDialog(row)">详情</el-button>
            <el-button
              v-if="row.status === 'pending'"
              type="success" link :icon="CreditCard" @click="handlePay(row)"
            >收款</el-button>
            <el-button
              v-if="row.status !== 'cancelled' && row.status !== 'refunded'"
              type="warning" link :icon="EditPen" @click="openStatusDialog(row)"
            >改状态</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 状态修改弹窗 -->
    <el-dialog v-model="statusDialogVisible" :title="`修改订单状态 - ${statusOrderName}`" width="420px" :close-on-click-modal="false">
      <el-form label-width="80px">
        <el-form-item label="新状态">
          <el-select v-model="statusForm.status" style="width:100%">
            <el-option label="待支付" value="pending" />
            <el-option label="已支付" value="paid" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
            <el-option v-if="isAdmin" label="已退款" value="refunded" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="statusForm.remark" placeholder="状态变更原因（可选）" maxlength="100" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="statusDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="statusLoading" @click="handleStatusUpdate">确认修改</el-button>
      </template>
    </el-dialog>

    <!-- 订单详情弹窗 -->
    <el-dialog v-model="detailDialogVisible" title="订单详情" width="640px" :close-on-click-modal="false">
      <template v-if="detailOrder">
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="订单号">{{ detailOrder.order_no }}</el-descriptions-item>
          <el-descriptions-item label="类型">
            <el-tag :type="typeTag(detailOrder.order_type)" size="small">{{ typeLabel(detailOrder.order_type) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="客户">{{ detailOrder.customer_name || '散客' }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="statusTag(detailOrder.status)" size="small">{{ statusLabel(detailOrder.status) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="支付方式">{{ payMethodLabel(detailOrder.payment_method) }}</el-descriptions-item>
          <el-descriptions-item label="操作人">{{ detailOrder.operator_name || '—' }}</el-descriptions-item>
          <el-descriptions-item label="总金额">¥{{ Number(detailOrder.total_amount).toFixed(2) }}</el-descriptions-item>
          <el-descriptions-item label="优惠">¥{{ Number(detailOrder.discount_amount).toFixed(2) }}</el-descriptions-item>
          <el-descriptions-item label="实付金额"><span style="font-weight:700;color:#f56c6c">¥{{ Number(detailOrder.final_amount).toFixed(2) }}</span></el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ detailOrder.created_at }}</el-descriptions-item>
          <el-descriptions-item v-if="detailOrder.remark" label="备注" :span="2">{{ detailOrder.remark }}</el-descriptions-item>
        </el-descriptions>

        <!-- 明细列表 -->
        <div v-if="detailOrder.items && detailOrder.items.length > 0" style="margin-top:16px">
          <h4 style="margin:0 0 8px 0;font-size:14px;color:#303133">订单明细</h4>
          <el-table :data="detailOrder.items" size="small" border>
            <el-table-column label="项目" min-width="140">
              <template #default="{ row: item }: { row: OrderItem }">
                {{ item.product_name || item.service_name || '—' }}
              </template>
            </el-table-column>
            <el-table-column label="类型" width="60">
              <template #default="{ row: item }: { row: OrderItem }">
                {{ item.item_type === 'product' ? '商品' : '服务' }}
              </template>
            </el-table-column>
            <el-table-column label="单价" width="80">
              <template #default="{ row: item }: { row: OrderItem }">¥{{ Number(item.unit_price).toFixed(2) }}</template>
            </el-table-column>
            <el-table-column label="数量" width="60" prop="quantity" />
            <el-table-column label="小计" width="90">
              <template #default="{ row: item }: { row: OrderItem }">¥{{ Number(item.subtotal).toFixed(2) }}</template>
            </el-table-column>
          </el-table>
        </div>
      </template>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.page-root { max-width: 1400px; margin: 0 auto; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }
.page-title { font-size: 22px; font-weight: 700; color: #1a1a2e; margin: 0 0 4px 0; }
.page-subtitle { font-size: 13px; color: #909399; margin: 0; }

.stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 20px; }
.stat-card { background: #fff; border-radius: 14px; padding: 20px 24px; display: flex; align-items: center; gap: 16px; box-shadow: 0 2px 12px rgba(0,0,0,0.04); }
.stat-icon { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.stat-body { display: flex; flex-direction: column; min-width: 0; }
.stat-num { font-size: 24px; font-weight: 700; color: #303133; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.stat-label { font-size: 13px; color: #909399; margin-top: 2px; }

.toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 8px; }
.filter-group { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.search-input { width: 200px; }
.filter-select { width: 120px; }
.date-picker { width: 240px; }

.table-card { background: #fff; border-radius: 16px; padding: 4px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); overflow: hidden; }

:deep(.el-table) { --el-table-border-color: transparent; font-size: 14px; }
:deep(.el-table th.el-table__cell) { background: #fafafa; color: #606266; font-weight: 600; height: 48px; }
:deep(.el-table .el-table__row:hover > td) { background-color: #f5f7fa !important; }

/* ========== 移动端适配 ========== */
@media (max-width: 767px) {
  .page-header { flex-direction: column; gap: 12px; }
  .page-header .el-button { width: 100%; }
  .page-title { font-size: 18px; }

  .stats-row { grid-template-columns: repeat(2, 1fr); gap: 10px; }
  .stat-card { padding: 12px 16px; gap: 10px; }
  .stat-icon { width: 40px; height: 40px; }
  .stat-num { font-size: 16px; }

  .toolbar { flex-direction: column; gap: 12px; }
  .filter-group { width: 100%; }
  .search-input { width: 100%; }
  .filter-select { width: 100%; }
  .date-picker { width: 100%; }

  .table-card { overflow-x: auto; -webkit-overflow-scrolling: touch; }
}

@media (max-width: 480px) {
  .stats-row { grid-template-columns: 1fr; }
}
</style>

<script setup lang="ts">
// views/DashboardPage.vue — 数据工作台
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart } from 'echarts/charts'
import {
  TitleComponent, TooltipComponent, LegendComponent, GridComponent,
} from 'echarts/components'
import {
  Coin, Document, Money, WarningFilled, Goods, Scissor, RefreshRight,
} from '@element-plus/icons-vue'
import { dashboardApi, type DashboardData } from '@/api/dashboard'
import { useStoreStore } from '@/stores/store'
import { useUserStore } from '@/stores/user'

use([CanvasRenderer, LineChart, BarChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent])

const router = useRouter()
const storeStore = useStoreStore()
const userStore = useUserStore()
const isAdmin = computed(() => userStore.user?.role === 'admin')

const data = ref<DashboardData | null>(null)
const isLoading = ref(false)

const fetchData = async () => {
  isLoading.value = true
  try {
    const storeId = storeStore.currentStoreId ?? undefined
    const res = await dashboardApi.getSummary(storeId)
    data.value = res.data
  } catch {
    ElMessage.error('获取数据面板失败')
  } finally { isLoading.value = false }
}

onMounted(fetchData)

// 监听门店切换
watch(() => storeStore.currentStoreId, () => { fetchData() })

// ========== 图表配置 ==========
const trendOption = computed(() => {
  if (!data.value) return {}
  const trend = data.value.daily_trend
  return {
    tooltip: { trigger: 'axis' },
    legend: { data: ['订单数', '营收(¥)'], bottom: 0 },
    grid: { left: 10, right: 50, top: 10, bottom: 30 },
    xAxis: { type: 'category', data: trend.map(t => t.date), axisLabel: { fontSize: 11 } },
    yAxis: [
      { type: 'value', name: '订单数', min: 0, splitLine: { show: false }, axisLabel: { fontSize: 11 } },
      { type: 'value', name: '营收(¥)', min: 0, splitLine: { show: false }, axisLabel: { fontSize: 11, formatter: (v: number) => `¥${v}` } },
    ],
    series: [
      { name: '订单数', type: 'bar', data: trend.map(t => t.order_count), barWidth: 14, itemStyle: { borderRadius: [4, 4, 0, 0], color: '#409eff' } },
      { name: '营收(¥)', type: 'line', yAxisIndex: 1, data: trend.map(t => t.revenue), smooth: true, lineStyle: { color: '#67c23a', width: 2 }, itemStyle: { color: '#67c23a' }, symbol: 'circle', symbolSize: 6 },
    ],
  }
})

const statusLabelMap: Record<string, string> = {
  pending: '待支付', paid: '已支付', completed: '已完成', cancelled: '已取消', refunded: '已退款',
}
const statusTagMap: Record<string, string> = {
  pending: 'warning', paid: 'info', completed: 'success', cancelled: '', refunded: 'danger',
}

const formatAmount = (v: number) => `¥${v.toFixed(2)}`
</script>

<template>
  <div class="page-root">
    <div class="page-header">
      <div>
        <h2 class="page-title">数据工作台</h2>
        <p class="page-subtitle">{{ storeStore.currentStoreName || '全部门店' }} · 经营数据概览</p>
      </div>
      <el-button :icon="RefreshRight" @click="fetchData" :loading="isLoading">刷新数据</el-button>
    </div>

    <div class="page-body" v-loading="isLoading">
      <!-- 统计卡片 -->
      <div class="stats-row">
        <div class="stat-card">
          <div class="stat-icon" style="background:#ecf5ff;color:#409eff"><el-icon :size="22"><Coin /></el-icon></div>
          <div class="stat-body">
            <span class="stat-num">{{ formatAmount(data?.today_revenue || 0) }}</span>
            <span class="stat-label">今日营收</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background:#f0f9eb;color:#67c23a"><el-icon :size="22"><Document /></el-icon></div>
          <div class="stat-body">
            <span class="stat-num">{{ data?.today_orders || 0 }}</span>
            <span class="stat-label">今日订单</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background:#fdf6ec;color:#e6a23c"><el-icon :size="22"><Money /></el-icon></div>
          <div class="stat-body">
            <span class="stat-num">{{ formatAmount(data?.month_revenue || 0) }}</span>
            <span class="stat-label">本月营收</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon" style="background:#fef0f0;color:#f56c6c"><el-icon :size="22"><WarningFilled /></el-icon></div>
          <div class="stat-body">
            <span class="stat-num">{{ data?.pending_orders || 0 }}</span>
            <span class="stat-label">待处理订单</span>
          </div>
        </div>
      </div>

      <!-- 趋势图 + 低库存预警 -->
      <div class="content-row">
        <div class="card panel-chart">
          <h4 class="card-title">近7天趋势</h4>
          <v-chart :option="trendOption" style="height:260px" autoresize />
        </div>
        <div class="card panel-alerts">
          <h4 class="card-title">
            低库存预警
            <el-tag v-if="(data?.inventory_alerts?.length || 0) > 0" type="danger" size="small" style="margin-left:8px">{{ data?.inventory_alerts?.length || 0 }}项</el-tag>
          </h4>
          <div v-if="!data?.inventory_alerts?.length" class="empty-hint">暂无预警，库存充足</div>
          <div v-else class="alert-list">
            <div v-for="item in data.inventory_alerts" :key="item.id" class="alert-item">
              <div class="alert-name">{{ item.name }}</div>
              <div class="alert-meta">
                <span style="color:#f56c6c;font-weight:600">{{ item.quantity }}</span>
                <span style="color:#909399"> / {{ item.safety_stock }}{{ item.unit }}</span>
                <span style="color:#909399;margin-left:8px;font-size:12px">SKU: {{ item.sku }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 热门商品/服务 -->
      <div class="content-row">
        <div class="card panel-top">
          <h4 class="card-title"><el-icon :size="14"><Goods /></el-icon> 热门商品 Top 5</h4>
          <div v-if="!data?.top_products?.length" class="empty-hint">暂无数据</div>
          <div v-else class="top-list">
            <div v-for="(item, idx) in data.top_products" :key="item.id" class="top-item">
              <span class="top-rank" :class="'rank-' + (idx + 1)">{{ idx + 1 }}</span>
              <div class="top-info">
                <span class="top-name">{{ item.name }}</span>
                <span class="top-meta">{{ item.count }}笔 · {{ formatAmount(item.revenue) }}</span>
              </div>
            </div>
          </div>
        </div>
        <div class="card panel-top">
          <h4 class="card-title"><el-icon :size="14"><Scissor /></el-icon> 热门服务 Top 5</h4>
          <div v-if="!data?.top_services?.length" class="empty-hint">暂无数据</div>
          <div v-else class="top-list">
            <div v-for="(item, idx) in data.top_services" :key="item.id" class="top-item">
              <span class="top-rank" :class="'rank-' + (idx + 1)">{{ idx + 1 }}</span>
              <div class="top-info">
                <span class="top-name">{{ item.name }}</span>
                <span class="top-meta">{{ item.count }}笔 · {{ formatAmount(item.revenue) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 最近订单 -->
      <div class="card">
        <h4 class="card-title">最近订单</h4>
        <div v-if="!data?.recent_orders?.length" class="empty-hint">暂无订单</div>
        <el-table v-else :data="data.recent_orders" size="small" stripe>
          <el-table-column label="订单号" width="180">
            <template #default="{ row }">
              <span style="font-weight:600;font-size:13px">{{ row.order_no }}</span>
            </template>
          </el-table-column>
          <el-table-column label="类型" width="60">
            <template #default="{ row }">
              <el-tag :type="row.order_type === 'sale' ? 'success' : 'warning'" size="small">
                {{ row.order_type === 'sale' ? '销售' : '服务' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="客户" min-width="100">
            <template #default="{ row }">{{ row.customer_name || '散客' }}</template>
          </el-table-column>
          <el-table-column label="金额" width="100">
            <template #default="{ row }">¥{{ Number(row.final_amount).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="statusTagMap[row.status] || ''" size="small">{{ statusLabelMap[row.status] || row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="时间" width="110">
            <template #default="{ row }">{{ row.created_at }}</template>
          </el-table-column>
          <el-table-column label="操作" width="80">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="router.push('/orders')">查看</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-root { max-width: 1400px; margin: 0 auto; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }
.page-title { font-size: 22px; font-weight: 700; color: #1a1a2e; margin: 0 0 4px 0; }
.page-subtitle { font-size: 13px; color: #909399; margin: 0; }

/* 统计卡片 */
.stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 20px; }
.stat-card { background: #fff; border-radius: 14px; padding: 20px 24px; display: flex; align-items: center; gap: 16px; box-shadow: 0 2px 12px rgba(0,0,0,0.04); }
.stat-icon { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.stat-body { display: flex; flex-direction: column; min-width: 0; }
.stat-num { font-size: 24px; font-weight: 700; color: #303133; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.stat-label { font-size: 13px; color: #909399; margin-top: 2px; }

/* 内容行 */
.content-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 16px; }

.card { background: #fff; border-radius: 14px; padding: 20px 24px; box-shadow: 0 2px 12px rgba(0,0,0,0.04); }
.card-title { font-size: 15px; font-weight: 600; color: #303133; margin: 0 0 14px 0; display: flex; align-items: center; gap: 6px; }

.empty-hint { color: #909399; font-size: 13px; text-align: center; padding: 24px 0; }

/* 低库存 */
.alert-list { display: flex; flex-direction: column; gap: 10px; }
.alert-item { padding: 10px 12px; background: #fef0f0; border-radius: 8px; }
.alert-name { font-size: 14px; font-weight: 500; color: #303133; margin-bottom: 4px; }
.alert-meta { font-size: 13px; }

/* 热门排行 */
.top-list { display: flex; flex-direction: column; gap: 8px; }
.top-item { display: flex; align-items: center; gap: 12px; padding: 8px 0; border-bottom: 1px solid #f5f5f5; }
.top-item:last-child { border-bottom: none; }
.top-rank { width: 24px; height: 24px; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; color: #fff; background: #909399; flex-shrink: 0; }
.top-rank.rank-1 { background: #f56c6c; }
.top-rank.rank-2 { background: #e6a23c; }
.top-rank.rank-3 { background: #409eff; }
.top-info { display: flex; flex-direction: column; min-width: 0; }
.top-name { font-size: 14px; color: #303133; font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.top-meta { font-size: 12px; color: #909399; }

:deep(.el-table) { --el-table-border-color: transparent; font-size: 14px; }
:deep(.el-table th.el-table__cell) { background: #fafafa; color: #606266; font-weight: 600; }

/* ========== 移动端适配 ========== */
@media (max-width: 767px) {
  .page-header { flex-direction: column; gap: 12px; }
  .page-header .el-button { width: 100%; }
  .page-title { font-size: 18px; }

  .stats-row { grid-template-columns: repeat(2, 1fr); gap: 10px; }
  .stat-card { padding: 12px 16px; gap: 10px; }
  .stat-icon { width: 40px; height: 40px; }
  .stat-num { font-size: 18px; }

  .content-row { grid-template-columns: 1fr; }

  .card { padding: 14px 16px; }

  :deep(.el-table) { font-size: 12px; }
}
</style>

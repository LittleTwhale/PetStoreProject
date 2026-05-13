<script setup lang="ts">
// views/InventoryLogPage.vue — 库存流水明细
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Document } from '@element-plus/icons-vue'
import { inventoryApi, type InventoryLog, type InventoryItem } from '@/api/inventory'
import { useStoreStore } from '@/stores/store'

const storeStore = useStoreStore()

// ========== 数据 ==========
const logs = ref<InventoryLog[]>([])
const items = ref<InventoryItem[]>([])
const isLoading = ref(false)

const filterItemId = ref<number | null>(null)
const filterChangeType = ref<string | null>(null)
const filterStartTime = ref('')
const filterEndTime = ref('')

// ========== 变动类型标签 ==========
const changeTypeTag = (type: string) => {
  const map: Record<string, string> = {
    in: 'success',
    out: 'danger',
    adjust: 'warning',
  }
  return map[type] || 'info'
}

const changeTypeLabel = (type: string) => {
  const map: Record<string, string> = {
    in: '入库',
    out: '出库',
    adjust: '盘点调整',
  }
  return map[type] || type
}

// ========== 加载 ==========
const fetchLogs = async () => {
  isLoading.value = true
  try {
    const res = await inventoryApi.getLogs({
      limit: 200,
      store_id: storeStore.currentStoreId ?? undefined,
      item_id: filterItemId.value ?? undefined,
      change_type: filterChangeType.value ?? undefined,
      start_time: filterStartTime.value ? new Date(filterStartTime.value).toISOString() : undefined,
      end_time: filterEndTime.value ? new Date(filterEndTime.value + 'T23:59:59').toISOString() : undefined,
    })
    logs.value = res.data
  } catch {
    ElMessage.error('获取流水记录失败')
  } finally {
    isLoading.value = false
  }
}

const fetchItems = async () => {
  try {
    const res = await inventoryApi.listItems({ limit: 500, store_id: storeStore.currentStoreId ?? undefined })
    items.value = res.data
  } catch { /* ignore */ }
}

onMounted(() => { fetchLogs(); fetchItems() })
</script>

<template>
  <div class="page-root">
    <div class="page-header">
      <div>
        <h2 class="page-title">库存流水明细</h2>
        <p class="page-subtitle">查看所有库存变动记录（入库/出库/盘点调整）</p>
      </div>
      <el-button @click="fetchLogs">刷新数据</el-button>
    </div>

    <!-- 筛选 -->
    <div class="toolbar">
      <div class="filter-group">
        <el-select v-model="filterItemId" placeholder="选择物品" clearable class="filter-select" @change="fetchLogs">
          <el-option v-for="it in items" :key="it.id" :label="`${it.name} (${it.sku})`" :value="it.id" />
        </el-select>
        <el-select v-model="filterChangeType" placeholder="变动类型" clearable style="width:130px" @change="fetchLogs">
          <el-option label="入库" value="in" />
          <el-option label="出库" value="out" />
          <el-option label="盘点调整" value="adjust" />
        </el-select>
        <el-date-picker v-model="filterStartTime" type="date" placeholder="开始日期" value-format="YYYY-MM-DD" style="width:150px" @change="fetchLogs" />
        <el-date-picker v-model="filterEndTime" type="date" placeholder="结束日期" value-format="YYYY-MM-DD" style="width:150px" @change="fetchLogs" />
      </div>
    </div>

    <!-- 表格 -->
    <div class="table-card">
      <el-table :data="logs" v-loading="isLoading" stripe style="width:100%"
        :default-sort="{ prop: 'created_at', order: 'descending' }">
        <el-table-column label="时间" width="170" sortable prop="created_at">
          <template #default="{ row }">
            {{ new Date(row.created_at).toLocaleString('zh-CN') }}
          </template>
        </el-table-column>
        <el-table-column label="物品" min-width="160">
          <template #default="{ row }">
            <div class="item-cell">
              <el-icon :size="16"><Document /></el-icon>
              <div>
                <span class="item-name">{{ row.item_name || '已删除' }}</span>
                <span class="item-sku">{{ row.item_sku || '' }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="变动类型" width="110">
          <template #default="{ row }">
            <el-tag :type="changeTypeTag(row.change_type)" size="small" round>
              {{ changeTypeLabel(row.change_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="变动数量" width="100" sortable prop="quantity_change">
          <template #default="{ row }">
            <span
              :style="{ color: row.change_type === 'out' ? '#f56c6c' : row.change_type === 'in' ? '#67c23a' : '#e6a23c', fontWeight: 600 }"
            >
              {{ row.quantity_change >= 0 ? '+' : '' }}{{ row.quantity_change }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="变动后库存" width="110" sortable prop="quantity_after">
          <template #default="{ row }">
            <span style="font-weight:600">{{ row.quantity_after }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作人" width="80">
          <template #default="{ row }">
            {{ row.operator_id || '系统' }}
          </template>
        </el-table-column>
        <el-table-column label="备注" min-width="150" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.remark || '—' }}
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<style scoped>
.page-root { max-width: 1200px; margin: 0 auto; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }
.page-title { font-size: 22px; font-weight: 700; color: #1a1a2e; margin: 0 0 4px 0; }
.page-subtitle { font-size: 13px; color: #909399; margin: 0; }

.toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.filter-group { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.filter-select { width: 220px; }

.table-card { background: #fff; border-radius: 16px; padding: 4px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); overflow: hidden; }

.item-cell { display: flex; align-items: center; gap: 8px; }
.item-name { font-weight: 600; color: #303133; font-size: 14px; }
.item-sku { font-size: 12px; color: #909399; margin-left: 4px; }

:deep(.el-table) { --el-table-border-color: transparent; font-size: 14px; }
:deep(.el-table th.el-table__cell) { background: #fafafa; color: #606266; font-weight: 600; height: 48px; }
:deep(.el-table .el-table__row:hover > td) { background-color: #f5f7fa !important; }
</style>

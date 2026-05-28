<script setup lang="ts">
// views/InventoryItemPage.vue — 库存物品管理
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import {
  Plus, Search, EditPen, Delete, Goods, WarningFilled, Coin,
} from '@element-plus/icons-vue'
import { inventoryApi, type InventoryItem, type InventoryCategory } from '@/api/inventory'
import { useStoreStore } from '@/stores/store'

const storeStore = useStoreStore()

// ========== 数据 ==========
const items = ref<InventoryItem[]>([])
const categories = ref<InventoryCategory[]>([])
const isLoading = ref(false)
const searchText = ref('')
const filterCategoryId = ref<number | null>(null)
const lowStockOnly = ref(false)

// ========== 统计 ==========
const totalItems = computed(() => items.value.length)
const totalValue = computed(() =>
  items.value.reduce((sum, i) => sum + i.quantity * (i.selling_price || 0), 0),
)
const lowStockCount = computed(() =>
  items.value.filter(i => i.quantity <= i.safety_stock && i.safety_stock > 0).length,
)

// ========== 创建弹窗 ==========
const createDialogVisible = ref(false)
const createFormRef = ref<FormInstance>()
const createLoading = ref(false)
const createForm = reactive({
  name: '', sku: '', category_id: null as number | null,
  unit: '个', safety_stock: 0, unit_price: null as number | null,
  selling_price: null as number | null, supplier: '',
})
const createRules: FormRules = {
  name: [{ required: true, message: '请输入物品名称', trigger: 'blur' }],
  sku: [{ required: true, message: '请输入SKU编码', trigger: 'blur' }],
  category_id: [{ required: true, message: '请选择分类', trigger: 'change' }],
}

// ========== 编辑弹窗 ==========
const editDialogVisible = ref(false)
const editFormRef = ref<FormInstance>()
const editLoading = ref(false)
const editingId = ref<number | null>(null)
const editForm = reactive({
  name: '', sku: '', category_id: null as number | null,
  unit: '', safety_stock: 0, unit_price: null as number | null,
  selling_price: null as number | null, supplier: '',
})

// ========== 入库弹窗 ==========
const stockInVisible = ref(false)
const stockInItem = ref<InventoryItem | null>(null)
const stockInQuantity = ref(0)
const stockInPrice = ref<number | null>(null)
const stockInRemark = ref('')
const stockInLoading = ref(false)

// ========== 出库弹窗 ==========
const stockOutVisible = ref(false)
const stockOutItem = ref<InventoryItem | null>(null)
const stockOutQuantity = ref(0)
const stockOutRemark = ref('')
const stockOutLoading = ref(false)

// ========== 加载 ==========
const fetchItems = async () => {
  isLoading.value = true
  try {
    const res = await inventoryApi.listItems({
      limit: 500,
      store_id: storeStore.currentStoreId ?? undefined,
      category_id: filterCategoryId.value ?? undefined,
      search: searchText.value || undefined,
      low_stock_only: lowStockOnly.value || undefined,
    })
    items.value = res.data
  } catch {
    ElMessage.error('获取物品列表失败')
  } finally {
    isLoading.value = false
  }
}

const fetchCategories = async () => {
  try {
    const res = await inventoryApi.listCategories({ limit: 500 })
    categories.value = res.data
  } catch { /* ignore */ }
}

onMounted(() => { fetchItems(); fetchCategories() })

// 监听门店切换自动刷新列表
watch(() => storeStore.currentStoreId, () => { fetchItems(); fetchCategories() })

// 表格行样式：低库存高亮
const tableRowClass = ({ row }: { row: InventoryItem }) =>
  row.safety_stock > 0 && row.quantity <= row.safety_stock ? 'low-stock-row' : ''

// ========== 创建 ==========
const resetCreateForm = () => {
  createForm.name = ''; createForm.sku = ''; createForm.category_id = null
  createForm.unit = '个'; createForm.safety_stock = 0
  createForm.unit_price = null; createForm.selling_price = null; createForm.supplier = ''
}

const handleCreate = async () => {
  if (!createFormRef.value) return
  const valid = await createFormRef.value.validate().catch(() => false)
  if (!valid) return
  if (!storeStore.currentStoreId) { ElMessage.warning('请先选择门店'); return }

  createLoading.value = true
  try {
    await inventoryApi.createItem({
      name: createForm.name, sku: createForm.sku,
      category_id: createForm.category_id!, store_id: storeStore.currentStoreId,
      unit: createForm.unit, safety_stock: createForm.safety_stock,
      unit_price: createForm.unit_price ?? undefined,
      selling_price: createForm.selling_price ?? undefined,
      supplier: createForm.supplier || undefined,
    })
    ElMessage.success('物品创建成功')
    createDialogVisible.value = false; resetCreateForm()
    await fetchItems()
  } catch (err: unknown) {
    ElMessage.error(
      (err as { response?: { data?: { detail?: string } } }).response?.data?.detail || '创建失败',
    )
  } finally { createLoading.value = false }
}

// ========== 编辑 ==========
const openEditDialog = (item: InventoryItem) => {
  editingId.value = item.id
  editForm.name = item.name; editForm.sku = item.sku
  editForm.category_id = item.category_id; editForm.unit = item.unit
  editForm.safety_stock = item.safety_stock
  editForm.unit_price = item.unit_price; editForm.selling_price = item.selling_price
  editForm.supplier = item.supplier || ''
  editDialogVisible.value = true
}

const handleEdit = async () => {
  if (!editFormRef.value || editingId.value === null) return
  editLoading.value = true
  try {
    await inventoryApi.updateItem(editingId.value, {
      name: editForm.name || undefined, sku: editForm.sku || undefined,
      category_id: editForm.category_id ?? undefined,
      unit: editForm.unit || undefined, safety_stock: editForm.safety_stock,
      unit_price: editForm.unit_price ?? undefined,
      selling_price: editForm.selling_price ?? undefined,
      supplier: editForm.supplier || undefined,
    })
    ElMessage.success('物品已更新')
    editDialogVisible.value = false
    await fetchItems()
  } catch (err: unknown) {
    ElMessage.error(
      (err as { response?: { data?: { detail?: string } } }).response?.data?.detail || '更新失败',
    )
  } finally { editLoading.value = false }
}

// ========== 入库 ==========
const openStockIn = (item: InventoryItem) => {
  stockInItem.value = item
  stockInQuantity.value = 0
  stockInPrice.value = null
  stockInRemark.value = ''
  stockInVisible.value = true
}

const handleStockIn = async () => {
  if (!stockInItem.value || stockInQuantity.value <= 0) {
    ElMessage.warning('请输入有效的入库数量'); return
  }
  stockInLoading.value = true
  try {
    await inventoryApi.stockIn({
      item_id: stockInItem.value.id,
      quantity: stockInQuantity.value,
      unit_price: stockInPrice.value ?? undefined,
      remark: stockInRemark.value || undefined,
    })
    ElMessage.success(`入库成功，当前库存: ${stockInItem.value.quantity + stockInQuantity.value}`)
    stockInVisible.value = false
    await fetchItems()
  } catch (err: unknown) {
    ElMessage.error(
      (err as { response?: { data?: { detail?: string } } }).response?.data?.detail || '入库失败',
    )
  } finally { stockInLoading.value = false }
}

// ========== 出库 ==========
const openStockOut = (item: InventoryItem) => {
  stockOutItem.value = item
  stockOutQuantity.value = 0
  stockOutRemark.value = ''
  stockOutVisible.value = true
}

const handleStockOut = async () => {
  if (!stockOutItem.value || stockOutQuantity.value <= 0) {
    ElMessage.warning('请输入有效的出库数量'); return
  }
  if (stockOutQuantity.value > stockOutItem.value.quantity) {
    ElMessage.warning(`库存不足，当前库存: ${stockOutItem.value.quantity}`); return
  }
  stockOutLoading.value = true
  try {
    await inventoryApi.stockOut({
      item_id: stockOutItem.value.id,
      quantity: stockOutQuantity.value,
      remark: stockOutRemark.value || undefined,
    })
    ElMessage.success('出库成功')
    stockOutVisible.value = false
    await fetchItems()
  } catch (err: unknown) {
    ElMessage.error(
      (err as { response?: { data?: { detail?: string } } }).response?.data?.detail || '出库失败',
    )
  } finally { stockOutLoading.value = false }
}
</script>

<template>
  <div class="page-root">
    <div class="page-header">
      <div>
        <h2 class="page-title">库存物品管理</h2>
        <p class="page-subtitle">管理库存物品、出入库操作及低库存预警</p>
      </div>
      <el-button type="primary" :icon="Plus" size="large" @click="createDialogVisible = true">
        新增物品
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-icon" style="background:#ecf5ff;color:#409eff"><el-icon :size="22"><Goods /></el-icon></div>
        <div class="stat-body"><span class="stat-num">{{ totalItems }}</span><span class="stat-label">物品总数</span></div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background:#fdf6ec;color:#e6a23c"><el-icon :size="22"><WarningFilled /></el-icon></div>
        <div class="stat-body"><span class="stat-num">{{ lowStockCount }}</span><span class="stat-label">低库存预警</span></div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background:#f0f9eb;color:#67c23a"><el-icon :size="22"><Coin /></el-icon></div>
        <div class="stat-body"><span class="stat-num">¥{{ totalValue.toFixed(0) }}</span><span class="stat-label">库存总价值</span></div>
      </div>
    </div>

    <!-- 筛选 -->
    <div class="toolbar">
      <div class="filter-group">
        <el-input v-model="searchText" placeholder="搜索名称或SKU..." :prefix-icon="Search" clearable class="search-input" @change="fetchItems" />
        <el-select v-model="filterCategoryId" placeholder="分类筛选" clearable class="filter-select" @change="fetchItems">
          <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
        <el-checkbox v-model="lowStockOnly" @change="fetchItems" border>仅低库存</el-checkbox>
      </div>
      <el-button @click="fetchItems">刷新</el-button>
    </div>

    <!-- 表格 -->
    <div class="table-card">
      <el-table :data="items" v-loading="isLoading" stripe style="width:100%" :row-class-name="tableRowClass">
        <el-table-column prop="sku" label="SKU" width="120" />
        <el-table-column label="名称" min-width="140">
          <template #default="{ row }">
            <span style="font-weight:600">{{ row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column label="分类" width="100">
          <template #default="{ row }">{{ row.category_name || '—' }}</template>
        </el-table-column>
        <el-table-column label="库存量" width="100" sortable prop="quantity">
          <template #default="{ row }">
            <span :style="{ color: row.safety_stock > 0 && row.quantity <= row.safety_stock ? '#f56c6c' : '#303133', fontWeight: 600 }">
              {{ row.quantity }} {{ row.unit }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="safety_stock" label="安全库存" width="90" />
        <el-table-column label="进货价" width="100">
          <template #default="{ row }">¥{{ row.unit_price?.toFixed(2) || '—' }}</template>
        </el-table-column>
        <el-table-column label="售价" width="100">
          <template #default="{ row }">¥{{ row.selling_price?.toFixed(2) || '—' }}</template>
        </el-table-column>
        <el-table-column prop="supplier" label="供应商" width="120" show-overflow-tooltip>
          <template #default="{ row }">{{ row.supplier || '—' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button type="success" link :icon="Plus" @click="openStockIn(row)">入库</el-button>
            <el-button type="warning" link :icon="Delete" @click="openStockOut(row)">出库</el-button>
            <el-button type="primary" link :icon="EditPen" @click="openEditDialog(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 创建弹窗 -->
    <el-dialog v-model="createDialogVisible" title="新增库存物品" width="550px" :close-on-click-modal="false" destroy-on-close>
      <el-form ref="createFormRef" :model="createForm" :rules="createRules" label-width="90px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="物品名称" prop="name"><el-input v-model="createForm.name" maxlength="100" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="SKU编码" prop="sku"><el-input v-model="createForm.sku" maxlength="50" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="所属分类" prop="category_id">
              <el-select v-model="createForm.category_id" style="width:100%">
                <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单位"><el-input v-model="createForm.unit" placeholder="个/瓶/袋" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="安全库存"><el-input-number v-model="createForm.safety_stock" :min="0" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="进货价"><el-input-number v-model="createForm.unit_price" :min="0" :precision="2" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="售价"><el-input-number v-model="createForm.selling_price" :min="0" :precision="2" style="width:100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="供应商"><el-input v-model="createForm.supplier" maxlength="100" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="createLoading" @click="handleCreate">确认创建</el-button>
      </template>
    </el-dialog>

    <!-- 编辑弹窗 -->
    <el-dialog v-model="editDialogVisible" title="编辑物品" width="550px" :close-on-click-modal="false" destroy-on-close>
      <el-form ref="editFormRef" :model="editForm" label-width="90px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="物品名称"><el-input v-model="editForm.name" maxlength="100" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="SKU编码"><el-input v-model="editForm.sku" maxlength="50" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="所属分类">
              <el-select v-model="editForm.category_id" style="width:100%">
                <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单位"><el-input v-model="editForm.unit" /></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="安全库存"><el-input-number v-model="editForm.safety_stock" :min="0" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="进货价"><el-input-number v-model="editForm.unit_price" :min="0" :precision="2" style="width:100%" /></el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="售价"><el-input-number v-model="editForm.selling_price" :min="0" :precision="2" style="width:100%" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="供应商"><el-input v-model="editForm.supplier" maxlength="100" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="editLoading" @click="handleEdit">保存修改</el-button>
      </template>
    </el-dialog>

    <!-- 入库弹窗 -->
    <el-dialog v-model="stockInVisible" title="入库操作" width="420px" :close-on-click-modal="false" destroy-on-close>
      <div v-if="stockInItem" class="stock-info">
        <p><strong>物品：</strong>{{ stockInItem.name }}（{{ stockInItem.sku }}）</p>
        <p><strong>当前库存：</strong>{{ stockInItem.quantity }} {{ stockInItem.unit }}</p>
      </div>
      <el-form label-width="80px" style="margin-top:16px">
        <el-form-item label="入库数量">
          <el-input-number v-model="stockInQuantity" :min="0.01" :step="1" style="width:100%" />
        </el-form-item>
        <el-form-item label="进货单价">
          <el-input-number v-model="stockInPrice" :min="0" :precision="2" style="width:100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="stockInRemark" maxlength="255" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="stockInVisible = false">取消</el-button>
        <el-button type="primary" :loading="stockInLoading" @click="handleStockIn">确认入库</el-button>
      </template>
    </el-dialog>

    <!-- 出库弹窗 -->
    <el-dialog v-model="stockOutVisible" title="出库操作" width="420px" :close-on-click-modal="false" destroy-on-close>
      <div v-if="stockOutItem" class="stock-info">
        <p><strong>物品：</strong>{{ stockOutItem.name }}（{{ stockOutItem.sku }}）</p>
        <p><strong>当前库存：</strong>{{ stockOutItem.quantity }} {{ stockOutItem.unit }}</p>
      </div>
      <el-form label-width="80px" style="margin-top:16px">
        <el-form-item label="出库数量">
          <el-input-number v-model="stockOutQuantity" :min="0.01" :max="stockOutItem?.quantity" :step="1" style="width:100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="stockOutRemark" maxlength="255" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="stockOutVisible = false">取消</el-button>
        <el-button type="primary" :loading="stockOutLoading" @click="handleStockOut">确认出库</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.page-root { max-width: 1200px; margin: 0 auto; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }
.page-title { font-size: 22px; font-weight: 700; color: #1a1a2e; margin: 0 0 4px 0; }
.page-subtitle { font-size: 13px; color: #909399; margin: 0; }

.stats-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 20px; }
.stat-card { background: #fff; border-radius: 14px; padding: 20px 24px; display: flex; align-items: center; gap: 16px; box-shadow: 0 2px 12px rgba(0,0,0,0.04); }
.stat-icon { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.stat-body { display: flex; flex-direction: column; }
.stat-num { font-size: 24px; font-weight: 700; color: #303133; }
.stat-label { font-size: 13px; color: #909399; margin-top: 2px; }

.toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.filter-group { display: flex; align-items: center; gap: 12px; }
.search-input { width: 240px; }
.filter-select { width: 160px; }

.table-card { background: #fff; border-radius: 16px; padding: 4px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); overflow: hidden; }

:deep(.low-stock-row) { background-color: #fef0f0 !important; }
:deep(.el-table) { --el-table-border-color: transparent; font-size: 14px; }
:deep(.el-table th.el-table__cell) { background: #fafafa; color: #606266; font-weight: 600; height: 48px; }
:deep(.el-table .el-table__row:hover > td) { background-color: #f5f7fa !important; }

.stock-info { background: #f5f7fa; padding: 12px 16px; border-radius: 8px; }
.stock-info p { margin: 4px 0; font-size: 14px; }

/* ========== 响应式适配 ========== */
@media (max-width: 1024px) {
  .page-root { max-width: 100%; }
  .stats-row { grid-template-columns: repeat(3, 1fr); gap: 12px; }
  .stat-card { padding: 16px; }
  .stat-num { font-size: 20px; }
}

@media (max-width: 767px) {
  .page-header { flex-direction: column; gap: 12px; }
  .page-header .el-button { width: 100%; }
  .page-title { font-size: 20px; }

  .stats-row {
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }

  .stat-card { padding: 12px 16px; gap: 12px; }
  .stat-icon { width: 40px; height: 40px; }
  .stat-num { font-size: 18px; }

  .toolbar {
    flex-direction: column;
    gap: 12px;
  }

  .filter-group {
    flex-wrap: wrap;
    width: 100%;
  }

  .search-input { width: 100%; }
  .filter-select { width: 100%; }

  .filter-group .el-checkbox {
    margin-left: 0;
  }

  .table-card {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
}

@media (max-width: 480px) {
  .stats-row { grid-template-columns: 1fr; }
}
</style>

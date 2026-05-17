<script setup lang="ts">
// views/ServicePage.vue — 服务项目管理
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Plus, Search, EditPen, Delete, Scissor, Coin } from '@element-plus/icons-vue'
import { serviceApi, type Service } from '@/api/service'
import { useUserStore } from '@/stores/user'
import { useStoreStore } from '@/stores/store'

const userStore = useUserStore()
const storeStore = useStoreStore()
const isAdmin = computed(() => userStore.user?.role === 'admin')

// ========== 数据 ==========
const services = ref<Service[]>([])
const isLoading = ref(false)
const searchText = ref('')
const filterCategory = ref<string | null>(null)

const totalCount = computed(() => services.value.length)
const activeCount = computed(() => services.value.filter(s => s.is_active).length)
const groomingCount = computed(() => services.value.filter(s => s.category === 'grooming').length)
const medicalCount = computed(() => services.value.filter(s => s.category === 'medical').length)

// ========== 创建弹窗 ==========
const createDialogVisible = ref(false)
const createFormRef = ref<FormInstance>()
const createLoading = ref(false)
const createForm = reactive({
  name: '', category: 'grooming', price: 0, duration_minutes: 0, description: '',
})
const createRules: FormRules = {
  name: [{ required: true, message: '请输入服务名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择服务分类', trigger: 'change' }],
  price: [{ required: true, message: '请输入价格', trigger: 'blur' }],
}

// ========== 编辑弹窗 ==========
const editDialogVisible = ref(false)
const editFormRef = ref<FormInstance>()
const editLoading = ref(false)
const editingId = ref<number | null>(null)
const editForm = reactive({
  name: '', category: 'grooming', price: 0, duration_minutes: 0, description: '',
})

// ========== 加载 ==========
const fetchServices = async () => {
  isLoading.value = true
  try {
    const res = await serviceApi.list({
      limit: 500,
      store_id: storeStore.currentStoreId ?? undefined,
      category: filterCategory.value ?? undefined,
      search: searchText.value || undefined,
    })
    services.value = res.data
  } catch {
    ElMessage.error('获取服务列表失败')
  } finally { isLoading.value = false }
}

onMounted(() => { fetchServices() })

// 监听门店切换自动刷新
watch(() => storeStore.currentStoreId, () => { fetchServices() })

// ========== 创建 ==========
const resetCreateForm = () => {
  createForm.name = ''; createForm.category = 'grooming'
  createForm.price = 0; createForm.duration_minutes = 0; createForm.description = ''
}

const handleCreate = async () => {
  if (!createFormRef.value) return
  const valid = await createFormRef.value.validate().catch(() => false)
  if (!valid) return
  if (!storeStore.currentStoreId) { ElMessage.warning('请先选择门店'); return }

  createLoading.value = true
  try {
    await serviceApi.create({
      name: createForm.name, category: createForm.category,
      store_id: storeStore.currentStoreId, price: createForm.price,
      duration_minutes: createForm.duration_minutes,
      description: createForm.description || undefined,
    })
    ElMessage.success('服务项目创建成功')
    createDialogVisible.value = false; resetCreateForm()
    await fetchServices()
  } catch (err: unknown) {
    ElMessage.error(
      (err as { response?: { data?: { detail?: string } } }).response?.data?.detail || '创建失败',
    )
  } finally { createLoading.value = false }
}

// ========== 编辑 ==========
const openEditDialog = (item: Service) => {
  editingId.value = item.id
  editForm.name = item.name; editForm.category = item.category
  editForm.price = item.price; editForm.duration_minutes = item.duration_minutes
  editForm.description = item.description || ''
  editDialogVisible.value = true
}

const handleEdit = async () => {
  if (!editFormRef.value || editingId.value === null) return
  editLoading.value = true
  try {
    await serviceApi.update(editingId.value, {
      name: editForm.name || undefined, category: editForm.category,
      price: editForm.price, duration_minutes: editForm.duration_minutes,
      description: editForm.description || undefined,
    })
    ElMessage.success('服务项目已更新')
    editDialogVisible.value = false
    await fetchServices()
  } catch (err: unknown) {
    ElMessage.error(
      (err as { response?: { data?: { detail?: string } } }).response?.data?.detail || '更新失败',
    )
  } finally { editLoading.value = false }
}

// ========== 下架 ==========
const handleDelete = async (item: Service) => {
  try {
    await ElMessageBox.confirm(`确定要下架服务「${item.name}」吗？`, '下架服务',
      { type: 'warning', confirmButtonText: '确认下架' })
    await serviceApi.delete(item.id)
    ElMessage.success('服务已下架')
    await fetchServices()
  } catch { /* 取消 */ }
}

// 分类相关
const categoryLabelMap: Record<string, string> = {
  grooming: '美容', boarding: '寄养', medical: '医疗', training: '训练', other: '其他',
}
const categoryTagMap: Record<string, string> = {
  grooming: 'info', boarding: 'warning', medical: 'danger', training: 'success', other: '',
}
const categoryLabel = (cat: string) => categoryLabelMap[cat] || cat
const categoryTag = (cat: string) => categoryTagMap[cat] || 'info'

// 格式化时长
const formatDuration = (minutes: number) => {
  if (minutes < 60) return `${minutes}分钟`
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  return m > 0 ? `${h}小时${m}分钟` : `${h}小时`
}
</script>

<template>
  <div class="page-root">
    <div class="page-header">
      <div>
        <h2 class="page-title">服务管理</h2>
        <p class="page-subtitle">管理美容、寄养、医疗等服务项目</p>
      </div>
      <el-button v-if="isAdmin" type="primary" :icon="Plus" size="large" @click="createDialogVisible = true">
        新增服务
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-icon" style="background:#ecf5ff;color:#409eff"><el-icon :size="22"><Scissor /></el-icon></div>
        <div class="stat-body"><span class="stat-num">{{ totalCount }}</span><span class="stat-label">服务总数</span></div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background:#f0f9eb;color:#67c23a"><el-icon :size="22"><Scissor /></el-icon></div>
        <div class="stat-body"><span class="stat-num">{{ activeCount }}</span><span class="stat-label">上架服务</span></div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background:#fdf6ec;color:#e6a23c"><el-icon :size="22"><Coin /></el-icon></div>
        <div class="stat-body"><span class="stat-num">{{ groomingCount + medicalCount }}</span><span class="stat-label">美容 + 医疗</span></div>
      </div>
    </div>

    <!-- 筛选 -->
    <div class="toolbar">
      <div class="filter-group">
        <el-input v-model="searchText" placeholder="搜索服务名称..." :prefix-icon="Search" clearable class="search-input" @change="fetchServices" />
        <el-select v-model="filterCategory" placeholder="分类筛选" clearable class="filter-select" @change="fetchServices">
          <el-option v-for="(label, key) in categoryLabelMap" :key="key" :label="label" :value="key" />
        </el-select>
      </div>
      <el-button @click="fetchServices">刷新</el-button>
    </div>

    <!-- 表格 -->
    <div class="table-card">
      <el-table :data="services" v-loading="isLoading" stripe style="width:100%">
        <el-table-column label="名称" min-width="140">
          <template #default="{ row }">
            <span style="font-weight:600">{{ row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column label="分类" width="80">
          <template #default="{ row }">
            <el-tag :type="categoryTag(row.category)" size="small">{{ categoryLabel(row.category) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="价格" width="100">
          <template #default="{ row }">¥{{ Number(row.price).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="时长" width="100">
          <template #default="{ row }">
            {{ row.duration_minutes > 0 ? formatDuration(row.duration_minutes) : '—' }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">{{ row.is_active ? '上架' : '下架' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column v-if="isAdmin" label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link :icon="EditPen" @click="openEditDialog(row)">编辑</el-button>
            <el-button v-if="row.is_active" type="danger" link :icon="Delete" @click="handleDelete(row)">下架</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 创建弹窗 -->
    <el-dialog v-model="createDialogVisible" title="新增服务项目" width="550px" :close-on-click-modal="false" destroy-on-close>
      <el-form ref="createFormRef" :model="createForm" :rules="createRules" label-width="90px">
        <el-row :gutter="16">
          <el-col :span="14">
            <el-form-item label="服务名称" prop="name"><el-input v-model="createForm.name" maxlength="100" /></el-form-item>
          </el-col>
          <el-col :span="10">
            <el-form-item label="服务分类" prop="category">
              <el-select v-model="createForm.category" style="width:100%">
                <el-option v-for="(label, key) in categoryLabelMap" :key="key" :label="label" :value="key" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="价格 (¥)" prop="price">
              <el-input-number v-model="createForm.price" :min="0" :precision="2" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="预计时长">
              <el-input-number v-model="createForm.duration_minutes" :min="0" :step="5" style="width:100%" />
              <span style="margin-left:4px;font-size:12px;color:#909399">分钟</span>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="服务说明">
          <el-input v-model="createForm.description" type="textarea" :rows="3" maxlength="500" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="createLoading" @click="handleCreate">确认创建</el-button>
      </template>
    </el-dialog>

    <!-- 编辑弹窗 -->
    <el-dialog v-model="editDialogVisible" title="编辑服务项目" width="550px" :close-on-click-modal="false" destroy-on-close>
      <el-form ref="editFormRef" :model="editForm" label-width="90px">
        <el-row :gutter="16">
          <el-col :span="14">
            <el-form-item label="服务名称"><el-input v-model="editForm.name" maxlength="100" /></el-form-item>
          </el-col>
          <el-col :span="10">
            <el-form-item label="服务分类">
              <el-select v-model="editForm.category" style="width:100%">
                <el-option v-for="(label, key) in categoryLabelMap" :key="key" :label="label" :value="key" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="价格 (¥)">
              <el-input-number v-model="editForm.price" :min="0" :precision="2" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="预计时长">
              <el-input-number v-model="editForm.duration_minutes" :min="0" :step="5" style="width:100%" />
              <span style="margin-left:4px;font-size:12px;color:#909399">分钟</span>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="服务说明">
          <el-input v-model="editForm.description" type="textarea" :rows="3" maxlength="500" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="editLoading" @click="handleEdit">保存修改</el-button>
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
.filter-select { width: 150px; }

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
  .stat-num { font-size: 18px; }

  .toolbar { flex-direction: column; gap: 12px; }
  .filter-group { flex-wrap: wrap; width: 100%; }
  .search-input { width: 100%; }
  .filter-select { width: 100%; }

  .table-card { overflow-x: auto; -webkit-overflow-scrolling: touch; }
}

@media (max-width: 480px) {
  .stats-row { grid-template-columns: 1fr; }
}
</style>

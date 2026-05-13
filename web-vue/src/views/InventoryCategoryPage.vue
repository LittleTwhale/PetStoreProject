<script setup lang="ts">
// views/InventoryCategoryPage.vue — 库存分类管理（管理员专属）
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Plus, Search, EditPen, Delete, Collection } from '@element-plus/icons-vue'
import { inventoryApi, type InventoryCategory } from '@/api/inventory'
import { useStoreStore } from '@/stores/store'

const storeStore = useStoreStore()

// ========== 数据 ==========
const categories = ref<InventoryCategory[]>([])
const isLoading = ref(false)
const searchText = ref('')

// ========== 创建弹窗 ==========
const createDialogVisible = ref(false)
const createFormRef = ref<FormInstance>()
const createLoading = ref(false)
const createForm = reactive({ name: '', description: '' })

const createRules: FormRules = {
  name: [{ required: true, message: '请输入分类名称', trigger: 'blur' }],
}

// ========== 编辑弹窗 ==========
const editDialogVisible = ref(false)
const editFormRef = ref<FormInstance>()
const editLoading = ref(false)
const editingId = ref<number | null>(null)
const editForm = reactive({ name: '', description: '' })

// ========== 加载 ==========
const fetchCategories = async () => {
  isLoading.value = true
  try {
    const res = await inventoryApi.listCategories({
      limit: 500,
      store_id: storeStore.currentStoreId ?? undefined,
    })
    categories.value = res.data
  } catch {
    ElMessage.error('获取分类列表失败')
  } finally {
    isLoading.value = false
  }
}

onMounted(fetchCategories)

const filteredCategories = computed(() => {
  if (!searchText.value) return categories.value
  const kw = searchText.value.toLowerCase()
  return categories.value.filter(c => c.name.toLowerCase().includes(kw))
})

// ========== 创建 ==========
const handleCreate = async () => {
  if (!createFormRef.value) return
  const valid = await createFormRef.value.validate().catch(() => false)
  if (!valid) return
  if (!storeStore.currentStoreId) { ElMessage.warning('请先选择门店'); return }

  createLoading.value = true
  try {
    await inventoryApi.createCategory({
      name: createForm.name,
      description: createForm.description || undefined,
      store_id: storeStore.currentStoreId,
    })
    ElMessage.success('分类创建成功')
    createDialogVisible.value = false
    createForm.name = ''
    createForm.description = ''
    await fetchCategories()
  } catch (err: unknown) {
    ElMessage.error(
      (err as { response?: { data?: { detail?: string } } }).response?.data?.detail || '创建失败',
    )
  } finally {
    createLoading.value = false
  }
}

// ========== 编辑 ==========
const openEditDialog = (cat: InventoryCategory) => {
  editingId.value = cat.id
  editForm.name = cat.name
  editForm.description = cat.description || ''
  editDialogVisible.value = true
}

const handleEdit = async () => {
  if (!editFormRef.value || editingId.value === null) return
  editLoading.value = true
  try {
    await inventoryApi.updateCategory(editingId.value, {
      name: editForm.name || undefined,
      description: editForm.description || undefined,
    })
    ElMessage.success('分类已更新')
    editDialogVisible.value = false
    await fetchCategories()
  } catch (err: unknown) {
    ElMessage.error(
      (err as { response?: { data?: { detail?: string } } }).response?.data?.detail || '更新失败',
    )
  } finally {
    editLoading.value = false
  }
}

// ========== 删除 ==========
const handleDelete = async (cat: InventoryCategory) => {
  try {
    await ElMessageBox.confirm(
      `确定要停用分类「${cat.name}」吗？`,
      '停用分类',
      { type: 'warning', confirmButtonText: '确认停用' },
    )
    await inventoryApi.deleteCategory(cat.id)
    ElMessage.success('分类已停用')
    await fetchCategories()
  } catch { /* 取消 */ }
}
</script>

<template>
  <div class="page-root">
    <div class="page-header">
      <div>
        <h2 class="page-title">库存分类管理</h2>
        <p class="page-subtitle">管理库存物品的分类体系（如：狗粮、药品、用品）</p>
      </div>
      <el-button type="primary" :icon="Plus" size="large" @click="createDialogVisible = true">
        新增分类
      </el-button>
    </div>

    <div class="toolbar">
      <el-input
        v-model="searchText"
        placeholder="搜索分类名称..."
        :prefix-icon="Search"
        clearable
        class="search-input"
      />
    </div>

    <div class="table-card">
      <el-table
        :data="filteredCategories"
        v-loading="isLoading"
        stripe
        style="width: 100%"
        row-class-name="table-row"
      >
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column label="分类名称" min-width="180">
          <template #default="{ row }">
            <div class="name-cell">
              <el-icon :size="18" color="#409eff"><Collection /></el-icon>
              <span style="font-weight: 600">{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.description || '—' }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small" round>
              {{ row.is_active ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link :icon="EditPen" @click="openEditDialog(row)">编辑</el-button>
            <el-button
              v-if="row.is_active"
              type="danger" link :icon="Delete"
              @click="handleDelete(row)"
            >停用</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 创建弹窗 -->
    <el-dialog v-model="createDialogVisible" title="新增库存分类" width="450px"
      :close-on-click-modal="false" destroy-on-close>
      <el-form ref="createFormRef" :model="createForm" :rules="createRules" label-width="80px">
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="createForm.name" placeholder="如：狗粮" maxlength="50" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="createForm.description" placeholder="分类描述（可选）" maxlength="200" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="createLoading" @click="handleCreate">确认创建</el-button>
      </template>
    </el-dialog>

    <!-- 编辑弹窗 -->
    <el-dialog v-model="editDialogVisible" title="编辑库存分类" width="450px"
      :close-on-click-modal="false" destroy-on-close>
      <el-form ref="editFormRef" :model="editForm" label-width="80px">
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="editForm.name" maxlength="50" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="editForm.description" maxlength="200" />
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
.page-root { max-width: 1120px; margin: 0 auto; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }
.page-title { font-size: 22px; font-weight: 700; color: #1a1a2e; margin: 0 0 4px 0; }
.page-subtitle { font-size: 13px; color: #909399; margin: 0; }
.toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.search-input { width: 340px; }
.table-card { background: #fff; border-radius: 16px; padding: 4px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); overflow: hidden; }
:deep(.table-row) { height: 56px; }
.name-cell { display: flex; align-items: center; gap: 10px; }
:deep(.el-table) { --el-table-border-color: transparent; font-size: 14px; }
:deep(.el-table th.el-table__cell) { background: #fafafa; color: #606266; font-weight: 600; height: 48px; }
:deep(.el-table .el-table__row:hover > td) { background-color: #f5f7fa !important; }

/* ========== 响应式适配 ========== */
@media (max-width: 767px) {
  .page-root { max-width: 100%; }
  .page-header { flex-direction: column; gap: 12px; }
  .page-header .el-button { width: 100%; }
  .page-title { font-size: 20px; }
  .toolbar { flex-direction: column; }
  .search-input { width: 100%; }
  .table-card { overflow-x: auto; -webkit-overflow-scrolling: touch; }
}
</style>

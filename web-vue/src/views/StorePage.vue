<script setup lang="ts">
// views/StorePage.vue — 门店管理页面（管理员专属）
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Plus, Search, EditPen, Delete, Shop, UserFilled } from '@element-plus/icons-vue'
import { storeApi, type Store, type StoreUser } from '@/api/store'

// ========== 数据状态 ==========
const stores = ref<Store[]>([])
const isLoading = ref(false)
const searchText = ref('')

// ========== 创建门店弹窗 ==========
const createDialogVisible = ref(false)
const createFormRef = ref<FormInstance>()
const createLoading = ref(false)

const createForm = reactive({
  name: '',
  code: '',
  address: '',
  phone: '',
  manager_id: null as number | null,
})

const createRules: FormRules = {
  name: [{ required: true, message: '请输入门店名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入门店编码', trigger: 'blur' }],
}

// ========== 编辑门店弹窗 ==========
const editDialogVisible = ref(false)
const editFormRef = ref<FormInstance>()
const editLoading = ref(false)
const editingStoreId = ref<number | null>(null)

const editForm = reactive({
  name: '',
  code: '',
  address: '',
  phone: '',
  manager_id: null as number | null,
})

// ========== 店员管理弹窗 ==========
const userDialogVisible = ref(false)
const userDialogStoreId = ref<number | null>(null)
const userDialogStoreName = ref('')
const storeUsers = ref<StoreUser[]>([])
const usersLoading = ref(false)
const bindUserId = ref<number | null>(null)
const bindLoading = ref(false)

// ========== 数据加载 ==========
const fetchStores = async () => {
  isLoading.value = true
  try {
    const res = await storeApi.list({ limit: 500 })
    stores.value = res.data
  } catch {
    ElMessage.error('获取门店列表失败')
  } finally {
    isLoading.value = false
  }
}

onMounted(fetchStores)

// 搜索过滤
const filteredStores = computed(() => {
  if (!searchText.value) return stores.value
  const kw = searchText.value.toLowerCase()
  return stores.value.filter(
    s => s.name.toLowerCase().includes(kw) || s.code.toLowerCase().includes(kw),
  )
})

// ========== 创建门店 ==========
const resetCreateForm = () => {
  createForm.name = ''
  createForm.code = ''
  createForm.address = ''
  createForm.phone = ''
  createForm.manager_id = null
}

const handleCreate = async () => {
  if (!createFormRef.value) return
  const valid = await createFormRef.value.validate().catch(() => false)
  if (!valid) return

  createLoading.value = true
  try {
    await storeApi.create({
      name: createForm.name,
      code: createForm.code,
      address: createForm.address || undefined,
      phone: createForm.phone || undefined,
      manager_id: createForm.manager_id ?? undefined,
    })
    ElMessage.success('门店创建成功')
    createDialogVisible.value = false
    resetCreateForm()
    await fetchStores()
  } catch (err: unknown) {
    ElMessage.error(
      (err as { response?: { data?: { detail?: string } } }).response?.data?.detail || '创建失败',
    )
  } finally {
    createLoading.value = false
  }
}

// ========== 编辑门店 ==========
const openEditDialog = (store: Store) => {
  editingStoreId.value = store.id
  editForm.name = store.name
  editForm.code = store.code
  editForm.address = store.address || ''
  editForm.phone = store.phone || ''
  editForm.manager_id = store.manager_id
  editDialogVisible.value = true
}

const handleEdit = async () => {
  if (!editFormRef.value || editingStoreId.value === null) return

  editLoading.value = true
  try {
    await storeApi.update(editingStoreId.value, {
      name: editForm.name || undefined,
      code: editForm.code || undefined,
      address: editForm.address || undefined,
      phone: editForm.phone || undefined,
      manager_id: editForm.manager_id ?? undefined,
    })
    ElMessage.success('门店信息已更新')
    editDialogVisible.value = false
    await fetchStores()
  } catch (err: unknown) {
    ElMessage.error(
      (err as { response?: { data?: { detail?: string } } }).response?.data?.detail || '更新失败',
    )
  } finally {
    editLoading.value = false
  }
}

// ========== 停用门店 ==========
const handleDelete = async (store: Store) => {
  try {
    await ElMessageBox.confirm(
      `确定要停用门店「${store.name}」吗？停用后该门店将无法进行业务操作。`,
      '停用门店',
      { type: 'warning', confirmButtonText: '确认停用' },
    )
    await storeApi.delete(store.id)
    ElMessage.success('门店已停用')
    await fetchStores()
  } catch {
    // 取消
  }
}

// ========== 店员管理 ==========
const openUserDialog = async (store: Store) => {
  userDialogStoreId.value = store.id
  userDialogStoreName.value = store.name
  userDialogVisible.value = true
  await fetchStoreUsers()
}

const fetchStoreUsers = async () => {
  if (userDialogStoreId.value === null) return
  usersLoading.value = true
  try {
    const res = await storeApi.getUsers(userDialogStoreId.value)
    storeUsers.value = res.data
  } catch {
    storeUsers.value = []
  } finally {
    usersLoading.value = false
  }
}

const handleBindUser = async () => {
  if (!bindUserId.value || userDialogStoreId.value === null) return
  bindLoading.value = true
  try {
    await storeApi.bindUser(userDialogStoreId.value, { user_id: bindUserId.value })
    ElMessage.success('店员绑定成功')
    bindUserId.value = null
    await fetchStoreUsers()
  } catch (err: unknown) {
    ElMessage.error(
      (err as { response?: { data?: { detail?: string } } }).response?.data?.detail || '绑定失败',
    )
  } finally {
    bindLoading.value = false
  }
}

const handleUnbindUser = async (userId: number) => {
  if (userDialogStoreId.value === null) return
  try {
    await ElMessageBox.confirm('确定要解除该店员与本门店的绑定吗？', '解除绑定', {
      type: 'warning',
      confirmButtonText: '确认解除',
    })
    await storeApi.unbindUser(userDialogStoreId.value, userId)
    ElMessage.success('已解除绑定')
    await fetchStoreUsers()
  } catch {
    // 取消
  }
}
</script>

<template>
  <div class="store-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div>
        <h2 class="page-title">门店管理</h2>
        <p class="page-subtitle">管理所有分店信息及店员分配</p>
      </div>
      <el-button type="primary" :icon="Plus" size="large" @click="createDialogVisible = true">
        新增门店
      </el-button>
    </div>

    <!-- 搜索 -->
    <div class="toolbar">
      <el-input
        v-model="searchText"
        placeholder="搜索门店名称或编码..."
        :prefix-icon="Search"
        clearable
        class="search-input"
      />
    </div>

    <!-- 门店表格 -->
    <div class="table-card">
      <el-table
        :data="filteredStores"
        v-loading="isLoading"
        stripe
        style="width: 100%"
        :default-sort="{ prop: 'id', order: 'descending' }"
        row-class-name="table-row"
      >
        <el-table-column prop="id" label="ID" width="65" sortable />
        <el-table-column label="门店" min-width="180">
          <template #default="{ row }">
            <div class="store-cell">
              <el-icon :size="20" color="#409eff"><Shop /></el-icon>
              <div class="store-cell-info">
                <span class="store-name">{{ row.name }}</span>
                <span class="store-code">{{ row.code }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="address" label="地址" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.address || '未填写' }}
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="电话" width="140">
          <template #default="{ row }">
            {{ row.phone || '未填写' }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small" round>
              {{ row.is_active ? '营业中' : '已停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link :icon="EditPen" @click="openEditDialog(row)">
              编辑
            </el-button>
            <el-button type="warning" link :icon="UserFilled" @click="openUserDialog(row)">
              店员
            </el-button>
            <el-button
              v-if="row.is_active"
              type="danger"
              link
              :icon="Delete"
              @click="handleDelete(row)"
            >
              停用
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- ========== 创建门店弹窗 ========== -->
    <el-dialog
      v-model="createDialogVisible"
      title="新增门店"
      width="500px"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createRules"
        label-width="90px"
        label-position="left"
      >
        <el-form-item label="门店名称" prop="name">
          <el-input v-model="createForm.name" placeholder="如: 非诚勿宠·XX店" maxlength="100" />
        </el-form-item>
        <el-form-item label="门店编码" prop="code">
          <el-input v-model="createForm.code" placeholder="如: BJ001" maxlength="20" />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="createForm.address" placeholder="详细地址" maxlength="255" />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="createForm.phone" placeholder="门店座机或手机" maxlength="20" />
        </el-form-item>
        <el-form-item label="店长ID">
          <el-input-number v-model="createForm.manager_id" :min="1" placeholder="可选" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="createLoading" @click="handleCreate">
          确认创建
        </el-button>
      </template>
    </el-dialog>

    <!-- ========== 编辑门店弹窗 ========== -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑门店"
      width="500px"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <el-form ref="editFormRef" :model="editForm" label-width="90px" label-position="left">
        <el-form-item label="门店名称" prop="name">
          <el-input v-model="editForm.name" placeholder="门店名称" maxlength="100" />
        </el-form-item>
        <el-form-item label="门店编码" prop="code">
          <el-input v-model="editForm.code" placeholder="门店编码" maxlength="20" />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="editForm.address" placeholder="详细地址" maxlength="255" />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="editForm.phone" placeholder="门店电话" maxlength="20" />
        </el-form-item>
        <el-form-item label="店长ID">
          <el-input-number v-model="editForm.manager_id" :min="1" placeholder="可选" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="editLoading" @click="handleEdit">
          保存修改
        </el-button>
      </template>
    </el-dialog>

    <!-- ========== 店员管理弹窗 ========== -->
    <el-dialog
      v-model="userDialogVisible"
      :title="`店员管理 — ${userDialogStoreName}`"
      width="550px"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <!-- 绑定新店员 -->
      <div class="bind-row">
        <el-input-number
          v-model="bindUserId"
          :min="1"
          placeholder="输入用户ID"
          style="width: 180px"
        />
        <el-button type="primary" :loading="bindLoading" @click="handleBindUser">
          绑定到本店
        </el-button>
      </div>

      <!-- 已绑定店员列表 -->
      <el-table :data="storeUsers" v-loading="usersLoading" stripe style="width: 100%; margin-top: 16px">
        <el-table-column label="用户ID" prop="user_id" width="80" />
        <el-table-column label="昵称" prop="nickname" min-width="120" />
        <el-table-column label="角色" width="90">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : row.role === 'staff' ? 'warning' : ''" size="small">
              {{ row.role === 'admin' ? '管理员' : row.role === 'staff' ? '店员' : '顾客' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="职位" prop="position_desc" min-width="120">
          <template #default="{ row }">
            {{ row.position_desc || '—' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ row }">
            <el-button type="danger" link :icon="Delete" @click="handleUnbindUser(row.user_id)">
              移除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<style scoped>
.store-page {
  max-width: 1120px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.page-title {
  font-size: 22px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 4px 0;
}

.page-subtitle {
  font-size: 13px;
  color: #909399;
  margin: 0;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.search-input {
  width: 340px;
}

.table-card {
  background: #fff;
  border-radius: 16px;
  padding: 4px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

:deep(.table-row) {
  height: 60px;
}

.store-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.store-cell-info {
  display: flex;
  flex-direction: column;
}

.store-name {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}

.store-code {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.bind-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

:deep(.el-table) {
  --el-table-border-color: transparent;
  font-size: 14px;
}

:deep(.el-table th.el-table__cell) {
  background: #fafafa;
  color: #606266;
  font-weight: 600;
  height: 48px;
}

:deep(.el-table .el-table__row:hover > td) {
  background-color: #f5f7fa !important;
}

/* ========== 响应式适配 ========== */
@media (max-width: 767px) {
  .store-page {
    max-width: 100%;
  }

  .page-header {
    flex-direction: column;
    gap: 12px;
  }

  .page-header .el-button {
    width: 100%;
  }

  .page-title {
    font-size: 20px;
  }

  .toolbar {
    flex-direction: column;
  }

  .search-input {
    width: 100%;
  }

  .table-card {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  .bind-row {
    flex-direction: column;
    align-items: stretch;
  }

  .bind-row .el-input-number {
    width: 100% !important;
  }
}
</style>

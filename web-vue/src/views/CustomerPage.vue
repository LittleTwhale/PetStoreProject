<script setup lang="ts">
// views/CustomerPage.vue — 客户档案管理页面
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import {
  Plus,
  Search,
  EditPen,
  Delete,
  UserFilled,
  PhoneFilled,
  Medal,
  Money,
} from '@element-plus/icons-vue'
import { customerApi, type CustomerProfile } from '@/api/customer'
import { useStoreStore } from '@/stores/store'

const storeStore = useStoreStore()

// ========== 数据状态 ==========
const customers = ref<CustomerProfile[]>([])
const isLoading = ref(false)
const searchText = ref('')

// ========== 创建客户弹窗 ==========
const createDialogVisible = ref(false)
const createFormRef = ref<FormInstance>()
const createLoading = ref(false)

const createForm = reactive({
  user_id: null as number | null,
  real_name: '',
  phone: '',
  address: '',
  membership_level: '普通会员',
  points: 0,
  balance: 0,
})

const createRules: FormRules = {
  user_id: [
    { required: true, message: '请输入关联的用户ID', trigger: 'blur' },
  ],
}

// ========== 编辑客户弹窗 ==========
const editDialogVisible = ref(false)
const editFormRef = ref<FormInstance>()
const editLoading = ref(false)
const editingCustomerId = ref<number | null>(null)

const editForm = reactive({
  real_name: '',
  phone: '',
  address: '',
  membership_level: '',
  points: 0,
  balance: 0,
})

// 会员等级选项
const membershipOptions = ['普通会员', '银卡会员', '金卡会员', '钻石会员']

// 等级标签颜色
const membershipTagType = (level: string) => {
  const map: Record<string, string> = {
    '普通会员': '',
    '银卡会员': 'info',
    '金卡会员': 'warning',
    '钻石会员': 'danger',
  }
  return map[level] || ''
}

// ========== 数据加载 ==========
const fetchCustomers = async () => {
  isLoading.value = true
  try {
    const res = await customerApi.list({
      limit: 500,
      store_id: storeStore.currentStoreId ?? undefined,
    })
    customers.value = res.data
  } catch (err: unknown) {
    ElMessage.error(
      (err as { response?: { data?: { detail?: string } } }).response?.data?.detail ||
        '获取客户列表失败',
    )
  } finally {
    isLoading.value = false
  }
}

onMounted(fetchCustomers)

// 搜索过滤
const filteredCustomers = computed(() => {
  if (!searchText.value) return customers.value
  const kw = searchText.value.toLowerCase()
  return customers.value.filter(
    (c) =>
      (c.real_name && c.real_name.toLowerCase().includes(kw)) ||
      (c.phone && c.phone.includes(kw)) ||
      String(c.id).includes(kw),
  )
})

// 统计名下宠物总数
const totalPets = computed(() =>
  filteredCustomers.value.reduce((sum, c) => sum + (c.pets?.length || 0), 0),
)

// ========== 创建客户 ==========
const resetCreateForm = () => {
  createForm.user_id = null
  createForm.real_name = ''
  createForm.phone = ''
  createForm.address = ''
  createForm.membership_level = '普通会员'
  createForm.points = 0
  createForm.balance = 0
}

const handleCreate = async () => {
  if (!createFormRef.value) return
  const valid = await createFormRef.value.validate().catch(() => false)
  if (!valid) return

  createLoading.value = true
  try {
    await customerApi.create({
      user_id: createForm.user_id!,
      real_name: createForm.real_name || undefined,
      phone: createForm.phone || undefined,
      address: createForm.address || undefined,
      membership_level: createForm.membership_level,
      points: createForm.points,
      balance: createForm.balance,
      store_id: storeStore.currentStoreId ?? undefined,
    })
    ElMessage.success('客户档案创建成功')
    createDialogVisible.value = false
    resetCreateForm()
    await fetchCustomers()
  } catch (err: unknown) {
    ElMessage.error(
      (err as { response?: { data?: { detail?: string } } }).response?.data?.detail ||
        '创建失败',
    )
  } finally {
    createLoading.value = false
  }
}

// ========== 编辑客户 ==========
const openEditDialog = (customer: CustomerProfile) => {
  editingCustomerId.value = customer.id
  editForm.real_name = customer.real_name || ''
  editForm.phone = customer.phone || ''
  editForm.address = customer.address || ''
  editForm.membership_level = customer.membership_level || '普通会员'
  editForm.points = customer.points
  editForm.balance = customer.balance
  editDialogVisible.value = true
}

const handleEdit = async () => {
  if (!editFormRef.value || editingCustomerId.value === null) return

  editLoading.value = true
  try {
    await customerApi.update(editingCustomerId.value, {
      real_name: editForm.real_name || undefined,
      phone: editForm.phone || undefined,
      address: editForm.address || undefined,
      membership_level: editForm.membership_level,
      points: editForm.points,
      balance: editForm.balance,
    })
    ElMessage.success('客户档案已更新')
    editDialogVisible.value = false
    await fetchCustomers()
  } catch (err: unknown) {
    ElMessage.error(
      (err as { response?: { data?: { detail?: string } } }).response?.data?.detail ||
        '更新失败',
    )
  } finally {
    editLoading.value = false
  }
}

// ========== 删除客户 ==========
const handleDelete = async (customer: CustomerProfile) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除客户「${customer.real_name || '未实名'}」(ID: ${customer.id}) 吗？其名下宠物将解除归属。`,
      '删除客户档案',
      { type: 'error', confirmButtonText: '确认删除', confirmButtonClass: 'el-button--danger' },
    )
    await customerApi.delete(customer.id)
    ElMessage.success('客户档案已删除')
    await fetchCustomers()
  } catch {
    // 取消操作
  }
}
</script>

<template>
  <div class="customer-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div>
        <h2 class="page-title">客户档案管理</h2>
        <p class="page-subtitle">管理所有客户的业务档案，含名下宠物概览</p>
      </div>
      <el-button type="primary" :icon="Plus" size="large" @click="createDialogVisible = true">
        新建客户档案
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-icon" style="background: #ecf5ff; color: #409eff">
          <el-icon :size="22"><UserFilled /></el-icon>
        </div>
        <div class="stat-body">
          <span class="stat-num">{{ filteredCustomers.length }}</span>
          <span class="stat-label">客户总数</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #fdf6ec; color: #e6a23c">
          <el-icon :size="22"><Medal /></el-icon>
        </div>
        <div class="stat-body">
          <span class="stat-num">{{ filteredCustomers.filter(c => c.membership_level !== '普通会员').length }}</span>
          <span class="stat-label">VIP 客户</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #f0f9eb; color: #67c23a">
          <el-icon :size="22"><Money /></el-icon>
        </div>
        <div class="stat-body">
          <span class="stat-num">{{ totalPets }}</span>
          <span class="stat-label">名下宠物</span>
        </div>
      </div>
    </div>

    <!-- 搜索与过滤 -->
    <div class="toolbar">
      <el-input
        v-model="searchText"
        placeholder="搜索客户姓名、电话或ID..."
        :prefix-icon="Search"
        clearable
        class="search-input"
      />
    </div>

    <!-- 客户表格 -->
    <div class="table-card">
      <el-table
        :data="filteredCustomers"
        v-loading="isLoading"
        stripe
        style="width: 100%"
        :default-sort="{ prop: 'id', order: 'descending' }"
        row-class-name="table-row"
      >
        <el-table-column prop="id" label="ID" width="65" sortable />
        <el-table-column label="客户信息" min-width="180">
          <template #default="{ row }">
            <div class="customer-cell">
              <el-avatar :size="36" :icon="UserFilled" />
              <div class="customer-cell-info">
                <span class="customer-name">{{ row.real_name || '未实名' }}</span>
                <span class="customer-phone">
                  <el-icon :size="12"><PhoneFilled /></el-icon>
                  {{ row.phone || '未填写' }}
                </span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="会员等级" width="120">
          <template #default="{ row }">
            <el-tag :type="membershipTagType(row.membership_level)" size="small" round>
              <el-icon :size="12" style="margin-right: 4px"><Medal /></el-icon>
              {{ row.membership_level }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="points" label="积分" width="80" sortable />
        <el-table-column label="余额" width="110" sortable prop="balance">
          <template #default="{ row }">
            <span style="font-weight: 600; color: #e6a23c">¥{{ row.balance?.toFixed(2) || '0.00' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="名下宠物" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.pets?.length" type="success" size="small" round>
              {{ row.pets.length }} 只
            </el-tag>
            <span v-else style="color: #c0c4cc">—</span>
          </template>
        </el-table-column>
        <el-table-column label="地址" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.address || '未填写' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link :icon="EditPen" @click="openEditDialog(row)">
              编辑
            </el-button>
            <el-button type="danger" link :icon="Delete" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- ========== 创建客户弹窗 ========== -->
    <el-dialog
      v-model="createDialogVisible"
      title="新建客户档案"
      width="520px"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createRules"
        label-width="100px"
        label-position="left"
      >
        <el-form-item label="关联用户ID" prop="user_id">
          <el-input-number
            v-model="createForm.user_id"
            :min="1"
            placeholder="请输入基础用户ID"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="真实姓名">
          <el-input v-model="createForm.real_name" placeholder="客户真实姓名" maxlength="50" />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="createForm.phone" placeholder="手机号或座机" maxlength="20" />
        </el-form-item>
        <el-form-item label="联系地址">
          <el-input v-model="createForm.address" placeholder="寄养接送需要" maxlength="255" />
        </el-form-item>
        <el-form-item label="会员等级">
          <el-select v-model="createForm.membership_level" style="width: 100%">
            <el-option
              v-for="opt in membershipOptions"
              :key="opt"
              :label="opt"
              :value="opt"
            />
          </el-select>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="初始积分">
              <el-input-number v-model="createForm.points" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="初始余额">
              <el-input-number
                v-model="createForm.balance"
                :min="0"
                :precision="2"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="createLoading" @click="handleCreate">
          确认创建
        </el-button>
      </template>
    </el-dialog>

    <!-- ========== 编辑客户弹窗 ========== -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑客户档案"
      width="520px"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        label-width="100px"
        label-position="left"
      >
        <el-form-item label="真实姓名">
          <el-input v-model="editForm.real_name" placeholder="客户真实姓名" maxlength="50" />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="editForm.phone" placeholder="手机号或座机" maxlength="20" />
        </el-form-item>
        <el-form-item label="联系地址">
          <el-input v-model="editForm.address" placeholder="寄养接送需要" maxlength="255" />
        </el-form-item>
        <el-form-item label="会员等级">
          <el-select v-model="editForm.membership_level" style="width: 100%">
            <el-option
              v-for="opt in membershipOptions"
              :key="opt"
              :label="opt"
              :value="opt"
            />
          </el-select>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="积分">
              <el-input-number v-model="editForm.points" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="余额">
              <el-input-number
                v-model="editForm.balance"
                :min="0"
                :precision="2"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="editLoading" @click="handleEdit">
          保存修改
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.customer-page {
  max-width: 1120px;
  margin: 0 auto;
}

/* ========== 页面标题 ========== */
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

/* ========== 统计卡片 ========== */
.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.stat-card {
  background: #fff;
  border-radius: 14px;
  padding: 20px 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  transition: box-shadow 0.3s;
}

.stat-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-body {
  display: flex;
  flex-direction: column;
}

.stat-num {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
}

.stat-label {
  font-size: 13px;
  color: #909399;
  margin-top: 2px;
}

/* ========== 工具栏 ========== */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.search-input {
  width: 340px;
}

/* ========== 表格 ========== */
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

/* 客户列 */
.customer-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.customer-cell-info {
  display: flex;
  flex-direction: column;
}

.customer-name {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}

.customer-phone {
  font-size: 12px;
  color: #909399;
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 2px;
}

/* ========== Element Plus 表格覆盖 ========== */
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
@media (max-width: 1024px) {
  .customer-page {
    max-width: 100%;
  }

  .stats-row {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 767px) {
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

  .stats-row {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .stat-card {
    padding: 16px;
  }

  .stat-num {
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
}

@media (max-width: 480px) {
  .stats-row {
    grid-template-columns: 1fr;
  }
}
</style>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Plus, Search, EditPen, UserFilled } from '@element-plus/icons-vue'
import { adminApi } from '@/api'

interface UserItem {
  id: number
  nickname: string
  avatar: string | null
  role: string
  position_desc: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

const users = ref<UserItem[]>([])
const isLoading = ref(false)
const searchText = ref('')

// ========== 创建用户弹窗 ==========
const createDialogVisible = ref(false)
const createFormRef = ref<FormInstance>()
const createLoading = ref(false)

const createForm = reactive({
  identifier: '',
  password: '',
  nickname: '',
  role: 'customer',
  position_desc: '',
})

const createRules: FormRules = {
  identifier: [
    { required: true, message: '请输入账号', trigger: 'blur' },
    { min: 3, message: '至少3位', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '至少6位', trigger: 'blur' },
  ],
  nickname: [{ required: true, message: '请输入昵称', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
}

// ========== 编辑用户弹窗 ==========
const editDialogVisible = ref(false)
const editFormRef = ref<FormInstance>()
const editLoading = ref(false)
const editingUserId = ref<number | null>(null)

const editForm = reactive({
  nickname: '',
  role: '',
  position_desc: '',
  is_active: true,
})

const resetCreateForm = () => {
  createForm.identifier = ''
  createForm.password = ''
  createForm.nickname = ''
  createForm.role = 'customer'
  createForm.position_desc = ''
}

const roleOptions = [
  { label: '管理员', value: 'admin' },
  { label: '员工', value: 'staff' },
  { label: '会员', value: 'customer' },
]

const roleLabel = (role: string) => {
  const map: Record<string, string> = { admin: '管理员', staff: '员工', customer: '会员' }
  return map[role] || role
}

const roleTagType = (role: string) => {
  const map: Record<string, string> = { admin: 'danger', staff: 'primary', customer: 'success' }
  return map[role] || 'info'
}

// 加载用户列表
const fetchUsers = async () => {
  isLoading.value = true
  try {
    const res = await adminApi.listUsers()
    users.value = res.data
  } catch (err: unknown) {
    ElMessage.error(
      (err as { response?: { data?: { detail?: string } } }).response?.data?.detail ||
        '获取用户列表失败',
    )
  } finally {
    isLoading.value = false
  }
}

onMounted(fetchUsers)

// 搜索过滤
const filteredUsers = computed(() => {
  if (!searchText.value) return users.value
  const kw = searchText.value.toLowerCase()
  return users.value.filter(
    (u) =>
      u.nickname.toLowerCase().includes(kw) ||
      String(u.id).includes(kw) ||
      (u.position_desc && u.position_desc.toLowerCase().includes(kw)),
  )
})

// ========== 创建用户 ==========
const handleCreate = async () => {
  if (!createFormRef.value) return
  const valid = await createFormRef.value.validate().catch(() => false)
  if (!valid) return

  createLoading.value = true
  try {
    await adminApi.createUser({
      identifier: createForm.identifier,
      password: createForm.password,
      nickname: createForm.nickname,
      role: createForm.role,
      position_desc: createForm.position_desc || undefined,
    })
    ElMessage.success('用户创建成功')
    createDialogVisible.value = false
    resetCreateForm()
    await fetchUsers()
  } catch (err: unknown) {
    ElMessage.error(
      (err as { response?: { data?: { detail?: string } } }).response?.data?.detail ||
        '创建失败',
    )
  } finally {
    createLoading.value = false
  }
}

// ========== 编辑用户 ==========
const openEditDialog = (user: UserItem) => {
  editingUserId.value = user.id
  editForm.nickname = user.nickname
  editForm.role = user.role
  editForm.position_desc = user.position_desc || ''
  editForm.is_active = user.is_active
  editDialogVisible.value = true
}

const handleEdit = async () => {
  if (!editFormRef.value || editingUserId.value === null) return
  const valid = await editFormRef.value.validate().catch(() => false)
  if (!valid) return

  editLoading.value = true
  try {
    await adminApi.updateUser(editingUserId.value, {
      nickname: editForm.nickname,
      role: editForm.role,
      position_desc: editForm.position_desc || undefined,
      is_active: editForm.is_active,
    })
    ElMessage.success('用户信息已更新')
    editDialogVisible.value = false
    await fetchUsers()
  } catch (err: unknown) {
    ElMessage.error(
      (err as { response?: { data?: { detail?: string } } }).response?.data?.detail ||
        '更新失败',
    )
  } finally {
    editLoading.value = false
  }
}

// ========== 切换激活状态 ==========
const toggleActive = async (user: UserItem) => {
  const action = user.is_active ? '停用' : '启用'
  try {
    await ElMessageBox.confirm(`确定要${action}用户「${user.nickname}」吗？`, '确认操作', {
      type: 'warning',
    })
    await adminApi.updateUser(user.id, { is_active: !user.is_active })
    ElMessage.success(`已${action}`)
    await fetchUsers()
  } catch {
    // 取消
  }
}
</script>

<template>
  <div class="admin-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div>
        <h2 class="page-title">用户管理</h2>
        <p class="page-subtitle">管理系统中的所有用户账户</p>
      </div>
      <el-button type="primary" :icon="Plus" size="large" @click="createDialogVisible = true">
        创建用户
      </el-button>
    </div>

    <!-- 搜索与统计 -->
    <div class="toolbar">
      <el-input
        v-model="searchText"
        placeholder="搜索用户昵称、ID 或职位..."
        :prefix-icon="Search"
        clearable
        class="search-input"
      />
      <div class="stats">
        <el-tag type="info" round>共 {{ filteredUsers.length }} 位用户</el-tag>
      </div>
    </div>

    <!-- 用户表格 -->
    <div class="table-card">
      <el-table
        :data="filteredUsers"
        v-loading="isLoading"
        stripe
        style="width: 100%"
        :default-sort="{ prop: 'id', order: 'descending' }"
        row-class-name="table-row"
      >
        <el-table-column prop="id" label="ID" width="70" sortable />
        <el-table-column label="用户" min-width="180">
          <template #default="{ row }">
            <div class="user-cell">
              <el-avatar :size="36" :src="row.avatar || undefined">
                <el-icon><UserFilled /></el-icon>
              </el-avatar>
              <div class="user-cell-info">
                <span class="user-cell-name">{{ row.nickname }}</span>
                <span class="user-cell-desc">{{ row.position_desc || '-' }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="roleTagType(row.role)" size="small" round>
              {{ roleLabel(row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-switch
              :model-value="row.is_active"
              :active-value="true"
              :inactive-value="false"
              @change="toggleActive(row)"
              inline-prompt
              active-text="正常"
              inactive-text="停用"
            />
          </template>
        </el-table-column>
        <el-table-column label="注册时间" width="170" sortable prop="created_at">
          <template #default="{ row }">
            {{ new Date(row.created_at).toLocaleString('zh-CN') }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link :icon="EditPen" @click="openEditDialog(row)">
              编辑
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- ========== 创建用户弹窗 ========== -->
    <el-dialog
      v-model="createDialogVisible"
      title="创建新用户"
      width="480px"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createRules"
        label-width="80px"
        label-position="left"
      >
        <el-form-item label="账号" prop="identifier">
          <el-input
            v-model="createForm.identifier"
            placeholder="用户登录账号"
            maxlength="100"
          />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="createForm.password"
            type="password"
            placeholder="至少6位"
            show-password
            maxlength="100"
          />
        </el-form-item>
        <el-form-item label="昵称" prop="nickname">
          <el-input
            v-model="createForm.nickname"
            placeholder="用户显示名称"
            maxlength="50"
          />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="createForm.role" style="width: 100%">
            <el-option
              v-for="opt in roleOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="职位描述">
          <el-input
            v-model="createForm.position_desc"
            placeholder="如：高级宠物美容师"
            maxlength="100"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="createLoading" @click="handleCreate">
          确认创建
        </el-button>
      </template>
    </el-dialog>

    <!-- ========== 编辑用户弹窗 ========== -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑用户"
      width="480px"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        label-width="80px"
        label-position="left"
      >
        <el-form-item
          label="昵称"
          prop="nickname"
          :rules="[{ required: true, message: '昵称不能为空', trigger: 'blur' }]"
        >
          <el-input v-model="editForm.nickname" maxlength="50" />
        </el-form-item>
        <el-form-item
          label="角色"
          prop="role"
          :rules="[{ required: true, message: '请选择角色', trigger: 'change' }]"
        >
          <el-select v-model="editForm.role" style="width: 100%">
            <el-option
              v-for="opt in roleOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="职位描述">
          <el-input
            v-model="editForm.position_desc"
            placeholder="职位或身份描述"
            maxlength="100"
          />
        </el-form-item>
        <el-form-item label="激活状态">
          <el-switch
            v-model="editForm.is_active"
            inline-prompt
            active-text="正常"
            inactive-text="停用"
          />
        </el-form-item>
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
.admin-page {
  max-width: 1040px;
  margin: 0 auto;
}

/* 页面标题 */
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

/* 工具栏 */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  gap: 16px;
}

.search-input {
  width: 300px;
}

/* 表格卡片 */
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

/* 用户列 */
.user-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-cell-info {
  display: flex;
  flex-direction: column;
}

.user-cell-name {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}

.user-cell-desc {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

/* Element Plus 表格优化 */
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
</style>

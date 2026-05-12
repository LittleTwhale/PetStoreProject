<script setup lang="ts">
// views/PetPage.vue — 宠物台账管理页面
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import {
  Plus,
  Search,
  EditPen,
  Delete,
  Medal,
  Money,
} from '@element-plus/icons-vue'
import { petApi, type PetInfo } from '@/api/pet'

// ========== 常量 ==========
const SPECIES_OPTIONS = ['狗', '猫', '兔', '仓鼠', '龙猫', '豚鼠', '鸟', '鱼', '龟', '蛇', '蜥蜴', '其他']
const GENDER_OPTIONS = ['公', '母', '未知']
const OWNERSHIP_TYPES = [
  { label: '客宠 (已售出)', value: 'customer' },
  { label: '待售宠物', value: 'for_sale' },
  { label: '店宠 / 吉祥物', value: 'store_mascot' },
]
const VACCINE_OPTIONS = ['未接种', '部分接种', '已完成', '不详']

// 归属类型标签
const ownershipTagType = (type: string) => {
  const map: Record<string, string> = {
    customer: '',
    for_sale: 'warning',
    store_mascot: 'success',
  }
  return map[type] || 'info'
}

const ownershipLabel = (type: string) => {
  const map: Record<string, string> = {
    customer: '客宠',
    for_sale: '待售',
    store_mascot: '店宠',
  }
  return map[type] || type
}

// ========== 数据状态 ==========
const pets = ref<PetInfo[]>([])
const isLoading = ref(false)
const filterOwnership = ref<string>('')
const filterOwnerId = ref<number | null>(null)
const searchText = ref('')

// ========== 创建宠物弹窗 ==========
const createDialogVisible = ref(false)
const createFormRef = ref<FormInstance>()
const createLoading = ref(false)

const createForm = reactive({
  name: '',
  species: '',
  breed: '',
  gender: '',
  weight: null as number | null,
  birth_date: '',
  is_neutered: false,
  vaccine_status: '',
  avatar: '',
  special_notes: '',
  ownership_type: 'customer',
  price: null as number | null,
  owner_id: null as number | null,
})

const createRules: FormRules = {
  species: [{ required: true, message: '请选择物种', trigger: 'change' }],
}

// 创建时 owner_id 是否必填（客宠时必填）
const createOwnerIdRequired = computed(() => createForm.ownership_type === 'customer')

// ========== 编辑宠物弹窗 ==========
const editDialogVisible = ref(false)
const editFormRef = ref<FormInstance>()
const editLoading = ref(false)
const editingPetId = ref<number | null>(null)

const editForm = reactive({
  name: '',
  species: '',
  breed: '',
  gender: '',
  weight: null as number | null,
  birth_date: '',
  is_neutered: false,
  vaccine_status: '',
  avatar: '',
  special_notes: '',
  ownership_type: '',
  price: null as number | null,
  owner_id: null as number | null,
})

// 编辑时 owner_id 是否必填
const editOwnerIdRequired = computed(() => editForm.ownership_type === 'customer')

// ========== 数据加载 ==========
const fetchPets = async () => {
  isLoading.value = true
  try {
    const params: Record<string, unknown> = { limit: 500 }
    if (filterOwnership.value) params.ownership_type = filterOwnership.value
    if (filterOwnerId.value) params.owner_id = filterOwnerId.value
    const res = await petApi.list(params)
    pets.value = res.data
  } catch (err: unknown) {
    ElMessage.error(
      (err as { response?: { data?: { detail?: string } } }).response?.data?.detail ||
        '获取宠物列表失败',
    )
  } finally {
    isLoading.value = false
  }
}

onMounted(fetchPets)

// 监听过滤条件变化自动刷新
watch([filterOwnership, filterOwnerId], () => {
  fetchPets()
})

// 搜索过滤（前端）
const filteredPets = computed(() => {
  if (!searchText.value) return pets.value
  const kw = searchText.value.toLowerCase()
  return pets.value.filter(
    (p) =>
      (p.name && p.name.toLowerCase().includes(kw)) ||
      p.species.toLowerCase().includes(kw) ||
      (p.breed && p.breed.toLowerCase().includes(kw)) ||
      String(p.id).includes(kw),
  )
})

// 统计
const stats = computed(() => {
  const total = filteredPets.value.length
  const customerPets = filteredPets.value.filter((p) => p.ownership_type === 'customer').length
  const forSale = filteredPets.value.filter((p) => p.ownership_type === 'for_sale').length
  const mascots = filteredPets.value.filter((p) => p.ownership_type === 'store_mascot').length
  return { total, customerPets, forSale, mascots }
})

// ========== 创建宠物 ==========
const resetCreateForm = () => {
  createForm.name = ''
  createForm.species = ''
  createForm.breed = ''
  createForm.gender = ''
  createForm.weight = null
  createForm.birth_date = ''
  createForm.is_neutered = false
  createForm.vaccine_status = ''
  createForm.avatar = ''
  createForm.special_notes = ''
  createForm.ownership_type = 'customer'
  createForm.price = null
  createForm.owner_id = null
}

const handleCreate = async () => {
  if (!createFormRef.value) return
  const valid = await createFormRef.value.validate().catch(() => false)
  if (!valid) return

  // 客宠必须指定 owner_id
  if (createForm.ownership_type === 'customer' && !createForm.owner_id) {
    ElMessage.error('客宠必须指定主人 (owner_id)')
    return
  }

  createLoading.value = true
  try {
    await petApi.create({
      name: createForm.name || undefined,
      species: createForm.species,
      breed: createForm.breed || undefined,
      gender: createForm.gender || undefined,
      weight: createForm.weight ?? undefined,
      birth_date: createForm.birth_date || undefined,
      is_neutered: createForm.is_neutered,
      vaccine_status: createForm.vaccine_status || undefined,
      avatar: createForm.avatar || undefined,
      special_notes: createForm.special_notes || undefined,
      ownership_type: createForm.ownership_type,
      price: createForm.ownership_type === 'for_sale' ? createForm.price : null,
      owner_id: createForm.ownership_type === 'customer' ? createForm.owner_id : null,
    })
    ElMessage.success('宠物档案已录入')
    createDialogVisible.value = false
    resetCreateForm()
    await fetchPets()
  } catch (err: unknown) {
    ElMessage.error(
      (err as { response?: { data?: { detail?: string } } }).response?.data?.detail ||
        '录入失败',
    )
  } finally {
    createLoading.value = false
  }
}

// ========== 编辑宠物 ==========
const openEditDialog = (pet: PetInfo) => {
  editingPetId.value = pet.id
  editForm.name = pet.name || ''
  editForm.species = pet.species
  editForm.breed = pet.breed || ''
  editForm.gender = pet.gender || ''
  editForm.weight = pet.weight
  editForm.birth_date = pet.birth_date || ''
  editForm.is_neutered = pet.is_neutered
  editForm.vaccine_status = pet.vaccine_status || ''
  editForm.avatar = pet.avatar || ''
  editForm.special_notes = pet.special_notes || ''
  editForm.ownership_type = pet.ownership_type
  editForm.price = pet.price
  editForm.owner_id = pet.owner_id
  editDialogVisible.value = true
}

const handleEdit = async () => {
  if (!editFormRef.value || editingPetId.value === null) return

  // 客宠必须指定 owner_id
  if (editForm.ownership_type === 'customer' && !editForm.owner_id) {
    ElMessage.error('客宠必须指定主人 (owner_id)')
    return
  }

  editLoading.value = true
  try {
    await petApi.update(editingPetId.value, {
      name: editForm.name || undefined,
      species: editForm.species || undefined,
      breed: editForm.breed || undefined,
      gender: editForm.gender || undefined,
      weight: editForm.weight ?? undefined,
      birth_date: editForm.birth_date || undefined,
      is_neutered: editForm.is_neutered,
      vaccine_status: editForm.vaccine_status || undefined,
      avatar: editForm.avatar || undefined,
      special_notes: editForm.special_notes || undefined,
      ownership_type: editForm.ownership_type,
      price: editForm.ownership_type === 'for_sale' ? editForm.price : null,
      owner_id: editForm.ownership_type === 'customer' ? editForm.owner_id : null,
    })
    ElMessage.success('宠物档案已更新')
    editDialogVisible.value = false
    await fetchPets()
  } catch (err: unknown) {
    ElMessage.error(
      (err as { response?: { data?: { detail?: string } } }).response?.data?.detail ||
        '更新失败',
    )
  } finally {
    editLoading.value = false
  }
}

// ========== 删除宠物 ==========
const handleDelete = async (pet: PetInfo) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除宠物「${pet.name || '未命名'}」(ID: ${pet.id}) 吗？此操作不可恢复。`,
      '删除宠物档案',
      { type: 'error', confirmButtonText: '确认删除', confirmButtonClass: 'el-button--danger' },
    )
    await petApi.delete(pet.id)
    ElMessage.success('宠物档案已删除')
    await fetchPets()
  } catch {
    // 取消操作
  }
}

// 监听创建时 ownership_type 变化，自动处理价格和 owner_id
watch(() => createForm.ownership_type, (newVal) => {
  if (newVal !== 'for_sale') createForm.price = null
  if (newVal !== 'customer') createForm.owner_id = null
})

// 监听编辑时 ownership_type 变化
watch(() => editForm.ownership_type, (newVal) => {
  if (newVal !== 'for_sale') editForm.price = null
  if (newVal !== 'customer') editForm.owner_id = null
})
</script>

<template>
  <div class="pet-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div>
        <h2 class="page-title">宠物台账管理</h2>
        <p class="page-subtitle">管理店内所有宠物档案：客宠、待售、店宠</p>
      </div>
      <el-button type="primary" :icon="Plus" size="large" @click="createDialogVisible = true">
        录入新宠物
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-card" :class="{ active: filterOwnership === '' }" @click="filterOwnership = ''">
        <div class="stat-icon" style="background: #ecf5ff; color: #409eff">
          <el-icon :size="22"><Medal /></el-icon>
        </div>
        <div class="stat-body">
          <span class="stat-num">{{ stats.total }}</span>
          <span class="stat-label">全部宠物</span>
        </div>
      </div>
      <div class="stat-card" :class="{ active: filterOwnership === 'customer' }" @click="filterOwnership = 'customer'">
        <div class="stat-icon" style="background: #f0f9eb; color: #67c23a">
          <el-icon :size="22"><Medal /></el-icon>
        </div>
        <div class="stat-body">
          <span class="stat-num">{{ stats.customerPets }}</span>
          <span class="stat-label">客宠</span>
        </div>
      </div>
      <div class="stat-card" :class="{ active: filterOwnership === 'for_sale' }" @click="filterOwnership = 'for_sale'">
        <div class="stat-icon" style="background: #fdf6ec; color: #e6a23c">
          <el-icon :size="22"><Money /></el-icon>
        </div>
        <div class="stat-body">
          <span class="stat-num">{{ stats.forSale }}</span>
          <span class="stat-label">待售</span>
        </div>
      </div>
      <div class="stat-card" :class="{ active: filterOwnership === 'store_mascot' }" @click="filterOwnership = 'store_mascot'">
        <div class="stat-icon" style="background: #fef0f0; color: #f56c6c">
          <el-icon :size="22"><Medal /></el-icon>
        </div>
        <div class="stat-body">
          <span class="stat-num">{{ stats.mascots }}</span>
          <span class="stat-label">店宠</span>
        </div>
      </div>
    </div>

    <!-- 过滤与搜索工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-select
          v-model="filterOwnership"
          placeholder="按归属类型过滤"
          clearable
          class="filter-select"
        >
          <el-option
            v-for="opt in OWNERSHIP_TYPES"
            :key="opt.value"
            :label="opt.label"
            :value="opt.value"
          />
        </el-select>
        <el-input-number
          v-model="filterOwnerId"
          placeholder="按主人ID过滤"
          :min="1"
          controls-position="right"
          class="filter-owner"
        />
      </div>
      <el-input
        v-model="searchText"
        placeholder="搜索昵称、物种、品种或ID..."
        :prefix-icon="Search"
        clearable
        class="search-input"
      />
    </div>

    <!-- 宠物表格 -->
    <div class="table-card">
      <el-table
        :data="filteredPets"
        v-loading="isLoading"
        stripe
        style="width: 100%"
        :default-sort="{ prop: 'id', order: 'descending' }"
        row-class-name="table-row"
      >
        <el-table-column prop="id" label="ID" width="60" sortable />
        <el-table-column label="宠物" min-width="180">
          <template #default="{ row }">
            <div class="pet-cell">
              <el-avatar
                :size="36"
                :src="row.avatar || undefined"
                shape="square"
              >
                <el-icon :size="18"><Medal /></el-icon>
              </el-avatar>
              <div class="pet-cell-info">
                <span class="pet-name">{{ row.name || '未命名' }}</span>
                <span class="pet-breed">{{ row.breed || row.species }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="species" label="物种" width="80" />
        <el-table-column label="性别" width="70">
          <template #default="{ row }">
            {{ row.gender || '—' }}
          </template>
        </el-table-column>
        <el-table-column label="体重" width="80">
          <template #default="{ row }">
            {{ row.weight != null ? row.weight + ' kg' : '—' }}
          </template>
        </el-table-column>
        <el-table-column label="归属" width="100">
          <template #default="{ row }">
            <el-tag :type="ownershipTagType(row.ownership_type)" size="small" round>
              {{ ownershipLabel(row.ownership_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="售价" width="100" sortable prop="price">
          <template #default="{ row }">
            <span v-if="row.ownership_type === 'for_sale' && row.price" style="font-weight: 600; color: #e6a23c">
              ¥{{ row.price?.toFixed(2) }}
            </span>
            <span v-else style="color: #c0c4cc">—</span>
          </template>
        </el-table-column>
        <el-table-column label="主人ID" width="80">
          <template #default="{ row }">
            <span v-if="row.owner_id" style="font-family: monospace">{{ row.owner_id }}</span>
            <span v-else style="color: #c0c4cc">—</span>
          </template>
        </el-table-column>
        <el-table-column label="疫苗状态" width="110">
          <template #default="{ row }">
            <el-tag
              v-if="row.vaccine_status"
              :type="row.vaccine_status === '已完成' ? 'success' : row.vaccine_status === '未接种' ? 'danger' : 'warning'"
              size="small"
              round
            >
              {{ row.vaccine_status }}
            </el-tag>
            <span v-else style="color: #c0c4cc">—</span>
          </template>
        </el-table-column>
        <el-table-column label="绝育" width="65">
          <template #default="{ row }">
            <span :style="{ color: row.is_neutered ? '#67c23a' : '#c0c4cc' }">
              {{ row.is_neutered ? '是' : '否' }}
            </span>
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

    <!-- ========== 录入宠物弹窗 ========== -->
    <el-dialog
      v-model="createDialogVisible"
      title="录入新宠物档案"
      width="600px"
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
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="宠物昵称">
              <el-input v-model="createForm.name" placeholder="选填" maxlength="50" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="物种" prop="species">
              <el-select v-model="createForm.species" placeholder="必选" style="width: 100%">
                <el-option
                  v-for="s in SPECIES_OPTIONS"
                  :key="s"
                  :label="s"
                  :value="s"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="品种">
              <el-input v-model="createForm.breed" placeholder="如：金毛、蓝猫" maxlength="50" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="性别">
              <el-select v-model="createForm.gender" placeholder="选填" style="width: 100%" clearable>
                <el-option
                  v-for="g in GENDER_OPTIONS"
                  :key="g"
                  :label="g"
                  :value="g"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="体重(kg)">
              <el-input-number
                v-model="createForm.weight"
                :min="0"
                :precision="2"
                :step="0.1"
                style="width: 100%"
                placeholder="选填"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="出生日期">
              <el-date-picker
                v-model="createForm.birth_date"
                type="date"
                placeholder="选填"
                style="width: 100%"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="疫苗状态">
              <el-select v-model="createForm.vaccine_status" placeholder="选填" style="width: 100%" clearable>
                <el-option
                  v-for="v in VACCINE_OPTIONS"
                  :key="v"
                  :label="v"
                  :value="v"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="是否绝育">
              <el-switch
                v-model="createForm.is_neutered"
                inline-prompt
                active-text="是"
                inactive-text="否"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="归属类型">
          <el-radio-group v-model="createForm.ownership_type">
            <el-radio-button
              v-for="opt in OWNERSHIP_TYPES"
              :key="opt.value"
              :value="opt.value"
            >
              {{ opt.label }}
            </el-radio-button>
          </el-radio-group>
        </el-form-item>

        <!-- 待售时显示售价 -->
        <el-form-item v-if="createForm.ownership_type === 'for_sale'" label="售价">
          <el-input-number
            v-model="createForm.price"
            :min="0"
            :precision="2"
            style="width: 220px"
            placeholder="设置售价"
          />
        </el-form-item>

        <!-- 客宠时显示主人ID -->
        <el-form-item
          v-if="createForm.ownership_type === 'customer'"
          label="主人ID"
          :required="createOwnerIdRequired"
        >
          <el-input-number
            v-model="createForm.owner_id"
            :min="1"
            style="width: 220px"
            placeholder="客户档案ID"
          />
        </el-form-item>

        <el-form-item label="照片URL">
          <el-input v-model="createForm.avatar" placeholder="宠物照片链接（选填）" maxlength="255" />
        </el-form-item>

        <el-form-item label="特殊备注">
          <el-input
            v-model="createForm.special_notes"
            type="textarea"
            :rows="2"
            placeholder="健康、饮食、行为等特殊注意事项"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="createLoading" @click="handleCreate">
          确认录入
        </el-button>
      </template>
    </el-dialog>

    <!-- ========== 编辑宠物弹窗 ========== -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑宠物档案"
      width="600px"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        label-width="90px"
        label-position="left"
      >
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="宠物昵称">
              <el-input v-model="editForm.name" placeholder="选填" maxlength="50" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="物种">
              <el-select v-model="editForm.species" placeholder="物种" style="width: 100%">
                <el-option
                  v-for="s in SPECIES_OPTIONS"
                  :key="s"
                  :label="s"
                  :value="s"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="品种">
              <el-input v-model="editForm.breed" placeholder="品种" maxlength="50" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="性别">
              <el-select v-model="editForm.gender" placeholder="选填" style="width: 100%" clearable>
                <el-option
                  v-for="g in GENDER_OPTIONS"
                  :key="g"
                  :label="g"
                  :value="g"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="体重(kg)">
              <el-input-number
                v-model="editForm.weight"
                :min="0"
                :precision="2"
                :step="0.1"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="出生日期">
              <el-date-picker
                v-model="editForm.birth_date"
                type="date"
                placeholder="选填"
                style="width: 100%"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="疫苗状态">
              <el-select v-model="editForm.vaccine_status" placeholder="选填" style="width: 100%" clearable>
                <el-option
                  v-for="v in VACCINE_OPTIONS"
                  :key="v"
                  :label="v"
                  :value="v"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="是否绝育">
              <el-switch
                v-model="editForm.is_neutered"
                inline-prompt
                active-text="是"
                inactive-text="否"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="归属类型">
          <el-radio-group v-model="editForm.ownership_type">
            <el-radio-button
              v-for="opt in OWNERSHIP_TYPES"
              :key="opt.value"
              :value="opt.value"
            >
              {{ opt.label }}
            </el-radio-button>
          </el-radio-group>
        </el-form-item>

        <!-- 待售时显示售价 -->
        <el-form-item v-if="editForm.ownership_type === 'for_sale'" label="售价">
          <el-input-number
            v-model="editForm.price"
            :min="0"
            :precision="2"
            style="width: 220px"
            placeholder="设置售价"
          />
        </el-form-item>

        <!-- 客宠时显示主人ID -->
        <el-form-item
          v-if="editForm.ownership_type === 'customer'"
          label="主人ID"
          :required="editOwnerIdRequired"
        >
          <el-input-number
            v-model="editForm.owner_id"
            :min="1"
            style="width: 220px"
            placeholder="客户档案ID"
          />
        </el-form-item>

        <el-form-item label="照片URL">
          <el-input v-model="editForm.avatar" placeholder="宠物照片链接" maxlength="255" />
        </el-form-item>

        <el-form-item label="特殊备注">
          <el-input
            v-model="editForm.special_notes"
            type="textarea"
            :rows="2"
            placeholder="健康、饮食、行为等特殊注意事项"
            maxlength="500"
            show-word-limit
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
.pet-page {
  max-width: 1200px;
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
  grid-template-columns: repeat(4, 1fr);
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
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
}

.stat-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.stat-card.active {
  border-color: #409eff;
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.15);
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
  gap: 16px;
}

.toolbar-left {
  display: flex;
  gap: 12px;
  align-items: center;
}

.filter-select {
  width: 180px;
}

.filter-owner {
  width: 160px;
}

.search-input {
  width: 280px;
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

/* 宠物列 */
.pet-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.pet-cell-info {
  display: flex;
  flex-direction: column;
}

.pet-name {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}

.pet-breed {
  font-size: 12px;
  color: #909399;
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
</style>

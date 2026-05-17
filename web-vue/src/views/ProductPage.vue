<script setup lang="ts">
// views/ProductPage.vue — 商品管理
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules, UploadRequestOptions } from 'element-plus'
import { Plus, Search, EditPen, Delete, Goods, Present } from '@element-plus/icons-vue'
import { productApi, type Product } from '@/api/product'
import { petApi, type PetInfo } from '@/api/pet'
import { inventoryApi, type InventoryItem } from '@/api/inventory'
import { useStoreStore } from '@/stores/store'

const storeStore = useStoreStore()

// ========== 数据 ==========
const products = ref<Product[]>([])
const isLoading = ref(false)
const searchText = ref('')
const filterType = ref<string | null>(null)
const petOptions = ref<PetInfo[]>([])
const inventoryOptions = ref<InventoryItem[]>([])

const totalCount = computed(() => products.value.length)
const goodsCount = computed(() => products.value.filter((p) => p.product_type === 'goods').length)
const petCount = computed(() => products.value.filter((p) => p.product_type === 'pet').length)

// ========== 创建弹窗 ==========
const createDialogVisible = ref(false)
const createFormRef = ref<FormInstance>()
const createLoading = ref(false)
const createForm = reactive({
  name: '',
  product_type: 'goods',
  price: 0,
  cost_price: null as number | null,
  stock: 0,
  pet_id: null as number | null,
  inventory_item_id: null as number | null,
  description: '',
  cover_image: '',
})
const createRules: FormRules = {
  name: [{ required: true, message: '请输入商品名称', trigger: 'blur' }],
  product_type: [{ required: true, message: '请选择商品类型', trigger: 'change' }],
  price: [{ required: true, message: '请输入售价', trigger: 'blur' }],
}

// ========== 编辑弹窗 ==========
const editDialogVisible = ref(false)
const editFormRef = ref<FormInstance>()
const editLoading = ref(false)
const editingId = ref<number | null>(null)
const editForm = reactive({
  name: '',
  product_type: 'goods',
  price: 0,
  cost_price: null as number | null,
  stock: 0,
  pet_id: null as number | null,
  inventory_item_id: null as number | null,
  description: '',
  cover_image: '',
})

// ========== 加载 ==========
const fetchProducts = async () => {
  isLoading.value = true
  try {
    const res = await productApi.list({
      limit: 500,
      store_id: storeStore.currentStoreId ?? undefined,
      product_type: filterType.value ?? undefined,
      search: searchText.value || undefined,
    })
    products.value = res.data
  } catch {
    ElMessage.error('获取商品列表失败')
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchProducts()
  loadDropdownData()
})

// 监听门店切换自动刷新
watch(() => storeStore.currentStoreId, () => {
  fetchProducts()
  loadDropdownData()
})

// 加载下拉选项数据
const loadDropdownData = async () => {
  try {
    const [petRes, invRes] = await Promise.all([
      petApi.list({ limit: 500, store_id: storeStore.currentStoreId ?? undefined }),
      inventoryApi.listItems({ limit: 500, store_id: storeStore.currentStoreId ?? undefined }),
    ])
    petOptions.value = petRes.data
    inventoryOptions.value = invRes.data
  } catch {
    // 下拉数据加载失败不影响主流程
  }
}

// ========== 创建 ==========
const resetCreateForm = () => {
  createForm.name = ''
  createForm.product_type = 'goods'
  createForm.price = 0
  createForm.cost_price = null
  createForm.stock = 0
  createForm.pet_id = null
  createForm.inventory_item_id = null
  createForm.description = ''
  createForm.cover_image = ''
}

const handleCreate = async () => {
  if (!createFormRef.value) return
  const valid = await createFormRef.value.validate().catch(() => false)
  if (!valid) return
  if (!storeStore.currentStoreId) {
    ElMessage.warning('请先选择门店')
    return
  }

  createLoading.value = true
  try {
    await productApi.create({
      name: createForm.name,
      product_type: createForm.product_type,
      store_id: storeStore.currentStoreId,
      price: createForm.price,
      cost_price: createForm.cost_price ?? undefined,
      stock: createForm.stock,
      pet_id: createForm.pet_id ?? undefined,
      inventory_item_id: createForm.inventory_item_id ?? undefined,
      description: createForm.description || undefined,
      cover_image: createForm.cover_image || undefined,
    })
    ElMessage.success('商品创建成功')
    createDialogVisible.value = false
    resetCreateForm()
    await fetchProducts()
  } catch (err: unknown) {
    ElMessage.error(
      (err as { response?: { data?: { detail?: string } } }).response?.data?.detail || '创建失败',
    )
  } finally {
    createLoading.value = false
  }
}

// ========== 编辑 ==========
const openEditDialog = (item: Product) => {
  editingId.value = item.id
  editForm.name = item.name
  editForm.product_type = item.product_type
  editForm.price = item.price
  editForm.cost_price = item.cost_price
  editForm.stock = item.stock
  editForm.pet_id = item.pet_id
  editForm.inventory_item_id = item.inventory_item_id
  editForm.description = item.description || ''
  editForm.cover_image = item.cover_image || ''
  editDialogVisible.value = true
}

const handleEdit = async () => {
  if (!editFormRef.value || editingId.value === null) return
  editLoading.value = true
  try {
    await productApi.update(editingId.value, {
      name: editForm.name || undefined,
      product_type: editForm.product_type,
      price: editForm.price,
      cost_price: editForm.cost_price ?? undefined,
      stock: editForm.stock,
      pet_id: editForm.pet_id,
      inventory_item_id: editForm.inventory_item_id,
      description: editForm.description || undefined,
      cover_image: editForm.cover_image || undefined,
    })
    ElMessage.success('商品已更新')
    editDialogVisible.value = false
    await fetchProducts()
  } catch (err: unknown) {
    ElMessage.error(
      (err as { response?: { data?: { detail?: string } } }).response?.data?.detail || '更新失败',
    )
  } finally {
    editLoading.value = false
  }
}

// ========== 下架 ==========
const handleDelete = async (item: Product) => {
  try {
    await ElMessageBox.confirm(`确定要下架商品「${item.name}」吗？`, '下架商品', {
      type: 'warning',
      confirmButtonText: '确认下架',
    })
    await productApi.delete(item.id)
    ElMessage.success('商品已下架')
    await fetchProducts()
  } catch {
    /* 取消 */
  }
}

// ========== 封面图上传相关 ==========
const beforeCoverUpload = (file: File) => {
  const isValidType = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'].includes(file.type)
  if (!isValidType) {
    ElMessage.error('仅支持 JPG / PNG / GIF / WebP 格式')
    return false
  }
  if (file.size > 20 * 1024 * 1024) {
    ElMessage.error('图片大小不能超过 20MB')
    return false
  }
  return true
}

const handleCoverUpload = async (options: UploadRequestOptions, formType: 'create' | 'edit') => {
  try {
    const res = await productApi.uploadCover(options.file as File)
    const imageUrl = res.data.url

    if (formType === 'create') {
      createForm.cover_image = imageUrl
    } else {
      editForm.cover_image = imageUrl
    }
    ElMessage.success('封面图上传成功')
  } catch (err: unknown) {
    console.error(err)
    ElMessage.error('封面图上传失败')
  }
}

const handleCreateCoverUpload = (options: UploadRequestOptions) =>
  handleCoverUpload(options, 'create')
const handleEditCoverUpload = (options: UploadRequestOptions) => handleCoverUpload(options, 'edit')

const removeCover = (formType: 'create' | 'edit') => {
  if (formType === 'create') createForm.cover_image = ''
  else editForm.cover_image = ''
}

const formatImageUrl = (url: string) => {
  if (!url) return ''
  return url
}

// 类型标签
const typeTag = (type: string) => (type === 'goods' ? 'success' : 'warning')
const typeLabel = (type: string) => (type === 'goods' ? '用品' : '活体宠物')
</script>

<template>
  <div class="page-root">
    <div class="page-header">
      <div>
        <h2 class="page-title">商品管理</h2>
        <p class="page-subtitle">管理宠物用品及活体宠物售卖</p>
      </div>
      <el-button type="primary" :icon="Plus" size="large" @click="createDialogVisible = true">
        新增商品
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-icon" style="background: #ecf5ff; color: #409eff">
          <el-icon :size="22"><Goods /></el-icon>
        </div>
        <div class="stat-body">
          <span class="stat-num">{{ totalCount }}</span
          ><span class="stat-label">商品总数</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #f0f9eb; color: #67c23a">
          <el-icon :size="22"><Goods /></el-icon>
        </div>
        <div class="stat-body">
          <span class="stat-num">{{ goodsCount }}</span
          ><span class="stat-label">用品类</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #fdf6ec; color: #e6a23c">
          <el-icon :size="22"><Present /></el-icon>
        </div>
        <div class="stat-body">
          <span class="stat-num">{{ petCount }}</span
          ><span class="stat-label">活体宠物</span>
        </div>
      </div>
    </div>

    <!-- 筛选 -->
    <div class="toolbar">
      <div class="filter-group">
        <el-input
          v-model="searchText"
          placeholder="搜索商品名称..."
          :prefix-icon="Search"
          clearable
          class="search-input"
          @change="fetchProducts"
        />
        <el-select
          v-model="filterType"
          placeholder="类型筛选"
          clearable
          class="filter-select"
          @change="fetchProducts"
        >
          <el-option label="用品" value="goods" />
          <el-option label="活体宠物" value="pet" />
        </el-select>
      </div>
      <el-button @click="fetchProducts">刷新</el-button>
    </div>

    <!-- 表格 -->
    <div class="table-card">
      <el-table :data="products" v-loading="isLoading" stripe style="width: 100%">
        <el-table-column label="名称" min-width="140">
          <template #default="{ row }">
            <span style="font-weight: 600">{{ row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column label="类型" width="90">
          <template #default="{ row }">
            <el-tag :type="typeTag(row.product_type)" size="small">{{
              typeLabel(row.product_type)
            }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="售价" width="100">
          <template #default="{ row }">¥{{ Number(row.price).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="成本价" width="100">
          <template #default="{ row }">{{
            row.cost_price != null ? `¥${Number(row.cost_price).toFixed(2)}` : '—'
          }}</template>
        </el-table-column>
        <el-table-column label="库存" width="80" prop="stock">
          <template #default="{ row }">
            <span :style="{ color: row.stock === 0 ? '#f56c6c' : '#303133', fontWeight: 600 }">
              {{ row.product_type === 'pet' ? (row.stock ? '有货' : '售罄') : row.stock }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="关联" min-width="120" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.pet_name || row.inventory_item_name || '—' }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">{{
              row.is_active ? '上架' : '下架'
            }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link :icon="EditPen" @click="openEditDialog(row)"
              >编辑</el-button
            >
            <el-button
              v-if="row.is_active"
              type="danger"
              link
              :icon="Delete"
              @click="handleDelete(row)"
              >下架</el-button
            >
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 创建弹窗 -->
    <el-dialog
      v-model="createDialogVisible"
      title="新增商品"
      width="560px"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <el-form ref="createFormRef" :model="createForm" :rules="createRules" label-width="90px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="商品名称" prop="name"
              ><el-input v-model="createForm.name" maxlength="100"
            /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="商品类型" prop="product_type">
              <el-select v-model="createForm.product_type" style="width: 100%">
                <el-option label="宠物用品" value="goods" />
                <el-option label="活体宠物" value="pet" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="售价 (¥)" prop="price">
              <el-input-number
                v-model="createForm.price"
                :min="0"
                :precision="2"
                style="width: 100%"
                controls-position="right"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="成本价 (¥)">
              <el-input-number
                v-model="createForm.cost_price"
                :min="0"
                :precision="2"
                style="width: 100%"
                controls-position="right"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="库存数量">
              <el-input-number
                v-model="createForm.stock"
                :min="0"
                :precision="2"
                style="width: 100%"
                controls-position="right"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="关联库存">
          <el-select
            v-model="createForm.inventory_item_id"
            placeholder="选择库存物品（可选）"
            clearable
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="item in inventoryOptions"
              :key="item.id"
              :label="`${item.name} (${item.sku})`"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="关联宠物">
          <el-select
            v-model="createForm.pet_id"
            placeholder="选择宠物（可选）"
            clearable
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="p in petOptions"
              :key="p.id"
              :label="`${p.name || '未命名'} (${p.species}${p.breed ? '·' + p.breed : ''})`"
              :value="p.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="封面图">
          <div class="custom-avatar-uploader">
            <el-upload
              action="#"
              :show-file-list="false"
              :before-upload="beforeCoverUpload"
              :http-request="handleCreateCoverUpload"
            >
              <img
                v-if="createForm.cover_image"
                :src="formatImageUrl(createForm.cover_image)"
                class="avatar-preview"
                alt="商品封面图"
              />
              <div v-else class="avatar-placeholder">
                <el-icon class="avatar-icon"><Plus /></el-icon>
                <span style="font-size: 12px">上传封面</span>
              </div>
            </el-upload>
            <el-button
              v-if="createForm.cover_image"
              type="danger"
              circle
              :icon="Delete"
              size="small"
              class="avatar-delete-btn"
              @click.stop="removeCover('create')"
            />
          </div>
        </el-form-item>
        <el-form-item label="商品描述">
          <el-input
            v-model="createForm.description"
            type="textarea"
            :rows="3"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="createLoading" @click="handleCreate"
          >确认创建</el-button
        >
      </template>
    </el-dialog>

    <!-- 编辑弹窗 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑商品"
      width="560px"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <el-form ref="editFormRef" :model="editForm" label-width="90px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="商品名称"
              ><el-input v-model="editForm.name" maxlength="100"
            /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="商品类型">
              <el-select v-model="editForm.product_type" style="width: 100%">
                <el-option label="宠物用品" value="goods" />
                <el-option label="活体宠物" value="pet" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="售价 (¥)">
              <el-input-number
                v-model="editForm.price"
                :min="0"
                :precision="2"
                style="width: 100%"
                controls-position="right"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="成本价 (¥)">
              <el-input-number
                v-model="editForm.cost_price"
                :min="0"
                :precision="2"
                style="width: 100%"
                controls-position="right"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="库存数量">
              <el-input-number
                v-model="editForm.stock"
                :min="0"
                :precision="2"
                style="width: 100%"
                controls-position="right"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="关联库存">
          <el-select
            v-model="editForm.inventory_item_id"
            placeholder="选择库存物品（可选）"
            clearable
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="item in inventoryOptions"
              :key="item.id"
              :label="`${item.name} (${item.sku})`"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="关联宠物">
          <el-select
            v-model="editForm.pet_id"
            placeholder="选择宠物（可选）"
            clearable
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="p in petOptions"
              :key="p.id"
              :label="`${p.name || '未命名'} (${p.species}${p.breed ? '·' + p.breed : ''})`"
              :value="p.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="封面图">
          <div class="custom-avatar-uploader">
            <el-upload
              action="#"
              :show-file-list="false"
              :before-upload="beforeCoverUpload"
              :http-request="handleEditCoverUpload"
            >
              <img
                v-if="editForm.cover_image"
                :src="formatImageUrl(editForm.cover_image)"
                class="avatar-preview"
                alt="商品封面图"
              />
              <div v-else class="avatar-placeholder">
                <el-icon class="avatar-icon"><Plus /></el-icon>
                <span style="font-size: 12px">上传封面</span>
              </div>
            </el-upload>
            <el-button
              v-if="editForm.cover_image"
              type="danger"
              circle
              :icon="Delete"
              size="small"
              class="avatar-delete-btn"
              @click.stop="removeCover('edit')"
            />
          </div>
        </el-form-item>
        <el-form-item label="商品描述">
          <el-input
            v-model="editForm.description"
            type="textarea"
            :rows="3"
            maxlength="500"
            show-word-limit
          />
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
.page-root {
  max-width: 1200px;
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

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.filter-group {
  display: flex;
  align-items: center;
  gap: 12px;
}
.search-input {
  width: 240px;
}
.filter-select {
  width: 150px;
}

.table-card {
  background: #fff;
  border-radius: 16px;
  padding: 4px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  overflow: hidden;
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

/* ========== 移动端适配 ========== */
@media (max-width: 767px) {
  .page-header {
    flex-direction: column;
    gap: 12px;
  }
  .page-header .el-button {
    width: 100%;
  }
  .page-title {
    font-size: 18px;
  }

  .stats-row {
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }
  .stat-card {
    padding: 12px 16px;
    gap: 10px;
  }
  .stat-icon {
    width: 40px;
    height: 40px;
  }
  .stat-num {
    font-size: 18px;
  }

  .toolbar {
    flex-direction: column;
    gap: 12px;
  }
  .filter-group {
    flex-wrap: wrap;
    width: 100%;
  }
  .search-input {
    width: 100%;
  }
  .filter-select {
    width: 100%;
  }

  .table-card {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
}
/* ========== 图片上传样式 ========== */
.custom-avatar-uploader {
  position: relative;
  width: 130px;
  height: 130px;
}

.custom-avatar-uploader :deep(.el-upload) {
  border: 1px dashed #d9d9d9;
  border-radius: 8px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  width: 130px;
  height: 130px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #fafafa;
  transition: border-color 0.3s;
}

.custom-avatar-uploader :deep(.el-upload:hover) {
  border-color: #409eff;
}

.avatar-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.avatar-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #8c939d;
  line-height: 1.5;
}

.avatar-icon {
  font-size: 28px;
  margin-bottom: 8px;
}

.avatar-delete-btn {
  position: absolute;
  top: -10px;
  right: -10px;
  z-index: 10;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}

@media (max-width: 480px) {
  .stats-row {
    grid-template-columns: 1fr;
  }
}
</style>

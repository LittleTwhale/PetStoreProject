<script setup lang="ts">
// views/OrderCreatePage.vue — 创建订单
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, Delete, Back } from '@element-plus/icons-vue'
import { orderApi, type OrderCreateItem } from '@/api/order'
import { productApi, type Product } from '@/api/product'
import { serviceApi, type Service } from '@/api/service'
import { customerApi } from '@/api/customer'
import { useStoreStore } from '@/stores/store'

const router = useRouter()
const storeStore = useStoreStore()

// ========== 订单基本信息 ==========
const orderType = ref<string>('sale') // sale / service
const customerId = ref<number | null>(null)
const paymentMethod = ref<string>('cash')
const discountAmount = ref(0)
const remark = ref('')
const submitting = ref(false)

// ========== 可选数据 ==========
const products = ref<Product[]>([])
const services = ref<Service[]>([])
const customers = ref<{ id: number; name: string; phone: string | null }[]>([])

// ========== 明细行 ==========
interface ItemRow {
  key: number
  itemType: string // 'product' | 'service'
  productId: number | null
  serviceId: number | null
  productName: string
  serviceName: string
  unitPrice: number
  quantity: number
  subtotal: number
  maxStock: number
}

let nextKey = 0
const items = ref<ItemRow[]>([createEmptyRow()])

function createEmptyRow(): ItemRow {
  return {
    key: nextKey++,
    itemType: 'product',
    productId: null,
    serviceId: null,
    productName: '',
    serviceName: '',
    unitPrice: 0,
    quantity: 1,
    subtotal: 0,
    maxStock: 0,
  }
}

const addRow = () => { items.value.push(createEmptyRow()) }

const removeRow = (idx: number) => {
  if (items.value.length <= 1) return
  items.value.splice(idx, 1)
}

// 选择商品
const onProductSelect = (idx: number, productId: number) => {
  const row = items.value[idx]
  if (!row) return
  row.productId = productId
  row.serviceId = null
  const p = products.value.find(x => x.id === productId)
  if (p) {
    row.productName = p.name
    row.unitPrice = p.price
    row.maxStock = p.stock
    row.quantity = 1
    row.subtotal = p.price
  }
}

// 选择服务
const onServiceSelect = (idx: number, serviceId: number) => {
  const row = items.value[idx]
  if (!row) return
  row.serviceId = serviceId
  row.productId = null
  row.itemType = 'service'
  const s = services.value.find(x => x.id === serviceId)
  if (s) {
    row.serviceName = s.name
    row.unitPrice = s.price
    row.quantity = 1
    row.subtotal = s.price
  }
}

// 数量/单价变化时重算小计
const recalcSubtotal = (idx: number) => {
  const row = items.value[idx]
  if (!row) return
  if (row.quantity > row.maxStock && row.itemType === 'product' && row.maxStock > 0) {
    row.quantity = row.maxStock
    ElMessage.warning('数量不可超过库存')
  }
  row.subtotal = row.unitPrice * row.quantity
}

// 总金额
const totalAmount = computed(() => items.value.reduce((s, r) => s + r.subtotal, 0))
const finalAmount = computed(() => Math.max(0, totalAmount.value - discountAmount.value))

// 加载下拉数据
const loadDropdownData = async () => {
  try {
    const [pRes, sRes, cRes] = await Promise.all([
      productApi.list({ limit: 500, store_id: storeStore.currentStoreId ?? undefined }),
      serviceApi.list({ limit: 500, store_id: storeStore.currentStoreId ?? undefined }),
      customerApi.list({ limit: 500 }),
    ])
    products.value = pRes.data.filter((p: Product) => p.is_active)
    services.value = sRes.data.filter((s: Service) => s.is_active)
    customers.value = cRes.data.map(
      (c: { id: number; real_name: string | null; phone: string | null }) => ({
        id: c.id,
        name: c.real_name || '未实名',
        phone: c.phone,
      }),
    )
  } catch {
    ElMessage.error('加载基础数据失败')
  }
}

onMounted(() => { loadDropdownData() })

// 切换订单类型时清空明细
watch(orderType, () => {
  items.value = [createEmptyRow()]
  discountAmount.value = 0
})

// 监听门店切换自动刷新商品和服务列表
watch(() => storeStore.currentStoreId, () => {
  loadDropdownData()
})

// 提交
const handleSubmit = async () => {
  if (!storeStore.currentStoreId) { ElMessage.warning('请先选择门店'); return }

  const validItems = items.value.filter(r =>
    r.itemType === 'product' ? r.productId : r.serviceId,
  )
  if (validItems.length === 0) { ElMessage.warning('请至少添加一个项目'); return }

  const orderItems: OrderCreateItem[] = validItems.map(r => ({
    item_type: r.itemType,
    product_id: r.productId,
    service_id: r.serviceId,
    quantity: r.quantity,
    unit_price: r.unitPrice,
    subtotal: r.subtotal,
  }))

  submitting.value = true
  try {
    const res = await orderApi.create({
      store_id: storeStore.currentStoreId,
      order_type: orderType.value,
      customer_id: customerId.value || undefined,
      discount_amount: discountAmount.value,
      payment_method: paymentMethod.value,
      remark: remark.value || undefined,
      items: orderItems,
    })
    ElMessage.success(`订单创建成功：${res.data.order_no}`)
    router.push('/orders')
  } catch (err: unknown) {
    ElMessage.error(
      (err as { response?: { data?: { detail?: string } } }).response?.data?.detail || '创建失败',
    )
  } finally { submitting.value = false }
}
</script>

<template>
  <div class="page-root">
    <div class="page-header">
      <div style="display:flex;align-items:center;gap:12px">
        <el-button :icon="Back" text @click="router.push('/orders')" />
        <div>
          <h2 class="page-title">创建订单</h2>
          <p class="page-subtitle">创建销售订单或服务订单</p>
        </div>
      </div>
    </div>

    <!-- 基本信息 -->
    <div class="section-card">
      <h3 class="section-title">基本信息</h3>
      <el-row :gutter="16">
        <el-col :xs="12" :sm="6">
          <div class="field-item">
            <label class="field-label">订单类型</label>
            <el-radio-group v-model="orderType">
              <el-radio-button value="sale">销售订单</el-radio-button>
              <el-radio-button value="service">服务订单</el-radio-button>
            </el-radio-group>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6">
          <div class="field-item">
            <label class="field-label">支付方式</label>
            <el-select v-model="paymentMethod" style="width:100%">
              <el-option label="现金" value="cash" />
              <el-option label="微信" value="wechat" />
              <el-option label="支付宝" value="alipay" />
              <el-option label="刷卡" value="card" />
              <el-option label="余额" value="balance" />
            </el-select>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6">
          <div class="field-item">
            <label class="field-label">客户（可选）</label>
            <el-select v-model="customerId" placeholder="散客可不选" clearable filterable style="width:100%">
              <el-option
                v-for="c in customers" :key="c.id"
                :label="`${c.name} ${c.phone || ''}`"
                :value="c.id"
              />
            </el-select>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6">
          <div class="field-item">
            <label class="field-label">优惠金额 (¥)</label>
            <el-input-number v-model="discountAmount" :min="0" :precision="2" style="width:100%" />
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 项目明细 -->
    <div class="section-card">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">
        <h3 class="section-title" style="margin-bottom:0">项目明细</h3>
        <el-button :icon="Plus" size="small" type="primary" plain @click="addRow">添加项目</el-button>
      </div>

      <div v-for="(row, idx) in items" :key="row.key" class="item-row">
        <el-row :gutter="10" align="middle">
          <!-- 选择商品/服务 -->
          <el-col :xs="24" :sm="5">
            <div class="field-item">
              <label class="field-label-inline">{{ orderType === 'sale' ? '商品' : '服务' }}</label>
              <template v-if="orderType === 'sale'">
                <el-select
                  :model-value="row.productId"
                  placeholder="选择商品"
                  filterable
                  style="width:100%"
                  @change="(val:number) => onProductSelect(idx, val)"
                >
                  <el-option
                    v-for="p in products" :key="p.id"
                    :label="`${p.name} (¥${Number(p.price).toFixed(2)})`"
                    :value="p.id"
                  />
                </el-select>
              </template>
              <template v-else>
                <el-select
                  :model-value="row.serviceId"
                  placeholder="选择服务"
                  filterable
                  style="width:100%"
                  @change="(val:number) => onServiceSelect(idx, val)"
                >
                  <el-option
                    v-for="s in services" :key="s.id"
                    :label="`${s.name} (¥${Number(s.price).toFixed(2)})`"
                    :value="s.id"
                  />
                </el-select>
              </template>
            </div>
          </el-col>
          <!-- 单价 -->
          <el-col :xs="8" :sm="3">
            <div class="field-item">
              <label class="field-label-inline">单价</label>
              <el-input-number
                v-model="row.unitPrice"
                :min="0"
                :precision="2"
                size="small"
                style="width:100%"
                @change="recalcSubtotal(idx)"
              />
            </div>
          </el-col>
          <!-- 数量 -->
          <el-col :xs="8" :sm="3">
            <div class="field-item">
              <label class="field-label-inline">数量</label>
              <el-input-number
                v-model="row.quantity"
                :min="1"
                :max="row.maxStock > 0 ? row.maxStock : 9999"
                size="small"
                style="width:100%"
                @change="recalcSubtotal(idx)"
              />
            </div>
          </el-col>
          <!-- 小计 -->
          <el-col :xs="8" :sm="3">
            <div class="field-item">
              <label class="field-label-inline">小计</label>
              <span class="subtotal-display">¥{{ row.subtotal.toFixed(2) }}</span>
            </div>
          </el-col>
          <!-- 操作 -->
          <el-col :xs="24" :sm="2" style="text-align:right">
            <el-button type="danger" :icon="Delete" circle size="small" @click="removeRow(idx)" :disabled="items.length <= 1" />
          </el-col>
        </el-row>
      </div>
    </div>

    <!-- 合计 + 备注 + 提交 -->
    <div class="section-card">
      <el-row :gutter="16">
        <el-col :xs="24" :sm="12">
          <div class="field-item">
            <label class="field-label">备注</label>
            <el-input v-model="remark" placeholder="订单备注（可选）" maxlength="200" />
          </div>
        </el-col>
        <el-col :xs="24" :sm="12">
          <div class="summary-area">
            <div class="summary-line">
              <span>总金额</span>
              <span>¥{{ totalAmount.toFixed(2) }}</span>
            </div>
            <div class="summary-line">
              <span>优惠</span>
              <span>-¥{{ discountAmount.toFixed(2) }}</span>
            </div>
            <div class="summary-line final">
              <span>实付金额</span>
              <span>¥{{ finalAmount.toFixed(2) }}</span>
            </div>
            <el-button type="primary" size="large" style="width:100%;margin-top:12px" :loading="submitting" @click="handleSubmit">
              提交订单
            </el-button>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<style scoped>
.page-root { max-width: 900px; margin: 0 auto; }
.page-header { margin-bottom: 20px; }
.page-title { font-size: 22px; font-weight: 700; color: #1a1a2e; margin: 0 0 4px 0; }
.page-subtitle { font-size: 13px; color: #909399; margin: 0; }

.section-card {
  background: #fff; border-radius: 14px; padding: 20px 24px;
  margin-bottom: 16px; box-shadow: 0 2px 12px rgba(0,0,0,0.04);
}
.section-title { font-size: 15px; font-weight: 600; color: #303133; margin: 0 0 14px 0; }

.field-item { margin-bottom: 10px; }
.field-label { display: block; font-size: 13px; color: #606266; margin-bottom: 4px; font-weight: 500; }
.field-label-inline { display: block; font-size: 12px; color: #909399; margin-bottom: 2px; }

.item-row {
  padding: 12px 0; border-bottom: 1px solid #f0f0f0;
}
.item-row:last-child { border-bottom: none; }

.subtotal-display {
  font-size: 15px; font-weight: 600; color: #409eff;
}

.summary-area {
  background: #fafafa; border-radius: 12px; padding: 16px;
}
.summary-line {
  display: flex; justify-content: space-between;
  font-size: 14px; color: #606266; margin-bottom: 8px;
}
.summary-line.final {
  font-size: 18px; font-weight: 700; color: #f56c6c;
  border-top: 1px solid #e8e8e8; padding-top: 10px; margin-top: 6px;
}

/* ========== 移动端适配 ========== */
@media (max-width: 767px) {
  .page-root { padding: 0 4px; }
  .page-title { font-size: 18px; }
  .section-card { padding: 14px 16px; }

  .item-row { padding: 10px 0; }
  .item-row .el-col { margin-bottom: 6px; }

  .summary-area { margin-top: 12px; }
}
</style>

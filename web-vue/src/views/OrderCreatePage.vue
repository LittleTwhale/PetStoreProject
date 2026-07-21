<script setup lang="ts">
// views/OrderCreatePage.vue 鈥?鍒涘缓璁㈠崟
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

// ========== 璁㈠崟鍩烘湰淇℃伅 ==========
const orderType = ref<string>('sale') // sale / service
const customerId = ref<number | null>(null)
const paymentMethod = ref<string>('cash')
const discountAmount = ref(0)
const remark = ref('')
const submitting = ref(false)

// ========== 鍙€夋暟鎹?==========
const products = ref<Product[]>([])
const services = ref<Service[]>([])
const customers = ref<{ id: number; name: string; phone: string | null }[]>([])

// ========== 鏄庣粏琛?==========
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

// 閫夋嫨鍟嗗搧
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
    row.subtotal = Math.round(p.price * 100) / 100
  }
}

// 閫夋嫨鏈嶅姟
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
    row.subtotal = Math.round(s.price * 100) / 100
  }
}

// 鏁伴噺/鍗曚环鍙樺寲鏃堕噸绠楀皬璁?const recalcSubtotal = (idx: number) => {
  const row = items.value[idx]
  if (!row) return
  if (row.quantity > row.maxStock && row.itemType === 'product' && row.maxStock > 0) {
    row.quantity = row.maxStock
    ElMessage.warning('鏁伴噺涓嶅彲瓒呰繃搴撳瓨')
  }
  row.subtotal = Math.round(row.unitPrice * row.quantity * 100) / 100
}

// 鎬婚噾棰?const totalAmount = computed(() => items.value.reduce((s, r) => s + r.subtotal, 0))
const finalAmount = computed(() => Math.max(0, Math.round((totalAmount.value - discountAmount.value) * 100) / 100))

// 鍔犺浇涓嬫媺鏁版嵁
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
        name: c.real_name || '鏈疄鍚?,
        phone: c.phone,
      }),
    )
  } catch {
    ElMessage.error('鍔犺浇鍩虹鏁版嵁澶辫触')
  }
}

onMounted(() => { loadDropdownData() })

// 鍒囨崲璁㈠崟绫诲瀷鏃舵竻绌烘槑缁?watch(orderType, () => {
  items.value = [createEmptyRow()]
  discountAmount.value = 0
})

// 鐩戝惉闂ㄥ簵鍒囨崲鑷姩鍒锋柊鍟嗗搧鍜屾湇鍔″垪琛?watch(() => storeStore.currentStoreId, () => {
  loadDropdownData()
})

// 鎻愪氦
const handleSubmit = async () => {
  if (!storeStore.currentStoreId) { ElMessage.warning('璇峰厛閫夋嫨闂ㄥ簵'); return }

  const validItems = items.value.filter(r =>
    r.itemType === 'product' ? r.productId : r.serviceId,
  )
  if (validItems.length === 0) { ElMessage.warning('璇疯嚦灏戞坊鍔犱竴涓」鐩?); return }

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
    ElMessage.success(`璁㈠崟鍒涘缓鎴愬姛锛?{res.data.order_no}`)
    router.push('/orders')
  } catch (err: unknown) {
    ElMessage.error(
      (err as { response?: { data?: { detail?: string } } }).response?.data?.detail || '鍒涘缓澶辫触',
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
          <h2 class="page-title">鍒涘缓璁㈠崟</h2>
          <p class="page-subtitle">鍒涘缓閿€鍞鍗曟垨鏈嶅姟璁㈠崟</p>
        </div>
      </div>
    </div>

    <!-- 鍩烘湰淇℃伅 -->
    <div class="section-card">
      <h3 class="section-title">鍩烘湰淇℃伅</h3>
      <el-row :gutter="16">
        <el-col :xs="12" :sm="6">
          <div class="field-item">
            <label class="field-label">璁㈠崟绫诲瀷</label>
            <el-radio-group v-model="orderType">
              <el-radio-button value="sale">閿€鍞鍗?/el-radio-button>
              <el-radio-button value="service">鏈嶅姟璁㈠崟</el-radio-button>
            </el-radio-group>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6">
          <div class="field-item">
            <label class="field-label">鏀粯鏂瑰紡</label>
            <el-select v-model="paymentMethod" style="width:100%">
              <el-option label="鐜伴噾" value="cash" />
              <el-option label="寰俊" value="wechat" />
              <el-option label="鏀粯瀹? value="alipay" />
              <el-option label="鍒峰崱" value="card" />
              <el-option label="浣欓" value="balance" />
            </el-select>
          </div>
        </el-col>
        <el-col :xs="12" :sm="6">
          <div class="field-item">
            <label class="field-label">瀹㈡埛锛堝彲閫夛級</label>
            <el-select v-model="customerId" placeholder="鏁ｅ鍙笉閫? clearable filterable style="width:100%">
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
            <label class="field-label">浼樻儬閲戦 (楼)</label>
            <el-input-number v-model="discountAmount" :min="0" :precision="2" style="width:100%" />
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- 椤圭洰鏄庣粏 -->
    <div class="section-card">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">
        <h3 class="section-title" style="margin-bottom:0">椤圭洰鏄庣粏</h3>
        <el-button :icon="Plus" size="small" type="primary" plain @click="addRow">娣诲姞椤圭洰</el-button>
      </div>

      <div v-for="(row, idx) in items" :key="row.key" class="item-row">
        <el-row :gutter="10" align="middle">
          <!-- 閫夋嫨鍟嗗搧/鏈嶅姟 -->
          <el-col :xs="24" :sm="5">
            <div class="field-item">
              <label class="field-label-inline">{{ orderType === 'sale' ? '鍟嗗搧' : '鏈嶅姟' }}</label>
              <template v-if="orderType === 'sale'">
                <el-select
                  :model-value="row.productId"
                  placeholder="閫夋嫨鍟嗗搧"
                  filterable
                  style="width:100%"
                  @change="(val:number) => onProductSelect(idx, val)"
                >
                  <el-option
                    v-for="p in products" :key="p.id"
                    :label="`${p.name} (楼${Number(p.price).toFixed(2)})`"
                    :value="p.id"
                  />
                </el-select>
              </template>
              <template v-else>
                <el-select
                  :model-value="row.serviceId"
                  placeholder="閫夋嫨鏈嶅姟"
                  filterable
                  style="width:100%"
                  @change="(val:number) => onServiceSelect(idx, val)"
                >
                  <el-option
                    v-for="s in services" :key="s.id"
                    :label="`${s.name} (楼${Number(s.price).toFixed(2)})`"
                    :value="s.id"
                  />
                </el-select>
              </template>
            </div>
          </el-col>
          <!-- 鍗曚环 -->
          <el-col :xs="8" :sm="3">
            <div class="field-item">
              <label class="field-label-inline">鍗曚环</label>
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
          <!-- 鏁伴噺 -->
          <el-col :xs="8" :sm="3">
            <div class="field-item">
              <label class="field-label-inline">鏁伴噺</label>
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
          <!-- 灏忚 -->
          <el-col :xs="8" :sm="3">
            <div class="field-item">
              <label class="field-label-inline">灏忚</label>
              <span class="subtotal-display">楼{{ row.subtotal.toFixed(2) }}</span>
            </div>
          </el-col>
          <!-- 鎿嶄綔 -->
          <el-col :xs="24" :sm="2" style="text-align:right">
            <el-button type="danger" :icon="Delete" circle size="small" @click="removeRow(idx)" :disabled="items.length <= 1" />
          </el-col>
        </el-row>
      </div>
    </div>

    <!-- 鍚堣 + 澶囨敞 + 鎻愪氦 -->
    <div class="section-card">
      <el-row :gutter="16">
        <el-col :xs="24" :sm="12">
          <div class="field-item">
            <label class="field-label">澶囨敞</label>
            <el-input v-model="remark" placeholder="璁㈠崟澶囨敞锛堝彲閫夛級" maxlength="200" />
          </div>
        </el-col>
        <el-col :xs="24" :sm="12">
          <div class="summary-area">
            <div class="summary-line">
              <span>鎬婚噾棰?/span>
              <span>楼{{ totalAmount.toFixed(2) }}</span>
            </div>
            <div class="summary-line">
              <span>浼樻儬</span>
              <span>-楼{{ discountAmount.toFixed(2) }}</span>
            </div>
            <div class="summary-line final">
              <span>瀹炰粯閲戦</span>
              <span>楼{{ finalAmount.toFixed(2) }}</span>
            </div>
            <el-button type="primary" size="large" style="width:100%;margin-top:12px" :loading="submitting" @click="handleSubmit">
              鎻愪氦璁㈠崟
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

/* ========== 绉诲姩绔€傞厤 ========== */
@media (max-width: 767px) {
  .page-root { padding: 0 4px; }
  .page-title { font-size: 18px; }
  .section-card { padding: 14px 16px; }

  .item-row { padding: 10px 0; }
  .item-row .el-col { margin-bottom: 6px; }

  .summary-area { margin-top: 12px; }
}
</style>


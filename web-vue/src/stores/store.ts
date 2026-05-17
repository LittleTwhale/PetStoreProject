// stores/store.ts — 门店上下文（当前操作门店选择）
import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { storeApi, type Store } from '@/api/store'
import { useUserStore } from './user'

export const useStoreStore = defineStore('store', () => {
  const userStore = useUserStore()

  // 1. 读取本地存储
  const storedId = localStorage.getItem('currentStoreId')

  // 2. 必须显式告诉 TS，这个变量既可以是数字，也可以是 null
  let initialId: number | null = null

  if (storedId && storedId !== 'null' && storedId !== 'undefined') {
    const parsed = Number(storedId)
    // 只有当转换后真的是一个有效数字时，才赋给 initialId
    if (!Number.isNaN(parsed)) {
      initialId = parsed
    } else {
      // 顺手清理掉本地的脏数据
      localStorage.removeItem('currentStoreId')
    }
  }

  // staff 用户强制使用绑定门店
  if (userStore.user?.role === 'staff') {
    const boundId = userStore.user?.bound_store_id
    if (boundId) {
      initialId = boundId
    }
  }

  // 3. 初始化 ref
  const currentStoreId = ref<number | null>(initialId)
  const myStores = ref<Store[]>([])

  /** staff 是否允许切换门店（staff只能看绑定门店，不可切换或查看全部） */
  const canSwitchStore = computed(() => userStore.user?.role === 'admin')

  /** staff 是否允许查看全部门店 */
  const canViewAll = computed(() => userStore.user?.role === 'admin')

  // 计算当前选中的门店完整信息
  const currentStore = computed(
    () => myStores.value.find((s) => s.id === currentStoreId.value) || null,
  )

  // 获取门店列表
  async function fetchMyStores() {
    try {
      // staff 使用 /stores/my 获取绑定门店
      if (userStore.user?.role === 'staff') {
        const res = await storeApi.my()
        myStores.value = res.data
        // staff 自动选中第一个绑定门店
        // 使用 ?. 防止严格模式下 [0] 报 undefined
        const firstStoreId = myStores.value[0]?.id
        if (firstStoreId) {
          switchStore(firstStoreId)
        }
      } else {
        const res = await storeApi.list({ limit: 500 })
        myStores.value = res.data
      }
    } catch {
      myStores.value = []
    }
  }

  // 切换门店方法（支持传入 null 代表全部门店，仅admin可用）
  function switchStore(storeId: number | null) {
    // staff 不可切换到全部门店
    if (userStore.user?.role === 'staff' && storeId === null) {
      return
    }
    currentStoreId.value = storeId
    if (storeId === null) {
      localStorage.removeItem('currentStoreId')
    } else {
      localStorage.setItem('currentStoreId', String(storeId))
    }
  }

  return {
    currentStoreId,
    myStores,
    currentStore,
    canSwitchStore,
    canViewAll,
    fetchMyStores,
    switchStore,
  }
})

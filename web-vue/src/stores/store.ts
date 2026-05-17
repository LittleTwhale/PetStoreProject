// stores/store.ts — 门店上下文（当前操作门店选择）
import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { storeApi, type Store } from '@/api/store'

export const useStoreStore = defineStore('store', () => {
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

  // 3. 初始化 ref
  const currentStoreId = ref<number | null>(initialId)
  const myStores = ref<Store[]>([])

  // 计算当前选中的门店完整信息
  const currentStore = computed(
    () => myStores.value.find((s) => s.id === currentStoreId.value) || null,
  )

  // 获取门店列表
  async function fetchMyStores() {
    try {
      const res = await storeApi.list({ limit: 500 })
      myStores.value = res.data
    } catch {
      myStores.value = []
    }
  }

  // 切换门店方法（支持传入 null 代表全部门店）
  function switchStore(storeId: number | null) {
    currentStoreId.value = storeId
    if (storeId === null) {
      localStorage.removeItem('currentStoreId')
    } else {
      localStorage.setItem('currentStoreId', String(storeId))
    }
  }

  return { currentStoreId, myStores, currentStore, fetchMyStores, switchStore }
})

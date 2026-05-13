// stores/store.ts — 门店上下文（当前操作门店选择）
import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { storeApi, type Store } from '@/api/store'

export const useStoreStore = defineStore('store', () => {
  const currentStoreId = ref<number | null>(
    Number(localStorage.getItem('currentStoreId')) || null,
  )
  const myStores = ref<Store[]>([])

  const currentStore = computed(() =>
    myStores.value.find(s => s.id === currentStoreId.value) || null,
  )

  async function fetchMyStores() {
    try {
      const res = await storeApi.list({ limit: 500 })
      myStores.value = res.data
      // 如果当前没有选中门店且有门店列表，自动选第一个
      if (!currentStoreId.value && myStores.value.length > 0) {
        switchStore(myStores.value[0].id)
      }
    } catch {
      myStores.value = []
    }
  }

  function switchStore(storeId: number) {
    currentStoreId.value = storeId
    localStorage.setItem('currentStoreId', String(storeId))
  }

  return { currentStoreId, myStores, currentStore, fetchMyStores, switchStore }
})

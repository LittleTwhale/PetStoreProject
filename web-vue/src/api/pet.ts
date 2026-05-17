// api/pet.ts — 宠物台账管理 API
import api from './index'

export interface PetInfo {
  id: number
  owner_id: number | null
  store_id: number | null
  name: string | null
  species: string
  breed: string | null
  gender: string | null
  weight: number | null
  birth_date: string | null
  is_neutered: boolean
  vaccine_status: string | null
  avatar: string | null
  special_notes: string | null
  ownership_type: string
  price: number | null
}

export const petApi = {
  /** 获取宠物列表，支持按归属类型、主人ID、门店过滤和分页 */
  list: (params?: {
    ownership_type?: string
    owner_id?: number
    store_id?: number
    skip?: number
    limit?: number
  }) => api.get('/pets/', { params }),

  /** 获取单个宠物详情 */
  get: (id: number) => api.get(`/pets/${id}`),

  /** 录入新宠物 */
  create: (data: {
    name?: string
    species: string
    breed?: string
    gender?: string
    weight?: number
    birth_date?: string
    is_neutered?: boolean
    vaccine_status?: string
    avatar?: string
    special_notes?: string
    ownership_type?: string
    price?: number | null
    owner_id?: number | null
    store_id?: number | null
  }) => api.post('/pets/', data),

  /** 更新宠物信息 */
  update: (
    id: number,
    data: {
      name?: string
      species?: string
      breed?: string
      gender?: string
      weight?: number
      birth_date?: string
      is_neutered?: boolean
      vaccine_status?: string
      avatar?: string
      special_notes?: string
      ownership_type?: string
      price?: number | null
      owner_id?: number | null
      store_id?: number | null
    },
  ) => api.put(`/pets/${id}`, data),

  /** 删除宠物档案 */
  delete: (id: number) => api.delete(`/pets/${id}`),

  /** 上传宠物照片 */
  uploadAvatar: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/pets/upload-avatar', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}

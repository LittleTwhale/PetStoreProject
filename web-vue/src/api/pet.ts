// api/pet.ts — 宠物台账管理 API
import api from './index'

export interface PetInfo {
  id: number
  owner_id: number | null
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
  /** 获取宠物列表，支持按归属类型、主人ID过滤和分页 */
  list: (params?: {
    ownership_type?: string
    owner_id?: number
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
    },
  ) => api.put(`/pets/${id}`, data),

  /** 删除宠物档案 */
  delete: (id: number) => api.delete(`/pets/${id}`),
}

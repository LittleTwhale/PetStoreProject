<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance } from 'element-plus'
import { UserFilled, Camera, InfoFilled, Edit } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { authApi } from '@/api'

const userStore = useUserStore()

const isEditing = ref(false)
const isSaving = ref(false)
const isUploading = ref(false)
const formRef = ref<FormInstance>()

const editForm = reactive({
  nickname: '',
  position_desc: '',
})

// 加载用户信息
onMounted(async () => {
  if (!userStore.user) {
    await userStore.fetchUser()
  }
  syncForm()
})

const syncForm = () => {
  if (userStore.user) {
    editForm.nickname = userStore.user.nickname
    editForm.position_desc = userStore.user.position_desc || ''
  }
}

// 开始编辑
const startEdit = () => {
  syncForm()
  isEditing.value = true
}

const cancelEdit = () => {
  isEditing.value = false
  syncForm()
}

// 保存
const handleSave = async () => {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  isSaving.value = true
  try {
    const res = await authApi.updateMe({
      nickname: editForm.nickname,
      position_desc: editForm.position_desc || undefined,
    })
    userStore.user = res.data
    isEditing.value = false
    ElMessage.success('个人信息已更新')
  } catch (err: unknown) {
    ElMessage.error(
      (err as { response?: { data?: { detail?: string } } }).response?.data?.detail ||
        '更新失败',
    )
  } finally {
    isSaving.value = false
  }
}

// 上传头像
const handleAvatarChange = async (file: File) => {
  isUploading.value = true
  try {
    const res = await authApi.uploadAvatar(file)
    if (userStore.user) {
      userStore.user.avatar = res.data.avatar_url
    }
    ElMessage.success('头像已更新')
  } catch (err: unknown) {
    ElMessage.error(
      (err as { response?: { data?: { detail?: string } } }).response?.data?.detail ||
        '上传失败',
    )
  } finally {
    isUploading.value = false
  }
}

// 文件选择前校验
const beforeAvatarUpload = (file: File) => {
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
  if (!allowedTypes.includes(file.type)) {
    ElMessage.error('仅支持 JPG / PNG / GIF / WebP 格式')
    return false
  }
  if (file.size > 5 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过 5MB')
    return false
  }
  handleAvatarChange(file)
  return false // 阻止 el-upload 默认上传
}

const roleLabel = (role: string) => {
  const map: Record<string, string> = {
    admin: '管理员',
    staff: '员工',
    customer: '会员',
  }
  return map[role] || role
}

const roleColor = (role: string) => {
  const map: Record<string, string> = {
    admin: '#f56c6c',
    staff: '#409eff',
    customer: '#67c23a',
  }
  return map[role] || '#909399'
}
</script>

<template>
  <div class="profile-page">
    <!-- 顶部卡片 — 头像 + 基本信息 -->
    <div class="hero-card">
      <div class="hero-bg"></div>
      <div class="hero-content">
        <!-- 头像区域 -->
        <div class="avatar-section">
          <div class="avatar-wrapper" v-loading="isUploading">
            <el-avatar
              :size="96"
              :src="userStore.user?.avatar || undefined"
              class="profile-avatar"
            >
              <el-icon :size="40"><UserFilled /></el-icon>
            </el-avatar>
            <el-upload
              class="avatar-uploader"
              :show-file-list="false"
              :before-upload="beforeAvatarUpload"
              accept="image/jpeg,image/png,image/gif,image/webp"
            >
              <div class="upload-overlay">
                <el-icon :size="18"><Camera /></el-icon>
                <span>更换</span>
              </div>
            </el-upload>
          </div>
          <div class="hero-info">
            <h2 class="hero-name">{{ userStore.user?.nickname }}</h2>
            <div class="hero-meta">
              <el-tag
                :color="roleColor(userStore.user?.role || '')"
                effect="dark"
                size="small"
                round
              >
                {{ roleLabel(userStore.user?.role || '') }}
              </el-tag>
              <span class="meta-desc">
                {{ userStore.user?.position_desc || '暂无职位描述' }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 详情卡片 -->
    <div class="detail-card">
      <div class="card-header">
        <h3 class="card-title">
          <el-icon><InfoFilled /></el-icon>
          账户信息
        </h3>
        <el-button
          v-if="!isEditing"
          type="primary"
          :icon="Edit"
          @click="startEdit"
          round
        >
          编辑资料
        </el-button>
        <div v-else class="edit-actions">
          <el-button @click="cancelEdit" round>取消</el-button>
          <el-button type="primary" :loading="isSaving" @click="handleSave" round>
            保存
          </el-button>
        </div>
      </div>

      <div class="card-body">
        <el-form
          ref="formRef"
          :model="editForm"
          label-width="100px"
          label-position="left"
          class="info-form"
        >
          <!-- 用户ID（不可编辑） -->
          <el-form-item label="用户 ID">
            <span class="info-value">{{ userStore.user?.id }}</span>
          </el-form-item>

          <!-- 昵称 -->
          <el-form-item
            label="昵称"
            prop="nickname"
            :rules="[{ required: true, message: '昵称不能为空', trigger: 'blur' }]"
          >
            <el-input
              v-if="isEditing"
              v-model="editForm.nickname"
              maxlength="50"
              show-word-limit
            />
            <span v-else class="info-value">{{ userStore.user?.nickname }}</span>
          </el-form-item>

          <!-- 职位描述 -->
          <el-form-item label="职位描述">
            <el-input
              v-if="isEditing"
              v-model="editForm.position_desc"
              maxlength="100"
              show-word-limit
              placeholder="如：高级宠物美容师"
            />
            <span v-else class="info-value">
              {{ userStore.user?.position_desc || '未设置' }}
            </span>
          </el-form-item>

          <!-- 角色 -->
          <el-form-item label="系统角色">
            <el-tag
              :color="roleColor(userStore.user?.role || '')"
              effect="dark"
              size="small"
              round
            >
              {{ roleLabel(userStore.user?.role || '') }}
            </el-tag>
          </el-form-item>

          <!-- 账户状态 -->
          <el-form-item label="账户状态">
            <el-tag
              :type="userStore.user?.is_active ? 'success' : 'danger'"
              effect="light"
              size="small"
              round
            >
              {{ userStore.user?.is_active ? '正常' : '已停用' }}
            </el-tag>
          </el-form-item>

          <!-- 注册时间 -->
          <el-form-item label="注册时间">
            <span class="info-value">
              {{ userStore.user?.created_at
                ? new Date(userStore.user.created_at).toLocaleString('zh-CN')
                : '-' }}
            </span>
          </el-form-item>

          <!-- 最近更新 -->
          <el-form-item label="最近更新">
            <span class="info-value">
              {{ userStore.user?.updated_at
                ? new Date(userStore.user.updated_at).toLocaleString('zh-CN')
                : '-' }}
            </span>
          </el-form-item>
        </el-form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-page {
  max-width: 720px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* ========== 顶部卡片 ========== */
.hero-card {
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  position: relative;
}

.hero-bg {
  height: 80px;
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
}

.hero-content {
  padding: 0 28px 28px;
  margin-top: -48px;
  position: relative;
}

.avatar-section {
  display: flex;
  align-items: flex-end;
  gap: 24px;
}

.avatar-wrapper {
  position: relative;
  flex-shrink: 0;
}

.profile-avatar {
  border: 4px solid #fff;
  border-radius: 50%;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.avatar-uploader {
  position: absolute;
  bottom: 0;
  right: 0;
}

.upload-overlay {
  width: 32px;
  height: 32px;
  background: rgba(0, 0, 0, 0.55);
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #fff;
  cursor: pointer;
  transition: background 0.2s;
  border: 2px solid #fff;
}

.upload-overlay span {
  font-size: 8px;
  line-height: 1;
}

.upload-overlay:hover {
  background: rgba(0, 0, 0, 0.75);
}

.hero-info {
  padding-bottom: 4px;
}

.hero-name {
  font-size: 24px;
  font-weight: 700;
  color: #1a1a2e;
  margin-bottom: 10px;
}

.hero-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.meta-desc {
  font-size: 13px;
  color: #909399;
}

/* ========== 详情卡片 ========== */
.detail-card {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 28px;
  border-bottom: 1px solid #f0f0f0;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a2e;
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
}

.edit-actions {
  display: flex;
  gap: 8px;
}

.card-body {
  padding: 28px;
}

.info-form .el-form-item {
  margin-bottom: 22px;
}

.info-value {
  color: #303133;
  font-size: 14px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #606266;
}
</style>

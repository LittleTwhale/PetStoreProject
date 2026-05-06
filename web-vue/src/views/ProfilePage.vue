<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { UserFilled, Camera, InfoFilled, Edit, Lock } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { authApi } from '@/api'
import Cropper from 'cropperjs'

const userStore = useUserStore()

const isEditing = ref(false)
const isSaving = ref(false)
const isUploading = ref(false)
const formRef = ref<FormInstance>()

const editForm = reactive({
  nickname: '',
  position_desc: '',
})

// ========== 头像裁剪 ==========
const cropDialogVisible = ref(false)
const cropImageUrl = ref('')
const cropImageRef = ref<HTMLImageElement | null>(null)
let cropper: Cropper | null = null

const openCropDialog = (dataUrl: string) => {
  cropImageUrl.value = dataUrl
  cropDialogVisible.value = true
  nextTick(() => {
    const img = cropImageRef.value
    if (img) {
      cropper = new Cropper(img)
      const selection = cropper.getCropperSelection()
      if (selection) {
        selection.aspectRatio = 1
        selection.initialAspectRatio = 1
        selection.movable = true
        selection.resizable = true
        selection.zoomable = true
      }
    }
  })
}

const destroyCropper = () => {
  if (cropper) {
    cropper.destroy()
    cropper = null
  }
}

const confirmCrop = async () => {
  if (!cropper) return
  isUploading.value = true
  cropDialogVisible.value = false
  try {
    // 获取裁剪框(selection)而不是整个画布，确保导出的是裁剪后区域
    const selection = cropper.getCropperSelection()
    if (!selection) {
      ElMessage.error('裁剪失败，未能获取裁剪区域')
      isUploading.value = false
      destroyCropper()
      return
    }

    // 对裁剪框 selection 调用 $toCanvas
    const canvas = await selection.$toCanvas({ width: 256, height: 256 })
    const blob = await new Promise<Blob>((resolve, reject) => {
      canvas.toBlob((b: Blob | null) => {
        if (b) resolve(b)
        else reject(new Error('裁剪失败'))
      }, 'image/png')
    })

    // 将 Blob 包装为 File 对象，确保后端能正确识别文件后缀和内容类型
    const file = new File([blob], 'avatar.png', { type: 'image/png' })

    const res = await authApi.uploadAvatar(file, 'avatar.png')
    if (userStore.user) {
      userStore.user.avatar = res.data.avatar_url
    }
    ElMessage.success('头像已更新')
  } catch (err: unknown) {
    ElMessage.error(
      (err as { response?: { data?: { detail?: string } } }).response?.data?.detail || '上传失败',
    )
  } finally {
    isUploading.value = false
    destroyCropper()
  }
}

const cancelCrop = () => {
  cropDialogVisible.value = false
  destroyCropper()
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
  const reader = new FileReader()
  reader.onload = (e) => {
    openCropDialog(e.target?.result as string)
  }
  reader.readAsDataURL(file)
  return false
}

// ========== 修改密码 ==========
const passwordDialogVisible = ref(false)
const passwordFormRef = ref<FormInstance>()
const passwordLoading = ref(false)

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: '',
})

const validateConfirmPassword = (
  _rule: import('element-plus').FormItemRule,
  value: string,
  callback: (error?: Error) => void,
) => {
  if (value !== passwordForm.new_password) {
    callback(new Error('两次输入的新密码不一致'))
  } else {
    callback()
  }
}

const passwordRules: FormRules = {
  old_password: [{ required: true, message: '请输入旧密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '新密码至少6位', trigger: 'blur' },
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' },
  ],
}

const resetPasswordForm = () => {
  passwordForm.old_password = ''
  passwordForm.new_password = ''
  passwordForm.confirm_password = ''
}

const handleChangePassword = async () => {
  if (!passwordFormRef.value) return
  const valid = await passwordFormRef.value.validate().catch(() => false)
  if (!valid) return

  passwordLoading.value = true
  try {
    await authApi.changePassword({
      old_password: passwordForm.old_password,
      new_password: passwordForm.new_password,
    })
    ElMessage.success('密码已更新，请牢记新密码')
    passwordDialogVisible.value = false
    resetPasswordForm()
  } catch (err: unknown) {
    ElMessage.error(
      (err as { response?: { data?: { detail?: string } } }).response?.data?.detail ||
        '修改密码失败',
    )
  } finally {
    passwordLoading.value = false
  }
}

// ========== 用户信息 ==========
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
      (err as { response?: { data?: { detail?: string } } }).response?.data?.detail || '更新失败',
    )
  } finally {
    isSaving.value = false
  }
}

const roleLabel = (role: string) => {
  const map: Record<string, string> = {
    admin: '管理员',
    staff: '店员',
    customer: '顾客',
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
              :size="108"
              :src="userStore.user?.avatar || undefined"
              class="profile-avatar"
            >
              <el-icon :size="48"><UserFilled /></el-icon>
            </el-avatar>
            <el-upload
              class="avatar-uploader"
              :show-file-list="false"
              :before-upload="beforeAvatarUpload"
              accept="image/jpeg,image/png,image/gif,image/webp"
            >
              <div class="upload-overlay">
                <el-icon :size="18"><Camera /></el-icon>
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
                class="role-tag"
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
          <div class="icon-wrapper">
            <el-icon><InfoFilled /></el-icon>
          </div>
          账户信息
        </h3>
        <div class="header-actions">
          <el-button class="action-btn" :icon="Lock" @click="passwordDialogVisible = true" round>
            修改密码
          </el-button>
          <el-button
            v-if="!isEditing"
            type="primary"
            class="action-btn"
            :icon="Edit"
            @click="startEdit"
            round
          >
            编辑资料
          </el-button>
          <div v-else class="edit-actions">
            <el-button @click="cancelEdit" round>取消</el-button>
            <el-button type="primary" :loading="isSaving" @click="handleSave" round>
              保存修改
            </el-button>
          </div>
        </div>
      </div>

      <div class="card-body">
        <el-form
          ref="formRef"
          :model="editForm"
          label-width="110px"
          label-position="left"
          class="info-form"
          :class="{ 'is-editing': isEditing }"
        >
          <!-- 用户ID（不可编辑） -->
          <el-form-item label="用户 ID">
            <span class="info-value id-badge">{{ userStore.user?.id }}</span>
          </el-form-item>

          <!-- 登录账号 -->
          <el-form-item label="登录账号">
            <span class="info-value">{{ userStore.user?.identifier || '未绑定' }}</span>
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
              placeholder="请输入您的昵称"
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
            <span v-else class="info-value text-muted">
              {{ userStore.user?.position_desc || '未设置' }}
            </span>
          </el-form-item>

          <!-- 角色 -->
          <el-form-item label="系统角色">
            <el-tag
              :color="roleColor(userStore.user?.role || '')"
              effect="light"
              size="small"
              round
            >
              {{ roleLabel(userStore.user?.role || '') }}
            </el-tag>
          </el-form-item>

          <!-- 账户状态 -->
          <el-form-item label="账户状态">
            <div class="status-indicator">
              <span
                class="status-dot"
                :class="userStore.user?.is_active ? 'active' : 'inactive'"
              ></span>
              {{ userStore.user?.is_active ? '正常使用中' : '已停用' }}
            </div>
          </el-form-item>

          <!-- 注册时间 -->
          <el-form-item label="注册时间">
            <span class="info-value text-sm">
              {{
                userStore.user?.created_at
                  ? new Date(userStore.user.created_at).toLocaleString('zh-CN', { hour12: false })
                  : '-'
              }}
            </span>
          </el-form-item>

          <!-- 最近更新 -->
          <el-form-item label="最近更新">
            <span class="info-value text-sm">
              {{
                userStore.user?.updated_at
                  ? new Date(userStore.user.updated_at).toLocaleString('zh-CN', { hour12: false })
                  : '-'
              }}
            </span>
          </el-form-item>
        </el-form>
      </div>
    </div>

    <!-- ========== 头像裁剪弹窗 ========== -->
    <el-dialog
      v-model="cropDialogVisible"
      title="裁剪头像"
      width="560px"
      :close-on-click-modal="false"
      class="custom-dialog"
      @closed="destroyCropper"
    >
      <div class="crop-container">
        <img ref="cropImageRef" :src="cropImageUrl" alt="裁剪预览" />
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="cancelCrop" round>取消</el-button>
          <el-button type="primary" @click="confirmCrop" round>确认裁剪</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- ========== 修改密码弹窗 ========== -->
    <el-dialog
      v-model="passwordDialogVisible"
      title="修改密码"
      width="440px"
      :close-on-click-modal="false"
      destroy-on-close
      class="custom-dialog"
      @closed="resetPasswordForm"
    >
      <el-form
        ref="passwordFormRef"
        :model="passwordForm"
        :rules="passwordRules"
        label-width="100px"
        label-position="top"
        class="password-form"
      >
        <el-form-item label="旧密码" prop="old_password">
          <el-input
            v-model="passwordForm.old_password"
            type="password"
            placeholder="请输入当前密码"
            show-password
            maxlength="100"
          />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input
            v-model="passwordForm.new_password"
            type="password"
            placeholder="至少6位新密码"
            show-password
            maxlength="100"
          />
        </el-form-item>
        <el-form-item label="确认新密码" prop="confirm_password">
          <el-input
            v-model="passwordForm.confirm_password"
            type="password"
            placeholder="请再次输入新密码"
            show-password
            maxlength="100"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="passwordDialogVisible = false" round>取消</el-button>
          <el-button type="primary" :loading="passwordLoading" @click="handleChangePassword" round>
            确认修改
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.profile-page {
  max-width: 760px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 20px 0;
}

/* ========== 顶部卡片 ========== */
.hero-card {
  background: #ffffff;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
  position: relative;
  transition:
    transform 0.3s ease,
    box-shadow 0.3s ease;
}

.hero-card:hover {
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.08);
}

.hero-bg {
  height: 120px;
  /* 更具现代感的渐变背景 */
  background: linear-gradient(120deg, #a1c4fd 0%, #c2e9fb 100%);
  position: relative;
}

.hero-bg::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI4IiBoZWlnaHQ9IjgiPgo8cmVjdCB3aWR0aD0iOCIgaGVpZ2h0PSI4IiBmaWxsPSIjZmZmIiBmaWxsLW9wYWNpdHk9IjAuMSIvPgo8L3N2Zz4=');
  opacity: 0.3;
}

.hero-content {
  padding: 0 32px 32px;
  margin-top: -54px;
  position: relative;
  z-index: 2;
}

.avatar-section {
  display: flex;
  align-items: flex-end;
  gap: 28px;
}

.avatar-wrapper {
  position: relative;
  flex-shrink: 0;
}

.profile-avatar {
  border: 4px solid #ffffff;
  background-color: #f0f2f5;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.avatar-wrapper:hover .profile-avatar {
  transform: scale(1.02);
}

.avatar-uploader {
  position: absolute;
  bottom: 4px;
  right: 4px;
}

.upload-overlay {
  width: 36px;
  height: 36px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #409eff;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid #e4e7ed;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.upload-overlay:hover {
  background: #409eff;
  color: #ffffff;
  transform: scale(1.1);
}

.hero-info {
  padding-bottom: 8px;
}

.hero-name {
  font-size: 26px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 12px 0;
  letter-spacing: 0.5px;
}

.hero-meta {
  display: flex;
  align-items: center;
  gap: 16px;
}

.role-tag {
  border: none;
  font-weight: 600;
  padding: 0 12px;
}

.meta-desc {
  font-size: 14px;
  color: #606266;
  background: #f5f7fa;
  padding: 4px 12px;
  border-radius: 12px;
}

/* ========== 裁剪弹窗 ========== */
.crop-container {
  width: 100%;
  height: 400px;
  background-image: radial-gradient(#dcdfe6 1px, transparent 1px);
  background-size: 20px 20px;
  background-color: #f0f2f5;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: inset 0 2px 10px rgba(0, 0, 0, 0.04);
}

.crop-container img {
  display: block;
  max-width: 100%;
  max-height: 100%;
}

/* 强制 Cropper v2 的自定义组件铺满可用空间 */
:deep(cropper-canvas) {
  width: 100%;
  height: 100%;
}

:deep(.cropper-bg) {
  background-image: none !important;
  background-color: transparent !important;
}

/* ========== 详情卡片 ========== */
.detail-card {
  background: #ffffff;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 32px;
  border-bottom: 1px solid #f0f2f5;
  background: #fafafa;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0;
}

.icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: #ecf5ff;
  color: #409eff;
  border-radius: 8px;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.action-btn {
  font-weight: 500;
}

.edit-actions {
  display: flex;
  gap: 12px;
  animation: fadeIn 0.3s ease;
}

.card-body {
  padding: 32px;
}

/* ========== 表单与只读展示优化 ========== */
.info-form {
  max-width: 600px;
}

.info-form .el-form-item {
  margin-bottom: 0;
  padding: 16px 0;
  border-bottom: 1px dashed #ebeef5;
  transition: background-color 0.3s ease;
}

.info-form .el-form-item:last-child {
  border-bottom: none;
}

.info-form:not(.is-editing) .el-form-item:hover {
  background-color: #fcfcfd;
  border-radius: 8px;
  padding-left: 8px;
  padding-right: 8px;
  margin-left: -8px;
  margin-right: -8px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #8c939d;
  align-items: center;
}

.info-value {
  color: #303133;
  font-size: 15px;
  font-weight: 500;
}

.text-muted {
  color: #909399;
  font-weight: 400;
}

.text-sm {
  font-size: 14px;
  color: #606266;
}

.id-badge {
  background: #f4f4f5;
  padding: 4px 10px;
  border-radius: 6px;
  font-family: monospace;
  color: #606266;
  font-size: 14px;
}

/* 状态圆点 */
.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.status-dot.active {
  background-color: #67c23a;
  box-shadow: 0 0 0 3px rgba(103, 194, 58, 0.2);
}

.status-dot.inactive {
  background-color: #f56c6c;
}

/* 弹窗样式优化 */
:deep(.custom-dialog) {
  border-radius: 16px;
  overflow: hidden;
}

:deep(.custom-dialog .el-dialog__header) {
  padding: 24px 24px 16px;
  margin-right: 0;
  border-bottom: 1px solid #f0f2f5;
}

:deep(.custom-dialog .el-dialog__title) {
  font-weight: 600;
}

.dialog-footer {
  padding-top: 10px;
}

/* 动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-5px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>

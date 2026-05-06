<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { User, Lock, UserFilled, Present, Check } from '@element-plus/icons-vue'
import { authApi } from '@/api'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const activeTab = ref<'login' | 'register'>('login')
const isLoading = ref(false)
const loginFormRef = ref<FormInstance>()
const registerFormRef = ref<FormInstance>()

// 登录表单
const loginForm = reactive({
  identifier: '',
  password: '',
})

const loginRules: FormRules = {
  identifier: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' },
  ],
}

// 注册表单
const registerForm = reactive({
  nickname: '',
  identifier: '',
  password: '',
  confirmPassword: '',
})

const validateConfirmPass = (
  _rule: import('element-plus').FormItemRule,
  value: string,
  callback: (error?: Error) => void,
) => {
  if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const registerRules: FormRules = {
  nickname: [{ required: true, message: '请输入昵称', trigger: 'blur' }],
  identifier: [
    { required: true, message: '请输入账号', trigger: 'blur' },
    { min: 3, message: '账号至少3位', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPass, trigger: 'blur' },
  ],
}

// 登录
const handleLogin = async () => {
  if (!loginFormRef.value) return
  const valid = await loginFormRef.value.validate().catch(() => false)
  if (!valid) return

  isLoading.value = true
  try {
    const res = await authApi.login(loginForm)
    localStorage.setItem('token', res.data.access_token)
    await userStore.fetchUser()
    ElMessage.success('登录成功')
    await router.push('/dashboard')
  } catch (err: unknown) {
    const msg =
      (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
      '登录失败'
    ElMessage.error(msg)
  } finally {
    isLoading.value = false
  }
}

// 注册
const handleRegister = async () => {
  if (!registerFormRef.value) return
  const valid = await registerFormRef.value.validate().catch(() => false)
  if (!valid) return

  isLoading.value = true
  try {
    const res = await authApi.register({
      identifier: registerForm.identifier,
      password: registerForm.password,
      nickname: registerForm.nickname,
    })
    localStorage.setItem('token', res.data.access_token)
    await userStore.fetchUser()
    ElMessage.success('注册成功，欢迎加入！')
    await router.push('/dashboard')
  } catch (err: unknown) {
    const msg =
      (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
      '注册失败'
    ElMessage.error(msg)
  } finally {
    isLoading.value = false
  }
}

const switchTab = (tab: 'login' | 'register') => {
  activeTab.value = tab
}
</script>

<template>
  <div class="login-page">
    <!-- 背景装饰 -->
    <div class="bg-decoration">
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
      <div class="circle circle-3"></div>
    </div>

    <!-- 主卡片 -->
    <div class="auth-card">
      <!-- 左侧品牌区 -->
      <div class="brand-panel">
        <div class="brand-content">
          <div class="brand-icon">
            <el-icon :size="48"><Present /></el-icon>
          </div>
          <h1 class="brand-name">非诚勿宠</h1>
          <p class="brand-desc">专业 · 贴心的全栈宠物服务平台</p>
          <div class="brand-features">
            <div class="feature-item">
              <el-icon><Check /></el-icon>
              <span>宠物用品一站式采购</span>
            </div>
            <div class="feature-item">
              <el-icon><Check /></el-icon>
              <span>专业宠物美容护理</span>
            </div>
            <div class="feature-item">
              <el-icon><Check /></el-icon>
              <span>贴心医疗服务保障</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧表单区 -->
      <div class="form-panel">
        <!-- Tab 切换 -->
        <div class="tab-header">
          <button
            :class="['tab-btn', { active: activeTab === 'login' }]"
            @click="switchTab('login')"
          >
            登录
          </button>
          <button
            :class="['tab-btn', { active: activeTab === 'register' }]"
            @click="switchTab('register')"
          >
            注册
          </button>
        </div>

        <!-- 登录表单 -->
        <transition name="fade" mode="out-in">
          <div v-if="activeTab === 'login'" key="login" class="form-wrapper">
            <h3 class="form-title">欢迎回来</h3>
            <p class="form-subtitle">登录您的账户继续使用</p>

            <el-form
              ref="loginFormRef"
              :model="loginForm"
              :rules="loginRules"
              @submit.prevent="handleLogin"
            >
              <el-form-item prop="identifier">
                <el-input
                  v-model="loginForm.identifier"
                  placeholder="账号 / 邮箱 / 手机号"
                  size="large"
                  :prefix-icon="User"
                  clearable
                />
              </el-form-item>

              <el-form-item prop="password">
                <el-input
                  v-model="loginForm.password"
                  type="password"
                  placeholder="请输入密码"
                  size="large"
                  :prefix-icon="Lock"
                  show-password
                  @keyup.enter="handleLogin"
                />
              </el-form-item>

              <el-form-item>
                <el-button
                  type="primary"
                  size="large"
                  class="submit-btn"
                  :loading="isLoading"
                  @click="handleLogin"
                >
                  登 录
                </el-button>
              </el-form-item>
            </el-form>
          </div>

          <!-- 注册表单 -->
          <div v-else key="register" class="form-wrapper">
            <h3 class="form-title">创建账户</h3>
            <p class="form-subtitle">注册成为非诚勿宠会员</p>

            <el-form
              ref="registerFormRef"
              :model="registerForm"
              :rules="registerRules"
              @submit.prevent="handleRegister"
            >
              <el-form-item prop="nickname">
                <el-input
                  v-model="registerForm.nickname"
                  placeholder="请输入昵称"
                  size="large"
                  :prefix-icon="UserFilled"
                  clearable
                />
              </el-form-item>

              <el-form-item prop="identifier">
                <el-input
                  v-model="registerForm.identifier"
                  placeholder="请输入账号"
                  size="large"
                  :prefix-icon="User"
                  clearable
                />
              </el-form-item>

              <el-form-item prop="password">
                <el-input
                  v-model="registerForm.password"
                  type="password"
                  placeholder="请输入密码（至少6位）"
                  size="large"
                  :prefix-icon="Lock"
                  show-password
                />
              </el-form-item>

              <el-form-item prop="confirmPassword">
                <el-input
                  v-model="registerForm.confirmPassword"
                  type="password"
                  placeholder="请再次输入密码"
                  size="large"
                  :prefix-icon="Lock"
                  show-password
                  @keyup.enter="handleRegister"
                />
              </el-form-item>

              <el-form-item>
                <el-button
                  type="primary"
                  size="large"
                  class="submit-btn"
                  :loading="isLoading"
                  @click="handleRegister"
                >
                  注 册
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  position: relative;
  overflow: hidden;
}

/* 背景装饰 */
.bg-decoration {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.08;
  background: #fff;
}

.circle-1 {
  width: 500px;
  height: 500px;
  top: -150px;
  right: -100px;
}

.circle-2 {
  width: 300px;
  height: 300px;
  bottom: -80px;
  left: -80px;
}

.circle-3 {
  width: 200px;
  height: 200px;
  top: 50%;
  left: 60%;
}

/* 主卡片 */
.auth-card {
  display: flex;
  width: 920px;
  min-height: 560px;
  background: #fff;
  border-radius: 20px;
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.25);
  overflow: hidden;
  position: relative;
  z-index: 1;
}

/* 左侧品牌区 */
.brand-panel {
  width: 400px;
  background: linear-gradient(135deg, #409eff 0%, #337ecc 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px;
  position: relative;
  overflow: hidden;
}

.brand-panel::before {
  content: '';
  position: absolute;
  width: 300px;
  height: 300px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.06);
  top: -60px;
  right: -80px;
}

.brand-panel::after {
  content: '';
  position: absolute;
  width: 200px;
  height: 200px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.04);
  bottom: -40px;
  left: -40px;
}

.brand-content {
  text-align: center;
  color: #fff;
  position: relative;
  z-index: 1;
}

.brand-icon {
  margin-bottom: 16px;
  display: inline-flex;
  padding: 16px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 16px;
}

.brand-name {
  font-size: 32px;
  font-weight: 800;
  letter-spacing: 2px;
  margin-bottom: 8px;
}

.brand-desc {
  font-size: 14px;
  opacity: 0.85;
  margin-bottom: 32px;
}

.brand-features {
  text-align: left;
  display: inline-flex;
  flex-direction: column;
  gap: 14px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  opacity: 0.9;
}

.feature-item .el-icon {
  color: #67c23a;
}

/* 右侧表单区 */
.form-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 40px 48px;
}

.tab-header {
  display: flex;
  gap: 0;
  margin-bottom: 32px;
  background: #f0f2f5;
  border-radius: 10px;
  padding: 4px;
}

.tab-btn {
  flex: 1;
  padding: 10px 0;
  border: none;
  background: transparent;
  font-size: 15px;
  font-weight: 500;
  color: #909399;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.3s;
}

.tab-btn.active {
  background: #fff;
  color: #409eff;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.form-wrapper {
  flex: 1;
}

.form-title {
  font-size: 22px;
  font-weight: 700;
  color: #1a1a2e;
  margin-bottom: 6px;
}

.form-subtitle {
  font-size: 13px;
  color: #909399;
  margin-bottom: 28px;
}

.submit-btn {
  width: 100%;
  height: 44px;
  font-size: 15px;
  letter-spacing: 4px;
  border-radius: 10px;
}

/* 动画 */
.fade-enter-active,
.fade-leave-active {
  transition: all 0.25s ease;
}
.fade-enter-from {
  opacity: 0;
  transform: translateX(20px);
}
.fade-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}
</style>

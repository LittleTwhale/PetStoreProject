<template>
  <div class="login-container">
    <div class="login-box">
      <!-- 左侧品牌展示区 (可替换为你的宠物店海报) -->
      <div class="login-banner">
        <h2>非诚勿宠</h2>
        <p>专业、贴心的全栈宠物服务平台</p>
      </div>

      <!-- 右侧登录表单区 -->
      <div class="login-form-wrapper">
        <h3 class="form-title">欢迎登录</h3>
        <el-form ref="formRef" :model="loginForm" :rules="rules" @submit.prevent="handleLogin">
          <el-form-item prop="identifier">
            <el-input
              v-model="loginForm.identifier"
              placeholder="请输入账号 / 邮箱 / 手机号"
              :prefix-icon="'User'"
              size="large"
            />
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              :prefix-icon="'Lock'"
              show-password
              size="large"
            />
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              native-type="submit"
              class="login-btn"
              size="large"
              :loading="isLoading"
            >
              登 录
            </el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const router = useRouter() //[cite: 1]
const isLoading = ref(false)

const loginForm = ref({
  identifier: '', //[cite: 1]
  password: '', //[cite: 1]
})

// 表单验证规则
const rules = {
  identifier: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const handleLogin = async () => {
  if (!loginForm.value.identifier || !loginForm.value.password) return

  isLoading.value = true
  try {
    const response = await axios.post('/api/auth/login', loginForm.value) //[cite: 1]
    const token = response.data.access_token //[cite: 1]
    localStorage.setItem('token', token) //[cite: 1]

    ElMessage.success('登录成功')
    await router.push('/dashboard') // 登录后跳转到主界面
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      //[cite: 1]
      ElMessage.error(error.response.data.detail || '账号或密码错误') //[cite: 1]
    } else {
      ElMessage.error('网络请求失败，请稍后再试') //[cite: 1]
    }
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); /* 现代感渐变背景 */
}

.login-box {
  display: flex;
  width: 800px;
  height: 450px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.login-banner {
  flex: 1;
  background: #409eff;
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 40px;
  text-align: center;
}

.login-banner h2 {
  font-size: 32px;
  margin-bottom: 15px;
  letter-spacing: 2px;
}

.login-form-wrapper {
  flex: 1;
  padding: 50px 40px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.form-title {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
  font-size: 24px;
}

.login-btn {
  width: 100%;
  margin-top: 10px;
}
</style>

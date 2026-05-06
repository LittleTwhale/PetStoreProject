<template>
  <div class="login-container">
    <h2>系统登录</h2>
    <form @submit.prevent="handleLogin">
      <div>
        <label>账号：</label>
        <input
          v-model="loginForm.identifier"
          type="text"
          placeholder="请输入账号/手机号/邮箱"
          required
        />
      </div>
      <div>
        <label>密码：</label>
        <input v-model="loginForm.password" type="password" placeholder="请输入密码" required />
      </div>
      <button type="submit">登录</button>
      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const loginForm = ref({
  identifier: '',
  password: '',
})
const errorMessage = ref('')

const handleLogin = async () => {
  try {
    errorMessage.value = ''
    // 请求后端的 /api/auth/login 接口
    const response = await axios.post('/api/auth/login', loginForm.value)

    // 登录成功，后端会返回 access_token，将其保存到 localStorage
    const token = response.data.access_token
    localStorage.setItem('token', token)

    // 跳转到个人信息界面
    await router.push('/profile')
  } catch (error) {
    // 使用 axios 提供的类型守卫
    if (axios.isAxiosError(error)) {
      // 此时在这个代码块内，TS 知道 error 是 AxiosError 类型
      if (error.response && error.response.status === 401) {
        errorMessage.value = error.response.data.detail || '账号或密码错误'
      } else {
        errorMessage.value = '登录失败，请稍后重试'
      }
    } else {
      // 处理非 Axios 错误（例如代码逻辑崩溃）
      errorMessage.value = '发生未知错误'
      console.error(error)
    }
  }
}
</script>

<style scoped>
.login-container {
  max-width: 300px;
  margin: 100px auto;
  text-align: center;
}
form div {
  margin-bottom: 15px;
  text-align: left;
}
input {
  width: 100%;
  padding: 8px;
  margin-top: 5px;
}
button {
  width: 100%;
  padding: 10px;
  background-color: #4caf50;
  color: white;
  border: none;
  cursor: pointer;
}
.error {
  color: red;
  font-size: 14px;
}
</style>

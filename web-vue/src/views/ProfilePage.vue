<template>
  <div class="profile-container" v-if="userInfo">
    <h2>个人信息</h2>
    <div class="info-card">
      <p><strong>用户ID：</strong> {{ userInfo.id }}</p>
      <p><strong>昵称：</strong> {{ userInfo.nickname }}</p>
      <p><strong>系统角色：</strong> {{ userInfo.role }}</p>
      <p><strong>职位描述：</strong> {{ userInfo.position_desc || '暂无' }}</p>
      <p><strong>账户状态：</strong> {{ userInfo.is_active ? '正常' : '已停用' }}</p>
      <p><strong>创建时间：</strong> {{ new Date(userInfo.created_at).toLocaleString() }}</p>
    </div>
    <button @click="handleLogout" class="logout-btn">退出登录</button>
  </div>
  <div v-else>加载中...</div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

//  定义用户信息接口，匹配在模板中使用的字段
interface User {
  id: number | string
  nickname: string
  role: string
  position_desc: string | null
  is_active: boolean
  created_at: string
}

const router = useRouter()

// 为 ref 增加类型定义
// 这样 TS 就知道 userInfo.value 以后会有 id, nickname 等属性了
const userInfo = ref<User | null>(null)

onMounted(async () => {
  const token = localStorage.getItem('token')
  if (!token) {
    await router.push('/login')
    return
  }

  try {
    // 请求后端 /api/auth/me 接口，并在请求头携带有效的 Bearer Token
    const response = await axios.get('/api/auth/me', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
    // 赋值时，TS 会自动检查 response.data 是否符合 User 接口
    userInfo.value = response.data
  } catch (error) {
    console.error('获取用户信息失败', error)
    // 如果 Token 失效或请求失败，清除状态并退回登录页
    localStorage.removeItem('token')
    await router.push('/login')
  }
})

const handleLogout = () => {
  localStorage.removeItem('token')
  router.push('/login')
}
</script>

<style scoped>
.profile-container {
  max-width: 400px;
  margin: 50px auto;
}
.info-card {
  border: 1px solid #ddd;
  padding: 20px;
  border-radius: 8px;
  text-align: left;
}
p {
  margin: 10px 0;
}
.logout-btn {
  margin-top: 20px;
  padding: 10px 20px;
  background-color: #f44336;
  color: white;
  border: none;
  cursor: pointer;
  border-radius: 4px;
}
</style>

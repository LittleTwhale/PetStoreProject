<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const isCollapse = ref(false)
const isMobile = ref(window.innerWidth < 768)

window.addEventListener('resize', () => {
  isMobile.value = window.innerWidth < 768
  if (isMobile.value) isCollapse.value = true
})

const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value
}

const menuItems = computed(() => {
  const items = [
    { index: '/dashboard', icon: 'Odometer', label: '数据工作台' },
    { index: '/profile', icon: 'UserFilled', label: '个人中心' },
  ]
  if (userStore.user?.role === 'admin') {
    items.push({ index: '/admin', icon: 'Setting', label: '用户管理' })
  }
  return items
})

const handleCommand = async (command: string) => {
  if (command === 'logout') {
    userStore.logout()
    router.push('/login')
    ElMessage.success('已退出登录')
  } else if (command === 'profile') {
    router.push('/profile')
  }
}

onMounted(async () => {
  if (!userStore.user) {
    try {
      await userStore.fetchUser()
    } catch {
      router.push('/login')
    }
  }
})
</script>

<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapse ? '64px' : '220px'" class="aside">
      <!-- Logo 区域 -->
      <div class="logo-area" :class="{ collapsed: isCollapse }">
        <el-icon :size="28" color="#fff">
          <Present />
        </el-icon>
        <transition name="fade">
          <span v-show="!isCollapse" class="logo-text">非诚勿宠</span>
        </transition>
      </div>

      <!-- 菜单 -->
      <el-menu
        :default-active="route.path"
        :collapse="isCollapse"
        :collapse-transition="false"
        router
        class="sidebar-menu"
        background-color="transparent"
        text-color="rgba(255,255,255,0.7)"
        active-text-color="#fff"
      >
        <el-menu-item
          v-for="item in menuItems"
          :key="item.index"
          :index="item.index"
        >
          <el-icon :size="18">
            <component :is="item.icon" />
          </el-icon>
          <template #title>
            <span class="menu-title">{{ item.label }}</span>
          </template>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 右侧主体 -->
    <el-container class="main-container">
      <!-- 顶部栏 -->
      <el-header class="top-header">
        <div class="header-left">
          <el-button
            class="collapse-btn"
            :icon="isCollapse ? 'Expand' : 'Fold'"
            text
            @click="toggleSidebar"
          />
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="route.path !== '/'">
              {{ route.meta.title || route.name }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="header-right">
          <!-- 用户信息 -->
          <el-dropdown trigger="click" @command="handleCommand">
            <div class="user-area">
              <el-avatar
                :size="34"
                :src="userStore.user?.avatar || undefined"
                class="user-avatar"
              >
                <el-icon :size="18"><UserFilled /></el-icon>
              </el-avatar>
              <span class="user-name">{{ userStore.user?.nickname || '用户' }}</span>
              <el-icon class="arrow-icon"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人信息
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 内容区 -->
      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade-slide" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.layout-container {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

/* ========== 侧边栏 ========== */
.aside {
  background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
  transition: width 0.3s ease;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 12px rgba(0, 0, 0, 0.15);
  z-index: 10;
}

.logo-area {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  padding: 0 16px;
  flex-shrink: 0;
}

.logo-area.collapsed {
  padding: 0;
}

.logo-text {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  letter-spacing: 1px;
  white-space: nowrap;
}

/* 侧边栏菜单 */
.sidebar-menu {
  flex: 1;
  border-right: none !important;
  padding: 8px 0;
}

.sidebar-menu .el-menu-item {
  margin: 4px 8px;
  border-radius: 8px;
  height: 44px;
  line-height: 44px;
  transition: all 0.2s ease;
}

.sidebar-menu .el-menu-item:hover {
  background: rgba(255, 255, 255, 0.08) !important;
}

.sidebar-menu .el-menu-item.is-active {
  background: rgba(64, 158, 255, 0.25) !important;
  color: #fff !important;
  font-weight: 600;
}

.sidebar-menu .el-menu-item.is-active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 20px;
  background: #409eff;
  border-radius: 0 2px 2px 0;
}

.menu-title {
  font-size: 14px;
}

/* 折叠状态 */
.el-menu--collapse {
  width: 64px;
}

.el-menu--collapse .el-menu-item {
  justify-content: center;
  padding: 0 !important;
}

/* ========== 顶部栏 ========== */
.main-container {
  flex-direction: column;
}

.top-header {
  height: 56px;
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  flex-shrink: 0;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.collapse-btn {
  font-size: 18px;
  color: #606266;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-area {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 8px;
  transition: background 0.2s;
}

.user-area:hover {
  background: #f5f7fa;
}

.user-avatar {
  flex-shrink: 0;
}

.user-name {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
}

.arrow-icon {
  font-size: 12px;
  color: #909399;
}

/* ========== 内容区 ========== */
.main-content {
  background: #f0f2f5;
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

/* ========== 动画 ========== */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}
.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(10px);
}
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useStoreStore } from '@/stores/store'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const storeStore = useStoreStore()

const isCollapse = ref(false)
const isMobile = ref(window.innerWidth < 768)
const mobileMenuOpen = ref(false)

window.addEventListener('resize', () => {
  isMobile.value = window.innerWidth < 768
  if (isMobile.value) isCollapse.value = true
})

const toggleSidebar = () => {
  if (isMobile.value) {
    mobileMenuOpen.value = !mobileMenuOpen.value
  } else {
    isCollapse.value = !isCollapse.value
  }
}

const closeMobileMenu = () => {
  mobileMenuOpen.value = false
}

// 移动端路由切换后自动关闭侧栏
watch(() => route.path, () => {
  if (isMobile.value) {
    mobileMenuOpen.value = false
  }
})

const menuItems = computed(() => {
  const items = [
    { index: '/dashboard', icon: 'Odometer', label: '数据工作台' },
    { index: '/profile', icon: 'UserFilled', label: '个人中心' },
  ]
  // 管理员和店员都可以使用客户与宠物管理
  if (userStore.user?.role === 'admin' || userStore.user?.role === 'staff') {
    items.push(
      { index: '/customers', icon: 'UserFilled', label: '客户档案' },
      { index: '/pets', icon: 'Present', label: '宠物台账' },
      { index: '/inventory-items', icon: 'Goods', label: '库存物品' },
      { index: '/inventory-logs', icon: 'Document', label: '库存流水' },
      { index: '/products', icon: 'Present', label: '商品管理' },
      { index: '/services', icon: 'Scissor', label: '服务管理' },
      { index: '/orders', icon: 'Document', label: '订单管理' },
    )
  }
  if (userStore.user?.role === 'admin') {
    items.push(
      { index: '/admin', icon: 'Setting', label: '用户管理' },
      { index: '/stores', icon: 'Shop', label: '门店管理' },
      { index: '/inventory-categories', icon: 'Collection', label: '库存分类' },
    )
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
  // 店员/管理员登录后加载门店列表
  if (userStore.user?.role === 'staff' || userStore.user?.role === 'admin') {
    storeStore.fetchMyStores()
  }
})
</script>

<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <!-- 移动端遮罩层 -->
    <div
      v-if="isMobile && mobileMenuOpen"
      class="mobile-overlay"
      @click="closeMobileMenu"
    ></div>

    <el-aside
      :width="isCollapse && !isMobile ? '64px' : '220px'"
      class="aside"
      :class="{ 'mobile-open': isMobile && mobileMenuOpen }"
    >
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
          <!-- 移动端汉堡菜单按钮 -->
          <el-button
            v-if="isMobile"
            class="hamburger-btn"
            text
            @click="toggleSidebar"
          >
            <el-icon :size="22">
              <component :is="mobileMenuOpen ? 'Close' : 'Menu'" />
            </el-icon>
          </el-button>
          <!-- 桌面端折叠按钮 -->
          <el-button
            v-else
            class="collapse-btn"
            :icon="isCollapse ? 'Expand' : 'Fold'"
            text
            @click="toggleSidebar"
          />
          <!-- 移动端隐藏面包屑 -->
          <el-breadcrumb v-if="!isMobile" separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="route.path !== '/'">
              {{ route.meta.title || route.name }}
            </el-breadcrumb-item>
          </el-breadcrumb>
          <span v-else class="mobile-page-title">
            {{ route.meta.title || route.name || '非诚勿宠' }}
          </span>
        </div>

        <div class="header-right">
          <!-- 门店切换器 -->
          <el-select
            v-if="userStore.user?.role === 'staff' || userStore.user?.role === 'admin'"
            :model-value="storeStore.currentStoreId"
            placeholder="选择门店"
            class="store-switcher"
            size="small"
            @change="(val: number) => storeStore.switchStore(val)"
          >
            <el-option
              v-for="s in storeStore.myStores"
              :key="s.id"
              :label="s.name"
              :value="s.id"
            >
              <span>{{ s.name }}</span>
              <span style="color: #909399; font-size: 12px; margin-left: 6px">{{ s.code }}</span>
            </el-option>
          </el-select>
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
  gap: 16px;
}

.store-switcher {
  width: 180px;
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

/* ========== 移动端样式 ========== */
/* 遮罩层 */
.mobile-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 99;
  animation: fadeIn 0.3s ease;
}

/* 移动端侧边栏弹出 */
.aside.mobile-open {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  z-index: 100;
  width: 220px !important;
  animation: slideIn 0.3s ease;
}

/* 移动端默认隐藏侧边栏 */
@media (max-width: 767px) {
  .aside:not(.mobile-open) {
    display: none;
  }
}

/* 移动端汉堡按钮 */
.hamburger-btn {
  color: #606266;
}

/* 移动端页面标题 */
.mobile-page-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

/* 响应式顶部栏 */
@media (max-width: 767px) {
  .top-header {
    padding: 0 12px;
  }

  .header-right {
    gap: 8px;
  }

  .store-switcher {
    width: 130px;
  }

  .user-name {
    display: none;
  }

  .arrow-icon {
    display: none;
  }
}

/* 响应式内容区 */
@media (max-width: 767px) {
  .main-content {
    padding: 12px;
  }
}

/* ========== 动画 ========== */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideIn {
  from { transform: translateX(-100%); }
  to { transform: translateX(0); }
}

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

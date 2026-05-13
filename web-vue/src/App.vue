<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <RouterView />
</template>

<style>
/* 全局重置 */
*,
*::before,
*::after {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html,
body,
#app {
  height: 100%;
  width: 100%;
  font-family:
    'Inter',
    'PingFang SC',
    'Helvetica Neue',
    Helvetica,
    Arial,
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #303133;
  background: #f0f2f5;
}

/* 滚动条美化 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.12);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.2);
}

/* Element Plus 全局覆盖 */
.el-button {
  font-weight: 500;
}

.el-card {
  border-radius: 12px !important;
}

/* ========== 全局响应式：移动端弹窗适配 ========== */
@media (max-width: 767px) {
  .el-dialog {
    width: 90% !important;
    max-width: 500px;
    margin: 0 auto;
  }

  .el-dialog .el-dialog__body {
    padding: 16px;
  }

  .el-message-box {
    width: 85% !important;
    max-width: 400px;
  }
}
</style>

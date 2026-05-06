import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

const app = createApp(App)

// 注册状态管理 Pinia 和 路由 Router
app.use(createPinia())
app.use(router)

app.mount('#app')

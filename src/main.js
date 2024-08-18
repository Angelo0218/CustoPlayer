import { createApp } from 'vue'
import App from './App.vue'
import './style.css'
import router from './router/router.js'
import '@fortawesome/fontawesome-free/css/all.css'
import '@fortawesome/fontawesome-free/js/all.js'
import axios from 'axios'

const app = createApp(App).use(router)

app.config.globalProperties.$http = axios

app.mount('#app')
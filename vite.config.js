import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from "url";
// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: [
      { find: '@', replacement: fileURLToPath(new URL('./src', import.meta.url)) },
      { find: '@assets', replacement: fileURLToPath(new URL('./src/assets', import.meta.url)) },
    ],
  },
  server: {
    host: '0.0.0.0',
    port:'5173',
    proxy: {
      '/.well-known': {
        target: 'http://angelo0218-server.ddns.net',
        changeOrigin: true,
      },
   
    },
  }
})

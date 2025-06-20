import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  build: {
    outDir: 'public',
    emptyOutDir: true,
  },
  // Setting the relative URL (`./`) for loading html and associated asset files (e.g. `./assets/index-CWBTEL-2.js`).
  // https://vite.dev/guide/build#public-base-path
  base: './'
})

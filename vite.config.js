import { copyFileSync, mkdirSync } from 'node:fs'
import { resolve } from 'node:path'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// The host serves static files only, so give /admin2 its own index.html.
const adminRoute = {
  name: 'admin2-route',
  closeBundle() {
    const dist = resolve(__dirname, 'dist')
    mkdirSync(resolve(dist, 'admin2'), { recursive: true })
    copyFileSync(resolve(dist, 'index.html'), resolve(dist, 'admin2/index.html'))
  },
}

export default defineConfig({
  plugins: [react(), adminRoute],
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
})

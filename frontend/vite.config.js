import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { fileURLToPath, URL } from 'node:url'

// Compila el frontend React dentro de backend/app/static/dist con nombres
// fijos (sin hash) para que el template Flask pueda referenciarlo sin manifest.
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) },
  },
  build: {
    outDir: '../backend/app/static/dist',
    emptyOutDir: true,
    rollupOptions: {
      input: 'src/index.jsx',
      output: {
        entryFileNames: 'app.js',
        chunkFileNames: '[name].js',
        assetFileNames: 'app.[ext]',
      },
    },
  },
  test: {
    environment: 'jsdom',
  },
})

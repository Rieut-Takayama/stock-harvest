import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'
import { visualizer } from 'rollup-plugin-visualizer'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    visualizer({
      filename: 'dist/stats.html',
      open: false,
      gzipSize: true
    })
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, './src')
    }
  },
  server: {
    port: 3247,
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // MUI関連を別チャンクに分離
          'mui-core': [
            '@mui/material',
            '@emotion/react',
            '@emotion/styled'
          ],
          // MUIアイコンを別チャンクに分離
          'mui-icons': ['@mui/icons-material'],
          // Charts関連を別チャンクに分離
          'charts': ['recharts'],
          // Router関連を別チャンクに分離
          'router': ['react-router-dom'],
          // React Query関連を別チャンクに分離
          'query': ['@tanstack/react-query'],
          // ユーティリティライブラリ
          'vendor': ['axios', 'zustand']
        }
      }
    }
  }
})

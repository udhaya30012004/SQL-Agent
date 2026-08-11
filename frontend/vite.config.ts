import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

const backendOrigin = process.env.VITE_BACKEND_ORIGIN || 'https://sql-agent-jwi7.onrender.com';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(import.meta.dirname, './src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: backendOrigin,
        changeOrigin: true,
      },
      '/charts': {
        target: backendOrigin,
        changeOrigin: true,
      },
    },
  },
});

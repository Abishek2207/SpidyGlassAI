import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      // Treat mediapipe packages as external - they are loaded via CDN script tags
      external: [
        '@mediapipe/hands',
        '@mediapipe/camera_utils',
        '@mediapipe/drawing_utils',
      ],
      output: {
        globals: {
          '@mediapipe/hands': 'Hands',
          '@mediapipe/camera_utils': 'CameraUtils',
          '@mediapipe/drawing_utils': 'DrawingUtils',
        },
      },
    },
  },
  optimizeDeps: {
    exclude: ['@mediapipe/hands', '@mediapipe/camera_utils', '@mediapipe/drawing_utils'],
  },
})

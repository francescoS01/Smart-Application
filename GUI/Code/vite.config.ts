import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'url'
import VueI18nPlugin from '@intlify/unplugin-vue-i18n/vite'
import { vuestic } from '@vuestic/compiler/vite'

// https://vitejs.dev/config/
export default defineConfig({
  build: {
    sourcemap: true,
  },
  plugins: [
    vuestic({
      devtools: true,
      cssLayers: true,
    }),
    vue(),
    VueI18nPlugin({
      include: resolve(dirname(fileURLToPath(import.meta.url)), './src/i18n/locales/**'),
    }),
  ],
  server: {
    proxy: {
      // Configura il proxy per le chiamate API
      '/api': {
        target: 'https://127.0.0.1:443', // Backend con HTTPS
        changeOrigin: true, // Cambia l'origin della richiesta per evitare errori CORS
        secure: false, // Ignora certificati SSL non validi
        rewrite: (path) => path.replace(/^\/api/, ''), // Rimuove /api dal percorso
      },
    },
  },
})

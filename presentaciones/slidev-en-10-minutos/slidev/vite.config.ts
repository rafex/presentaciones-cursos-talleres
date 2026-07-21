import { defineConfig } from 'vite'

// El directorio public es un enlace a ../assets para evitar duplicar recursos
export default defineConfig({
  publicDir: 'public',
})

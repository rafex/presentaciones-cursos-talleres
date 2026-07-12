import { defineConfig } from 'vite'

// El directorio public es un enlace a ../assets para evitar duplicar recursos
// entre el deck Marp y el piloto Slidev.
export default defineConfig({
  publicDir: 'public',
})

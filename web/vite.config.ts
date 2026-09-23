import { defineConfig } from 'vite';

// Same-origin API calls keep browser keys and cross-origin settings out of the UI.
export default defineConfig({
  server: { proxy: { '/api': 'http://127.0.0.1:8000' } },
  preview: { proxy: { '/api': 'http://127.0.0.1:8000' } },
});

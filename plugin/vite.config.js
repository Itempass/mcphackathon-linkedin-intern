import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import { crx } from '@crxjs/vite-plugin';
import manifest from './public/manifest.json' with { type: 'json' };
import path from 'path';
import { fileURLToPath } from 'url';
var __filename = fileURLToPath(import.meta.url);
var __dirname = path.dirname(__filename);
export default defineConfig(function (_a) {
    var mode = _a.mode;
    // Load env file based on mode
    var env = loadEnv(mode, path.resolve(__dirname, '..'), '');
    return {
        plugins: [
            react(),
            crx({ manifest: manifest }),
        ],
        // Build optimizations
        build: {
            outDir: 'dist',
            sourcemap: mode === 'development',
            minify: mode === 'production',
            target: 'es2015',
            rollupOptions: {
                input: {
                    sidepanel: 'src/sidepanel.html',
                },
            },
        },
        // Development server settings
        server: {
            port: 3000,
            strictPort: true,
            hmr: {
                port: 3000,
            },
        },
    };
});

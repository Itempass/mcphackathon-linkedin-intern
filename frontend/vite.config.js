import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import { crx } from '@crxjs/vite-plugin';
import manifest from './public/manifest.json' with { type: 'json' };
export default defineConfig(function (_a) {
    var mode = _a.mode;
    // Load env file based on mode
    var env = loadEnv(mode, process.cwd(), '');
    return {
        plugins: [
            react(),
            crx({ manifest: manifest }),
        ],
        // Environment variable handling
        define: {
            'process.env.NODE_ENV': JSON.stringify(mode),
            // Make env variables available
            'process.env.VITE_API_BASE_URL': JSON.stringify(env.VITE_API_BASE_URL),
        },
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

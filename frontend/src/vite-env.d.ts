/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_ENABLE_DEBUG_LOGGING: string
  readonly VITE_ENABLE_TELEMETRY: string
  readonly VITE_EXTENSION_ID: string
  readonly VITE_CSP_CONNECT_SRC: string
  readonly VITE_BUILD_MODE: string
  readonly VITE_BUILD_TARGET: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
} 
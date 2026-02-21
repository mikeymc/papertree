// ABOUTME: Vitest configuration for frontend BDD test suite
// ABOUTME: Merges vite.config.js (inherits @-alias + React plugin) with test settings

import { defineConfig, mergeConfig } from 'vitest/config'
import viteConfig from './vite.config.js'

export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      environment: 'jsdom',
      globals: true,
      css: false,
      restoreMocks: true,
      setupFiles: ['./src/__tests__/setup.js'],
      include: ['src/__tests__/**/*.test.{js,jsx}'],
      coverage: {
        provider: 'v8',
        thresholds: { lines: 60, functions: 50, branches: 55, statements: 60 },
        exclude: ['src/components/ui/**', 'node_modules/**'],
      },
    },
  })
)

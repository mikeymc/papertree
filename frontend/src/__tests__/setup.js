// ABOUTME: Global test setup for Vitest — MSW lifecycle, matchers, and storage cleanup
// ABOUTME: Runs before every test file via vitest.config.js setupFiles

import '@testing-library/jest-dom'
import 'fake-indexeddb/auto'
import { afterAll, afterEach, beforeAll, vi } from 'vitest'
import { cleanup } from '@testing-library/react'
import { server } from './mocks/server.js'

// jsdom localStorage can be broken when --localstorage-file is set by the runner.
// Provide a reliable in-memory shim so ThemeProvider and other localStorage users work.
const localStorageStore = {}
const localStorageMock = {
  getItem: vi.fn((key) => localStorageStore[key] ?? null),
  setItem: vi.fn((key, value) => { localStorageStore[key] = String(value) }),
  removeItem: vi.fn((key) => { delete localStorageStore[key] }),
  clear: vi.fn(() => { Object.keys(localStorageStore).forEach(k => delete localStorageStore[k]) }),
}
try {
  Object.defineProperty(window, 'localStorage', { value: localStorageMock, writable: true })
} catch (_) {
  // If defineProperty fails, the environment already has a working localStorage
}

beforeAll(() => server.listen({ onUnhandledRequest: 'warn' }))

afterEach(() => {
  cleanup()
  server.resetHandlers()
  localStorageMock.clear()
})

afterAll(() => server.close())

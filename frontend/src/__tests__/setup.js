// ABOUTME: Global test setup for Vitest — MSW lifecycle, matchers, and storage cleanup
// ABOUTME: Runs before every test file via vitest.config.js setupFiles

import '@testing-library/jest-dom'
import 'fake-indexeddb/auto'
import { afterAll, afterEach, beforeAll, vi } from 'vitest'
import { cleanup } from '@testing-library/react'
import { server } from './mocks/server.js'

// jsdom does not implement ResizeObserver — provide a no-op shim for resizable panel components.
global.ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}

// jsdom does not implement matchMedia — provide a minimal shim for components that read it.
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

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

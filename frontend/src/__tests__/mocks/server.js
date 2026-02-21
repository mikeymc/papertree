// ABOUTME: MSW server instance used by all test files
// ABOUTME: Initialized with default handlers; per-test overrides via server.use()

import { setupServer } from 'msw/node'
import { defaultHandlers } from './handlers/index.js'

export const server = setupServer(...defaultHandlers)

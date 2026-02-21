// ABOUTME: MSW handler for feedback submission endpoint
// ABOUTME: Returns success by default; override per-test to simulate errors

import { http, HttpResponse } from 'msw'

export const feedbackHandlers = [
  http.post('/api/feedback', () => HttpResponse.json({ success: true })),
]

// ABOUTME: MSW handlers for algorithm configuration and validation endpoints
// ABOUTME: Covers config load, save, validation, and optimization job endpoints

import { http, HttpResponse } from 'msw'
import { algorithmConfigResponse, validationResultResponse } from '../../fixtures/algorithm.js'

export const algorithmHandlers = [
  http.get('/api/algorithm/config', () => HttpResponse.json(algorithmConfigResponse)),

  http.post('/api/algorithm/config', async ({ request }) => {
    const body = await request.json()
    return HttpResponse.json({ ...algorithmConfigResponse, ...body })
  }),

  http.post('/api/validate/run', () => HttpResponse.json({ job_id: 'val-123' })),

  http.get('/api/validate/progress/:jobId', () => HttpResponse.json(validationResultResponse)),

  http.post('/api/optimize/run', () => HttpResponse.json({ job_id: 'opt-456' })),

  http.get('/api/optimize/progress/:jobId', () => HttpResponse.json({ status: 'running', progress: 50 })),
]

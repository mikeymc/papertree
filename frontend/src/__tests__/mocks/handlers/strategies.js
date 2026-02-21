// ABOUTME: MSW handlers for strategy management endpoints
// ABOUTME: Covers list, create, and delete strategy operations

import { http, HttpResponse } from 'msw'
import { strategiesListResponse } from '../../fixtures/strategies.js'

export const strategiesHandlers = [
  http.get('/api/strategies', () => HttpResponse.json(strategiesListResponse)),

  http.post('/api/strategies', async ({ request }) => {
    const body = await request.json()
    return HttpResponse.json({ id: 99, ...body }, { status: 201 })
  }),

  http.delete('/api/strategies/:id', () => HttpResponse.json({ success: true })),
]

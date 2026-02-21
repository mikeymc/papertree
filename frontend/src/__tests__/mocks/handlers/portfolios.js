// ABOUTME: MSW handlers for portfolio CRUD endpoints
// ABOUTME: Covers list, create, and delete portfolio operations

import { http, HttpResponse } from 'msw'
import { portfoliosListResponse } from '../../fixtures/portfolios.js'

export const portfoliosHandlers = [
  http.get('/api/portfolios', () => HttpResponse.json(portfoliosListResponse)),

  http.post('/api/portfolios', async ({ request }) => {
    const body = await request.json()
    return HttpResponse.json({ id: 99, ...body }, { status: 201 })
  }),

  http.delete('/api/portfolios/:id', () => HttpResponse.json({ success: true })),
]

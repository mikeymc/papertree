// ABOUTME: MSW handlers for alerts CRUD endpoints
// ABOUTME: Covers list, create, and delete alert operations

import { http, HttpResponse } from 'msw'
import { alertsListResponse } from '../../fixtures/alerts.js'

export const alertsHandlers = [
  http.get('/api/alerts', () => HttpResponse.json(alertsListResponse)),

  http.post('/api/alerts', async ({ request }) => {
    const body = await request.json()
    return HttpResponse.json({ id: 99, ...body, is_triggered: false }, { status: 201 })
  }),

  http.delete('/api/alerts/:alertId', () => HttpResponse.json({ success: true })),
]

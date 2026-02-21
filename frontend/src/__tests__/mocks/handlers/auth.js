// ABOUTME: MSW handlers for authentication endpoints
// ABOUTME: Default handlers return a logged-in user; override per-test for error cases

import { http, HttpResponse } from 'msw'
import { authenticatedUser } from '../../fixtures/users.js'

export const authHandlers = [
  http.get('/api/auth/user', () => {
    return HttpResponse.json(authenticatedUser)
  }),

  http.post('/api/auth/logout', () => {
    return HttpResponse.json({ success: true })
  }),

  http.post('/api/auth/login', async ({ request }) => {
    const body = await request.json()
    if (body.password === 'wrong') {
      return HttpResponse.json({ error: 'Invalid credentials' }, { status: 401 })
    }
    return HttpResponse.json(authenticatedUser)
  }),

  http.post('/api/auth/register', async ({ request }) => {
    const body = await request.json()
    return HttpResponse.json({ ...authenticatedUser, email: body.email })
  }),
]

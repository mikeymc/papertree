// ABOUTME: MSW handlers for dashboard API endpoints
// ABOUTME: Registered before page handlers — wins for all /api/dashboard/* routes

import { http, HttpResponse } from 'msw'
import { alertsResponse, watchlistResponse, portfoliosResponse, thesesResponse, earningsResponse, insiderIntentResponse, moversResponse } from '../../fixtures/dashboard.js'

export const dashboardHandlers = [
  http.get('/api/dashboard/alerts', () => HttpResponse.json(alertsResponse)),
  http.get('/api/dashboard/watchlist', () => HttpResponse.json({ watchlist: watchlistResponse })),
  http.get('/api/dashboard/portfolios', () => HttpResponse.json(portfoliosResponse)),
  http.get('/api/dashboard/theses', () => HttpResponse.json(thesesResponse)),
  http.get('/api/dashboard/earnings', () => HttpResponse.json(earningsResponse)),
  http.get('/api/dashboard/insider-intent', () => HttpResponse.json(insiderIntentResponse)),
  http.get('/api/market/movers', () => HttpResponse.json(moversResponse)),
]

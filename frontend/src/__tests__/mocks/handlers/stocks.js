// ABOUTME: MSW handlers for stock search and detail endpoints
// ABOUTME: Covers search, stock detail, watchlist, and history endpoints

import { http, HttpResponse } from 'msw'
import { searchResults, stockDetailResponse } from '../../fixtures/stocks.js'
import { watchlistResponse } from '../../fixtures/dashboard.js'

export const stockHandlers = [
  http.get('/api/stocks/search', ({ request }) => {
    const url = new URL(request.url)
    const q = url.searchParams.get('q') || ''
    const filtered = searchResults.filter(s =>
      s.symbol.includes(q.toUpperCase()) || s.company_name.toLowerCase().includes(q.toLowerCase())
    )
    return HttpResponse.json({ results: filtered })
  }),

  http.get('/api/stock/:symbol', () => {
    return HttpResponse.json({ evaluation: stockDetailResponse })
  }),

  http.get('/api/stock/:symbol/history', () => {
    return HttpResponse.json({ annual: [], quarterly: [] })
  }),

  http.get('/api/stock/:symbol/filings', () => {
    return HttpResponse.json({ filings: [] })
  }),

  http.get('/api/watchlist', () => HttpResponse.json({ watchlist: watchlistResponse })),

  http.post('/api/watchlist/:symbol', () => HttpResponse.json({ success: true })),

  http.delete('/api/watchlist/:symbol', () => HttpResponse.json({ success: true })),
]

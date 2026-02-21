// ABOUTME: BDD tests for EarningsCalendarPage
// ABOUTME: Data comes from /api/dashboard/earnings (dashboardHandlers, first-match)

import { describe, it, expect } from 'vitest'
import { http, HttpResponse } from 'msw'
import { server } from '../mocks/server.js'
import { renderWithProviders, screen, waitFor } from '../helpers/render.jsx'
import EarningsCalendarPage from '@/pages/EarningsCalendarPage'

describe('EarningsCalendarPage', () => {
  describe('when earnings load successfully', () => {
    it('renders earnings entries from the API', async () => {
      renderWithProviders(<EarningsCalendarPage />)
      // earningsResponse in fixtures has AAPL and NVDA
      await waitFor(() => expect(screen.getByText('AAPL')).toBeInTheDocument())
    })
  })

  describe('when the API fails', () => {
    it('shows an error or empty state', async () => {
      server.use(http.get('/api/dashboard/earnings', () => new HttpResponse(null, { status: 500 })))
      renderWithProviders(<EarningsCalendarPage />)
      await waitFor(() => {
        const body = document.body.textContent
        expect(body).toMatch(/error|failed|no earnings/i)
      })
    })
  })
})

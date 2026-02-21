// ABOUTME: BDD tests for ThesesPage
// ABOUTME: Data comes from /api/dashboard/theses (handled by dashboardHandlers, first-match)

import { describe, it, expect } from 'vitest'
import { http, HttpResponse } from 'msw'
import { server } from '../mocks/server.js'
import { renderWithProviders, screen, waitFor } from '../helpers/render.jsx'
import ThesesPage from '@/pages/ThesesPage'

describe('ThesesPage', () => {
  describe('when theses load successfully', () => {
    it('renders thesis entries from the API', async () => {
      renderWithProviders(<ThesesPage />)
      // thesesResponse in fixtures has AAPL and MSFT
      await waitFor(() => expect(screen.getByText('AAPL')).toBeInTheDocument())
      expect(screen.getByText('MSFT')).toBeInTheDocument()
    })
  })

  describe('when the API fails', () => {
    it('shows an error message', async () => {
      server.use(http.get('/api/dashboard/theses', () => new HttpResponse(null, { status: 500 })))
      renderWithProviders(<ThesesPage />)
      await waitFor(() => expect(screen.getByText(/Failed to load theses/i)).toBeInTheDocument())
    })
  })
})

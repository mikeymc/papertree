// ABOUTME: BDD tests for WatchlistQuickView dashboard widget
// ABOUTME: Covers loading, error, empty, and populated states

import { describe, it, expect, vi } from 'vitest'
import { http, HttpResponse } from 'msw'
import { server } from '../../mocks/server.js'
import { renderWithProviders, screen, waitFor } from '../../helpers/render.jsx'
import WatchlistQuickView from '@/components/dashboard/WatchlistQuickView'

describe('WatchlistQuickView', () => {
  describe('when watchlist data loads successfully', () => {
    it('shows the Watchlist card title', async () => {
      renderWithProviders(<WatchlistQuickView onNavigate={vi.fn()} />)
      await waitFor(() => expect(screen.getByText('Watchlist')).toBeInTheDocument())
    })

    it('renders the stock symbols from the API', async () => {
      renderWithProviders(<WatchlistQuickView onNavigate={vi.fn()} />)
      await waitFor(() => expect(screen.getByText('AAPL')).toBeInTheDocument())
      expect(screen.getByText('MSFT')).toBeInTheDocument()
    })
  })

  describe('when the API returns an empty watchlist', () => {
    it('shows the empty state prompt', async () => {
      server.use(http.get('/api/dashboard/watchlist', () => HttpResponse.json([])))
      renderWithProviders(<WatchlistQuickView onNavigate={vi.fn()} />)
      await waitFor(() => expect(screen.getByText(/Add stocks to track/i)).toBeInTheDocument())
    })
  })

  describe('when the API fails', () => {
    it('shows an error message', async () => {
      server.use(http.get('/api/dashboard/watchlist', () => new HttpResponse(null, { status: 500 })))
      renderWithProviders(<WatchlistQuickView onNavigate={vi.fn()} />)
      await waitFor(() => expect(screen.getByText(/Failed to load watchlist/i)).toBeInTheDocument())
    })
  })

  describe('when View all is clicked', () => {
    it('calls onNavigate', async () => {
      const onNavigate = vi.fn()
      renderWithProviders(<WatchlistQuickView onNavigate={onNavigate} />)
      await waitFor(() => expect(screen.getByText('View all')).toBeInTheDocument())
      screen.getByText('View all').click()
      expect(onNavigate).toHaveBeenCalled()
    })
  })
})

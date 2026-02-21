// ABOUTME: BDD tests for Dashboard page
// ABOUTME: Checks that dashboard widgets render with their correct titles

import { describe, it, expect } from 'vitest'
import { renderWithProviders, screen, waitFor } from '../helpers/render.jsx'
import Dashboard from '@/pages/Dashboard'

describe('Dashboard', () => {
  describe('on initial render', () => {
    it('shows the Watchlist widget', async () => {
      renderWithProviders(<Dashboard />)
      await waitFor(() => expect(screen.getByText('Watchlist')).toBeInTheDocument())
    })

    it('shows the Alerts widget', async () => {
      renderWithProviders(<Dashboard />)
      await waitFor(() => expect(screen.getAllByText('Alerts').length).toBeGreaterThan(0))
    })

    it('shows the Movers widget', async () => {
      renderWithProviders(<Dashboard />)
      await waitFor(() => expect(screen.getByText('Movers')).toBeInTheDocument())
    })

    it('shows the New Theses widget', async () => {
      renderWithProviders(<Dashboard />)
      await waitFor(() => expect(screen.getByText('New Theses')).toBeInTheDocument())
    })
  })
})

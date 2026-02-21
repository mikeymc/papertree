// ABOUTME: BDD tests for AdminPortfolios page
// ABOUTME: Covers portfolio list rendering, search filtering, and empty state

import { describe, it, expect } from 'vitest'
import { renderWithProviders, screen, waitFor, userEvent } from '../../helpers/render.jsx'
import AdminPortfolios from '@/pages/admin/AdminPortfolios'

describe('AdminPortfolios', () => {
  describe('on initial render', () => {
    it('shows the Portfolios heading', async () => {
      renderWithProviders(<AdminPortfolios />)
      await waitFor(() => expect(screen.getByText('Portfolios')).toBeInTheDocument())
    })

    it('shows portfolios from the API', async () => {
      renderWithProviders(<AdminPortfolios />)
      await waitFor(() => expect(screen.getByText('Main Portfolio')).toBeInTheDocument())
    })

    it('shows multiple portfolios', async () => {
      renderWithProviders(<AdminPortfolios />)
      await waitFor(() => {
        expect(screen.getByText('Main Portfolio')).toBeInTheDocument()
        expect(screen.getByText('Growth Portfolio')).toBeInTheDocument()
      })
    })
  })

  describe('when searching', () => {
    it('filters portfolios by name', async () => {
      const user = userEvent.setup()
      renderWithProviders(<AdminPortfolios />)
      await waitFor(() => expect(screen.getByText('Main Portfolio')).toBeInTheDocument())

      const search = screen.getByPlaceholderText(/Search portfolios/i)
      await user.type(search, 'Growth')

      expect(screen.queryByText('Main Portfolio')).not.toBeInTheDocument()
      expect(screen.getByText('Growth Portfolio')).toBeInTheDocument()
    })
  })

  describe('when no portfolios match the search', () => {
    it('shows the empty state message', async () => {
      const user = userEvent.setup()
      renderWithProviders(<AdminPortfolios />)
      await waitFor(() => expect(screen.getByText('Main Portfolio')).toBeInTheDocument())

      const search = screen.getByPlaceholderText(/Search portfolios/i)
      await user.type(search, 'zzz_no_match')

      expect(screen.getByText(/No portfolios found/i)).toBeInTheDocument()
    })
  })
})

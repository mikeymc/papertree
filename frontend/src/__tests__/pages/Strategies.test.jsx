// ABOUTME: BDD tests for Strategies page
// ABOUTME: Covers loading, populated, empty, and error states

import { describe, it, expect } from 'vitest'
import { http, HttpResponse } from 'msw'
import { server } from '../mocks/server.js'
import { renderWithProviders, screen, waitFor } from '../helpers/render.jsx'
import Strategies from '@/pages/Strategies'

describe('Strategies', () => {
  describe('when strategies load successfully', () => {
    it('shows the page heading', async () => {
      renderWithProviders(<Strategies />)
      await waitFor(() => expect(screen.getByText('Investment Strategies')).toBeInTheDocument())
    })

    it('renders the strategy names', async () => {
      renderWithProviders(<Strategies />)
      await waitFor(() => expect(screen.getByText('Lynch Growth')).toBeInTheDocument())
      expect(screen.getByText('Value Hunt')).toBeInTheDocument()
    })
  })

  describe('when no strategies exist', () => {
    it('shows the empty state message', async () => {
      server.use(http.get('/api/strategies', () => HttpResponse.json([])))
      renderWithProviders(<Strategies />)
      await waitFor(() => expect(screen.getByText(/No strategies defined/i)).toBeInTheDocument())
    })
  })

  describe('when the API fails', () => {
    it('shows an error message', async () => {
      server.use(http.get('/api/strategies', () => new HttpResponse(null, { status: 500 })))
      renderWithProviders(<Strategies />)
      await waitFor(() => expect(screen.getByText(/Error loading strategies/i)).toBeInTheDocument())
    })
  })
})

// ABOUTME: BDD tests for AlgorithmTuning page
// ABOUTME: Covers config loading, tab navigation, and button visibility

import { describe, it, expect } from 'vitest'
import { http, HttpResponse } from 'msw'
import { server } from '../mocks/server.js'
import { renderWithProviders, screen, waitFor } from '../helpers/render.jsx'
import AlgorithmTuning from '@/pages/AlgorithmTuning'

describe('AlgorithmTuning', () => {
  describe('when the page loads', () => {
    it('shows the Manual tab', async () => {
      renderWithProviders(<AlgorithmTuning />)
      await waitFor(() => {
        const manualMatches = screen.getAllByText(/Manual/)
        expect(manualMatches.length).toBeGreaterThan(0)
      })
    })

    it('shows the Automatic tab', async () => {
      renderWithProviders(<AlgorithmTuning />)
      await waitFor(() => expect(screen.getByText(/Automatic/)).toBeInTheDocument())
    })

    it('shows the Run Validation button', async () => {
      renderWithProviders(<AlgorithmTuning />)
      await waitFor(() => expect(screen.getByText(/Run Validation/)).toBeInTheDocument())
    })

    it('shows the Save Config button', async () => {
      renderWithProviders(<AlgorithmTuning />)
      await waitFor(() => expect(screen.getByText(/Save Config/)).toBeInTheDocument())
    })
  })

  describe('when the API fails to load config', () => {
    it('still renders the page structure', async () => {
      server.use(http.get('/api/algorithm/config', () => new HttpResponse(null, { status: 500 })))
      renderWithProviders(<AlgorithmTuning />)
      await waitFor(() => {
        const manualMatches = screen.getAllByText(/Manual/)
        expect(manualMatches.length).toBeGreaterThan(0)
      })
    })
  })
})

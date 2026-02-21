// ABOUTME: BDD tests for AdminFeedback page
// ABOUTME: Covers feedback list rendering and empty state

import { describe, it, expect } from 'vitest'
import { renderWithProviders, screen, waitFor } from '../../helpers/render.jsx'
import AdminFeedback from '@/pages/admin/AdminFeedback'

describe('AdminFeedback', () => {
  describe('on initial render', () => {
    it('shows the User Feedback heading', async () => {
      renderWithProviders(<AdminFeedback />)
      await waitFor(() => expect(screen.getByText('User Feedback')).toBeInTheDocument())
    })

    it('shows the total entries count badge', async () => {
      renderWithProviders(<AdminFeedback />)
      await waitFor(() => expect(screen.getByText(/Total Entries/)).toBeInTheDocument())
    })
  })

  describe('when no feedback exists', () => {
    it('shows the empty state message', async () => {
      const { server } = await import('../../mocks/server.js')
      const { http, HttpResponse } = await import('msw')
      server.use(http.get('/api/admin/feedback', () => HttpResponse.json({ feedback: [] })))

      renderWithProviders(<AdminFeedback />)
      await waitFor(() => expect(screen.getByText('No feedback received yet')).toBeInTheDocument())
    })
  })

  describe('when the API returns an error', () => {
    it('shows an error alert', async () => {
      const { server } = await import('../../mocks/server.js')
      const { http, HttpResponse } = await import('msw')
      server.use(http.get('/api/admin/feedback', () => HttpResponse.json({}, { status: 500 })))

      renderWithProviders(<AdminFeedback />)
      await waitFor(() => expect(screen.getByText('Error')).toBeInTheDocument())
    })
  })
})

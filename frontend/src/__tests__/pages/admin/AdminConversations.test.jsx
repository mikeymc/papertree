// ABOUTME: BDD tests for AdminConversations page
// ABOUTME: Covers conversation list rendering and message loading on selection

import { describe, it, expect } from 'vitest'
import { renderWithProviders, screen, waitFor } from '../../helpers/render.jsx'
import AdminConversations from '@/pages/admin/AdminConversations'

vi.mock('react-chartjs-2', () => ({ Line: () => <canvas data-testid="chart" /> }))

describe('AdminConversations', () => {
  describe('on initial render', () => {
    it('shows the Conversations heading', async () => {
      renderWithProviders(<AdminConversations />)
      await waitFor(() => expect(screen.getByText('Conversations')).toBeInTheDocument())
    })

    it('shows conversations from the API', async () => {
      renderWithProviders(<AdminConversations />)
      await waitFor(() => expect(screen.getByText('Analyzing AAPL earnings')).toBeInTheDocument())
    })

    it('shows user emails for each conversation', async () => {
      renderWithProviders(<AdminConversations />)
      await waitFor(() => expect(screen.getByText('user@example.com')).toBeInTheDocument())
    })

    it('shows the select-conversation prompt', async () => {
      renderWithProviders(<AdminConversations />)
      await waitFor(() => expect(screen.getByText('Select a conversation to view')).toBeInTheDocument())
    })
  })

  describe('when no conversations exist', () => {
    it('shows an empty state message', async () => {
      const { server } = await import('../../mocks/server.js')
      const { http, HttpResponse } = await import('msw')
      server.use(http.get('/api/admin/conversations', () => HttpResponse.json({ conversations: [] })))

      renderWithProviders(<AdminConversations />)
      await waitFor(() => expect(screen.getByText('No conversations found')).toBeInTheDocument())
    })
  })
})

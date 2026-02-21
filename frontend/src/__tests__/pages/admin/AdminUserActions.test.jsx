// ABOUTME: BDD tests for AdminUserActions page
// ABOUTME: Covers activity feed and API usage stats tabs

import { describe, it, expect } from 'vitest'
import { renderWithProviders, screen, waitFor, userEvent } from '../../helpers/render.jsx'
import AdminUserActions from '@/pages/admin/AdminUserActions'

describe('AdminUserActions', () => {
  describe('on initial render', () => {
    it('shows the User Actions heading', async () => {
      renderWithProviders(<AdminUserActions />)
      await waitFor(() => expect(screen.getByText('User Actions')).toBeInTheDocument())
    })

    it('shows the Recent Activity tab', async () => {
      renderWithProviders(<AdminUserActions />)
      await waitFor(() => expect(screen.getByRole('tab', { name: /Recent Activity/i })).toBeInTheDocument())
    })

    it('shows the API Usage Statistics tab', async () => {
      renderWithProviders(<AdminUserActions />)
      await waitFor(() => expect(screen.getByRole('tab', { name: /API Usage Statistics/i })).toBeInTheDocument())
    })

    it('shows event paths in the activity table', async () => {
      renderWithProviders(<AdminUserActions />)
      await waitFor(() => expect(screen.getByText('/api/stock/AAPL')).toBeInTheDocument())
    })
  })

  describe('when the API Usage Statistics tab is active', () => {
    it('shows user hit counts', async () => {
      const user = userEvent.setup()
      renderWithProviders(<AdminUserActions />)
      await waitFor(() => expect(screen.getByRole('tab', { name: /API Usage Statistics/i })).toBeInTheDocument())

      await user.click(screen.getByRole('tab', { name: /API Usage Statistics/i }))

      await waitFor(() => expect(screen.getByText('142')).toBeInTheDocument())
    })
  })

  describe('when no events exist', () => {
    it('shows empty state message in activity tab', async () => {
      const { server } = await import('../../mocks/server.js')
      const { http, HttpResponse } = await import('msw')
      server.use(http.get('/api/admin/user_actions', () => HttpResponse.json({ events: [], stats: [] })))

      renderWithProviders(<AdminUserActions />)
      await waitFor(() => expect(screen.getByText('No recent user activity found.')).toBeInTheDocument())
    })
  })
})

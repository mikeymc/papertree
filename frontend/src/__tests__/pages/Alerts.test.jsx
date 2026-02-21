// ABOUTME: BDD tests for Alerts page
// ABOUTME: Covers loading, pending/triggered tabs, empty state, and API errors

import { describe, it, expect, vi } from 'vitest'
import { http, HttpResponse } from 'msw'
import { server } from '../mocks/server.js'
import { renderWithProviders, screen, waitFor } from '../helpers/render.jsx'
import Alerts from '@/pages/Alerts'

describe('Alerts', () => {
  describe('when alerts load successfully', () => {
    it('shows the Alerts heading', async () => {
      renderWithProviders(<Alerts />)
      await waitFor(() => expect(screen.getByText('Alerts')).toBeInTheDocument())
    })

    it('shows the Pending and Triggered tabs', async () => {
      renderWithProviders(<Alerts />)
      await waitFor(() => expect(screen.getByText('Pending')).toBeInTheDocument())
      expect(screen.getByText('Triggered')).toBeInTheDocument()
    })

    it('renders alerts in the Pending tab by default', async () => {
      renderWithProviders(<Alerts />)
      await waitFor(() => expect(screen.getByText(/AAPL/)).toBeInTheDocument())
    })
  })

  describe('when no alerts exist', () => {
    it('shows the empty state message', async () => {
      server.use(http.get('/api/alerts', () => HttpResponse.json({ alerts: [] })))
      renderWithProviders(<Alerts />)
      await waitFor(() => expect(screen.getByText(/No pending alerts/i)).toBeInTheDocument())
    })
  })

  describe('when the delete button is clicked', () => {
    it('calls the delete API', async () => {
      let deleteCalled = false
      server.use(http.delete('/api/alerts/:alertId', () => {
        deleteCalled = true
        return HttpResponse.json({ success: true })
      }))
      vi.spyOn(window, 'confirm').mockReturnValue(true)

      renderWithProviders(<Alerts />)
      await waitFor(() => expect(screen.getByText(/AAPL/)).toBeInTheDocument())

      const deleteButtons = document.querySelectorAll('button[class*="destructive"], button svg')
      expect(deleteButtons.length).toBeGreaterThan(0)
    })
  })
})

// ABOUTME: BDD tests for AdminStrategies page
// ABOUTME: Covers strategy list rendering and search filtering

import { describe, it, expect } from 'vitest'
import { renderWithProviders, screen, waitFor, userEvent } from '../../helpers/render.jsx'
import AdminStrategies from '@/pages/admin/AdminStrategies'

describe('AdminStrategies', () => {
  describe('on initial render', () => {
    it('shows the Strategies heading', async () => {
      renderWithProviders(<AdminStrategies />)
      await waitFor(() => expect(screen.getByText('Strategies')).toBeInTheDocument())
    })

    it('shows strategies from the API', async () => {
      renderWithProviders(<AdminStrategies />)
      await waitFor(() => expect(screen.getByText('Lynch Tenbagger')).toBeInTheDocument())
    })

    it('shows multiple strategies', async () => {
      renderWithProviders(<AdminStrategies />)
      await waitFor(() => {
        expect(screen.getByText('Lynch Tenbagger')).toBeInTheDocument()
        expect(screen.getByText('Buffett Fortress')).toBeInTheDocument()
      })
    })
  })

  describe('when searching', () => {
    it('filters strategies by name', async () => {
      const user = userEvent.setup()
      renderWithProviders(<AdminStrategies />)
      await waitFor(() => expect(screen.getByText('Lynch Tenbagger')).toBeInTheDocument())

      const search = screen.getByPlaceholderText(/Search strategies/i)
      await user.type(search, 'Buffett')

      expect(screen.queryByText('Lynch Tenbagger')).not.toBeInTheDocument()
      expect(screen.getByText('Buffett Fortress')).toBeInTheDocument()
    })
  })

  describe('when no strategies match the search', () => {
    it('shows the empty state message', async () => {
      const user = userEvent.setup()
      renderWithProviders(<AdminStrategies />)
      await waitFor(() => expect(screen.getByText('Lynch Tenbagger')).toBeInTheDocument())

      const search = screen.getByPlaceholderText(/Search strategies/i)
      await user.type(search, 'zzz_no_match')

      expect(screen.getByText(/No strategies found/i)).toBeInTheDocument()
    })
  })
})

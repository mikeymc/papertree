// ABOUTME: BDD tests for Settings page
// ABOUTME: Covers tab navigation, character selection, and appearance settings

import { describe, it, expect } from 'vitest'
import { renderWithProviders, screen, waitFor } from '../helpers/render.jsx'
import Settings from '@/pages/Settings'

describe('Settings', () => {
  describe('on initial render', () => {
    it('shows the Settings heading', async () => {
      renderWithProviders(<Settings />)
      await waitFor(() => expect(screen.getByText('Settings')).toBeInTheDocument())
    })

    it('shows the Investment Style sidebar item', async () => {
      renderWithProviders(<Settings />)
      await waitFor(() => expect(screen.getByText('Investment Style')).toBeInTheDocument())
    })

    it('shows the Expertise Level sidebar item', async () => {
      renderWithProviders(<Settings />)
      await waitFor(() => expect(screen.getByText('Expertise Level')).toBeInTheDocument())
    })

    it('shows the Appearance section heading', async () => {
      renderWithProviders(<Settings />)
      await waitFor(() => {
        const matches = screen.getAllByText('Appearance')
        expect(matches.length).toBeGreaterThan(0)
      })
    })
  })

  describe('when Investment Style is clicked', () => {
    it('displays character options', async () => {
      const userEvent = (await import('@testing-library/user-event')).default
      const user = userEvent.setup()
      renderWithProviders(<Settings />)
      await waitFor(() => expect(screen.getByText('Investment Style')).toBeInTheDocument())
      await user.click(screen.getByText('Investment Style'))
      await waitFor(() => expect(screen.getByText('Peter Lynch')).toBeInTheDocument())
    })
  })
})

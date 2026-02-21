// ABOUTME: BDD tests for Help page
// ABOUTME: Covers topic navigation and onboarding completion

import { describe, it, expect } from 'vitest'
import { renderWithProviders, screen, waitFor } from '../helpers/render.jsx'
import Help from '@/pages/Help'

describe('Help', () => {
  describe('on initial render', () => {
    it('shows the Quick Start Guide topic', async () => {
      renderWithProviders(<Help />)
      await waitFor(() => {
        const matches = screen.getAllByText('Quick Start Guide')
        expect(matches.length).toBeGreaterThan(0)
      })
    })

    it('shows topics in the Getting Started section', async () => {
      renderWithProviders(<Help />)
      await waitFor(() => expect(screen.getByText('Getting Started')).toBeInTheDocument())
    })
  })
})

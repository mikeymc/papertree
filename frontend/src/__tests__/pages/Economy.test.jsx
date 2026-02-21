// ABOUTME: BDD tests for Economy page
// ABOUTME: Mocks recharts to avoid canvas issues; checks section headings render

import { describe, it, expect, vi } from 'vitest'
import { renderWithProviders, screen, waitFor } from '../helpers/render.jsx'
import Economy from '@/pages/Economy'

vi.mock('react-chartjs-2', () => ({
  Line: () => <canvas data-testid="chart" />,
}))

describe('Economy', () => {
  describe('on initial render', () => {
    it('shows the Rates & Inflation section', async () => {
      renderWithProviders(<Economy />)
      await waitFor(() => expect(screen.getByText('Rates & Inflation')).toBeInTheDocument())
    })

    it('shows the Consumer section', async () => {
      renderWithProviders(<Economy />)
      await waitFor(() => expect(screen.getByText('Consumer')).toBeInTheDocument())
    })
  })
})

// ABOUTME: BDD tests for AdminJobStats page
// ABOUTME: Mocks react-chartjs-2 to avoid canvas; checks tab rendering and stat display

import { describe, it, expect, vi } from 'vitest'
import { renderWithProviders, screen, waitFor } from '../../helpers/render.jsx'
import AdminJobStats from '@/pages/admin/AdminJobStats'

vi.mock('react-chartjs-2', () => ({ Line: () => <canvas data-testid="chart" /> }))
vi.mock('chartjs-adapter-date-fns', () => ({}))

describe('AdminJobStats', () => {
  describe('on initial render', () => {
    it('shows the Job History tab', async () => {
      renderWithProviders(<AdminJobStats />)
      await waitFor(() => expect(screen.getByText('Job History')).toBeInTheDocument())
    })

    it('shows the Performance tab', async () => {
      renderWithProviders(<AdminJobStats />)
      await waitFor(() => expect(screen.getByText('Performance')).toBeInTheDocument())
    })

    it('shows job type from stats data', async () => {
      renderWithProviders(<AdminJobStats />)
      await waitFor(() => expect(screen.getByText('screening')).toBeInTheDocument())
    })
  })
})

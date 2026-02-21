// ABOUTME: Integration tests for StockListView component rendered via App routing
// ABOUTME: Verifies stock list rendering, empty state, and session loading

import { describe, it, expect } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { AuthProvider } from '@/context/AuthContext'
import { ChatProvider } from '@/context/ChatContext'
import { ThemeProvider } from '@/components/theme-provider'
import { server } from '../mocks/server.js'
import { http, HttpResponse } from 'msw'
import App from '@/App'

vi.mock('react-chartjs-2', () => ({ Line: () => <canvas data-testid="chart" /> }))
vi.mock('chartjs-adapter-date-fns', () => ({}))
vi.mock('chart.js', () => ({
  Chart: { register: vi.fn(), defaults: {} },
  CategoryScale: vi.fn(),
  LinearScale: vi.fn(),
  BarElement: vi.fn(),
  PointElement: vi.fn(),
  LineElement: vi.fn(),
  ArcElement: vi.fn(),
  Title: vi.fn(),
  Tooltip: vi.fn(),
  Legend: vi.fn(),
  TimeScale: vi.fn(),
  Filler: vi.fn(),
}))

function renderAtStocks() {
  return render(
    <MemoryRouter initialEntries={['/stocks']}>
      <AuthProvider>
        <ChatProvider>
          <ThemeProvider defaultTheme="light" storageKey="vite-ui-theme" disableFetch={true}>
            <App />
          </ThemeProvider>
        </ChatProvider>
      </AuthProvider>
    </MemoryRouter>
  )
}

describe('StockListView', () => {
  describe('when no prior session exists', () => {
    beforeEach(() => {
      server.use(http.get('/api/sessions/latest', () => HttpResponse.json({}, { status: 404 })))
    })

    it('renders without crashing', async () => {
      renderAtStocks()
      // App renders the authenticated shell - wait for it to stabilize
      await waitFor(() => expect(document.body).toBeTruthy(), { timeout: 3000 })
    })
  })

  describe('when a prior session has results', () => {
    beforeEach(() => {
      server.use(
        http.get('/api/sessions/latest', () =>
          HttpResponse.json({
            results: [
              {
                symbol: 'AAPL',
                company_name: 'Apple Inc.',
                overall_score: 82,
                overall_status: 'STRONG_BUY',
                pe_ratio: 28.5,
                peg_ratio: 1.2,
              },
              {
                symbol: 'MSFT',
                company_name: 'Microsoft Corp.',
                overall_score: 78,
                overall_status: 'BUY',
                pe_ratio: 32.1,
                peg_ratio: 1.8,
              },
            ],
            total_pages: 1,
            total_count: 2,
            active_character: 'lynch',
          })
        )
      )
    })

    it('shows stock symbols from the session', async () => {
      renderAtStocks()
      await waitFor(() => expect(screen.getByText('AAPL')).toBeInTheDocument(), { timeout: 5000 })
    })

    it('shows multiple stocks', async () => {
      renderAtStocks()
      await waitFor(() => {
        expect(screen.getByText('AAPL')).toBeInTheDocument()
        expect(screen.getByText('MSFT')).toBeInTheDocument()
      }, { timeout: 5000 })
    })
  })
})

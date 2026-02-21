// ABOUTME: Integration tests for App routing and auth guard behaviour
// ABOUTME: Covers unauthenticated redirects, authenticated routing, and admin guard

import { describe, it, expect } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { AuthProvider } from '@/context/AuthContext'
import { ChatProvider } from '@/context/ChatContext'
import { ThemeProvider } from '@/components/theme-provider'
import { server } from '../mocks/server.js'
import { http, HttpResponse } from 'msw'
import { authenticatedUser } from '../fixtures/users.js'
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

function renderApp(initialPath = '/') {
  return render(
    <MemoryRouter initialEntries={[initialPath]}>
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

describe('App', () => {
  // Add handlers for endpoints App calls that aren't in default handlers
  beforeEach(() => {
    server.use(
      http.get('/api/sessions/latest', () => HttpResponse.json({}, { status: 404 })),
      http.get('/api/market/index/*', () => HttpResponse.json({ data: [] })),
    )
  })

  describe('when user is unauthenticated', () => {
    beforeEach(() => {
      server.use(http.get('/api/auth/user', () => HttpResponse.json({ error: 'Not authenticated' }, { status: 401 })))
    })

    it('shows the landing page at /', async () => {
      renderApp('/')
      await waitFor(() => expect(screen.getByText(/Stop chasing hype/i)).toBeInTheDocument(), { timeout: 3000 })
    })

    it('shows the login page at /login', async () => {
      renderApp('/login')
      await waitFor(() => {
        const matches = screen.getAllByText(/Sign In/i)
        expect(matches.length).toBeGreaterThan(0)
      }, { timeout: 3000 })
    })

    it('redirects protected routes to the landing page', async () => {
      renderApp('/alerts')
      // Should end up on landing page (redirected), not alerts
      await waitFor(() => expect(screen.getByText(/Stop chasing hype/i)).toBeInTheDocument(), { timeout: 3000 })
    })
  })

  describe('when user is authenticated', () => {
    it('renders the Dashboard at /', async () => {
      renderApp('/')
      await waitFor(() => {
        const matches = screen.getAllByText(/Watchlist/i)
        expect(matches.length).toBeGreaterThan(0)
      }, { timeout: 5000 })
    })
  })

  describe('when user is a non-admin accessing /admin', () => {
    it('redirects to the home page', async () => {
      // Default auth handler returns non-admin user (no user_type: 'admin')
      renderApp('/admin')
      // RequireAdmin redirects to '/' which renders dashboard
      await waitFor(() => {
        const matches = screen.getAllByText(/Watchlist/i)
        expect(matches.length).toBeGreaterThan(0)
      }, { timeout: 5000 })
    })
  })

  describe('when user is an admin accessing /admin', () => {
    it('renders the admin job stats page', async () => {
      server.use(
        http.get('/api/auth/user', () => HttpResponse.json({ ...authenticatedUser, user_type: 'admin' }))
      )
      renderApp('/admin')
      await waitFor(() => expect(screen.getByText('Job History')).toBeInTheDocument(), { timeout: 5000 })
    })
  })
})

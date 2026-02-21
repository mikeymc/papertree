// ABOUTME: BDD tests for StockDetail page
// ABOUTME: Uses Routes + MemoryRouter to provide :symbol param via useParams()

import { describe, it, expect } from 'vitest'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import { render } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { server } from '../mocks/server.js'
import { screen, waitFor } from '../helpers/render.jsx'
import { AuthProvider } from '@/context/AuthContext'
import { ChatProvider } from '@/context/ChatContext'
import { ThemeProvider } from '@/components/theme-provider'
import StockDetail from '@/pages/StockDetail'

function renderStockDetail(symbol = 'AAPL') {
  return render(
    <MemoryRouter initialEntries={[`/stock/${symbol}`]}>
      <AuthProvider>
        <ChatProvider>
          <ThemeProvider defaultTheme="light" storageKey="test-theme" disableFetch={true}>
            <Routes>
              <Route path="/stock/:symbol" element={<StockDetail />} />
            </Routes>
          </ThemeProvider>
        </ChatProvider>
      </AuthProvider>
    </MemoryRouter>
  )
}

describe('StockDetail', () => {
  describe('when stock data loads successfully', () => {
    it('displays the stock price', async () => {
      renderStockDetail()
      await waitFor(() => expect(screen.getByText(/195\.50/)).toBeInTheDocument(), { timeout: 3000 })
    })

    it('displays the stock symbol', async () => {
      renderStockDetail()
      await waitFor(() => expect(screen.getAllByText('AAPL').length).toBeGreaterThan(0), { timeout: 3000 })
    })
  })

  describe('when the API fails', () => {
    it('shows an error state', async () => {
      server.use(http.get('/api/stock/:symbol', () => new HttpResponse(null, { status: 500 })))
      renderStockDetail()
      await waitFor(() => {
        const body = document.body.textContent
        expect(body).toMatch(/error|failed|not found/i)
      }, { timeout: 3000 })
    })
  })
})

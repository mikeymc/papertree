// ABOUTME: BDD tests for StockHeader component
// ABOUTME: Covers symbol/price display, status badges, and watchlist toggle

import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import StockHeader from '@/components/StockHeader'

const baseStock = {
  symbol: 'AAPL',
  company_name: 'Apple Inc.',
  price: 195.50,
  price_change_pct: 1.2,
  market_cap: 3_000_000_000_000,
  overall_status: 'excellent',
}

describe('StockHeader', () => {
  describe('when rendered with stock data', () => {
    it('displays the symbol and company name', () => {
      render(<StockHeader stock={baseStock} watchlist={new Set()} toggleWatchlist={vi.fn()} />)
      expect(screen.getByText('AAPL')).toBeInTheDocument()
      expect(screen.getByText('Apple Inc.')).toBeInTheDocument()
    })

    it('displays the current price', () => {
      render(<StockHeader stock={baseStock} watchlist={new Set()} toggleWatchlist={vi.fn()} />)
      expect(screen.getByText(/195\.50/)).toBeInTheDocument()
    })

    it('displays the market cap in trillions', () => {
      render(<StockHeader stock={baseStock} watchlist={new Set()} toggleWatchlist={vi.fn()} />)
      expect(screen.getByText(/\$3\.\d+T/)).toBeInTheDocument()
    })
  })

  describe('when the stock has STRONG_BUY status', () => {
    it('shows an Excellent badge', () => {
      render(<StockHeader stock={{ ...baseStock, overall_status: 'STRONG_BUY' }} watchlist={new Set()} toggleWatchlist={vi.fn()} />)
      expect(screen.getByText('Excellent')).toBeInTheDocument()
    })
  })

  describe('when the stock has AVOID status', () => {
    it('shows a Poor badge', () => {
      render(<StockHeader stock={{ ...baseStock, overall_status: 'AVOID' }} watchlist={new Set()} toggleWatchlist={vi.fn()} />)
      expect(screen.getByText('Poor')).toBeInTheDocument()
    })
  })

  describe('when the stock is in the watchlist', () => {
    it('shows the filled star character', () => {
      render(<StockHeader stock={baseStock} watchlist={new Set(['AAPL'])} toggleWatchlist={vi.fn()} />)
      expect(screen.getByText('★')).toBeInTheDocument()
    })
  })

  describe('when the watchlist toggle button is clicked', () => {
    it('calls toggleWatchlist with the stock symbol', async () => {
      const toggleWatchlist = vi.fn()
      const { container } = render(
        <StockHeader stock={baseStock} watchlist={new Set()} toggleWatchlist={toggleWatchlist} />
      )
      const buttons = container.querySelectorAll('button')
      buttons[0].click()
      expect(toggleWatchlist).toHaveBeenCalledWith('AAPL')
    })
  })
})

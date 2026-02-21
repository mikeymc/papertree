// ABOUTME: Stock search and detail fixture data for test suites
// ABOUTME: Used by stock search handlers and StockHeader/StockListCard component tests

export const searchResults = [
  { symbol: 'AAPL', company_name: 'Apple Inc.', exchange: 'NASDAQ' },
  { symbol: 'AAPLB', company_name: 'Apple Inc. B Class', exchange: 'NASDAQ' },
]

export const sampleStock = {
  symbol: 'AAPL',
  name: 'Apple Inc.',
  price: 195.50,
  market_cap: 3_000_000_000_000,
  pe_ratio: 28.5,
  debt_to_equity: 1.2,
  revenue_growth: 0.08,
  earnings_growth: 0.12,
  roe: 0.45,
  fcf_yield: 0.04,
  overall_score: 82,
  overall_status: 'excellent',
  criteria_scores: {
    pe_ratio: { score: 85, status: 'good' },
    revenue_growth: { score: 78, status: 'good' },
  },
  price_change_pct: 1.2,
  dividend_yield: 0.005,
}

export const stockDetailResponse = {
  symbol: 'AAPL',
  name: 'Apple Inc.',
  price: 195.50,
  market_cap: 3_000_000_000_000,
  overall_score: 82,
  overall_status: 'excellent',
  pe_ratio: 28.5,
  revenue_growth: 0.08,
  earnings_growth: 0.12,
  criteria_scores: {},
}

export const strategyTemplates = [
  { id: 'growth', name: 'Growth Investor', description: 'Focus on high-growth companies' },
  { id: 'value', name: 'Value Investor', description: 'Focus on undervalued companies' },
]

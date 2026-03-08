// ABOUTME: Dashboard widget fixture data for test suites
// ABOUTME: Used by MSW dashboard handlers — must match shapes consumed by each widget

export const alertsResponse = {
  alerts: {
    triggered: [
      { id: 1, symbol: 'NVDA', condition_type: 'price_above', condition_params: { value: 900 }, is_triggered: true },
    ],
    pending: [
      { id: 2, symbol: 'AAPL', condition_type: 'price_below', condition_params: { value: 150 }, is_triggered: false },
    ],
  },
}

export const watchlistResponse = [
  { symbol: 'AAPL', name: 'Apple Inc.', price: 195.50, price_change_pct: 1.2, overall_score: 82 },
  { symbol: 'MSFT', name: 'Microsoft Corp.', price: 420.00, price_change_pct: -0.5, overall_score: 78 },
]

export const portfoliosResponse = {
  total_value: 125000,
  total_gain_loss: 8500,
  total_gain_loss_pct: 7.3,
  portfolios: [
    { id: 1, name: 'Main Portfolio', value: 125000, gain_loss_pct: 7.3 },
  ],
}

export const thesesResponse = {
  recent_theses: {
    theses: [
      { id: 1, symbol: 'AAPL', name: 'Apple Inc.', thesis: 'Strong competitive moat with ecosystem lock-in.', verdict: 'bullish', character_id: 1, generated_at: '2024-01-15T10:00:00Z' },
      { id: 2, symbol: 'MSFT', name: 'Microsoft Corp.', thesis: 'Cloud dominance via Azure and AI integration.', verdict: 'bullish', character_id: 1, generated_at: '2024-01-14T10:00:00Z' },
    ],
    total_count: 2,
  },
}

export const earningsResponse = {
  upcoming_earnings: {
    earnings: [
      { symbol: 'AAPL', company_name: 'Apple Inc.', earnings_date: '2024-02-01', estimate_eps: 2.10 },
      { symbol: 'NVDA', company_name: 'NVIDIA Corp.', earnings_date: '2024-02-21', estimate_eps: 5.60 },
    ],
    total_count: 2,
  },
}

export const insiderIntentResponse = {
  insider_intent: {
    filings: [
      {
        id: 1,
        symbol: 'AAPL',
        accession_number: '0001234567-26-000001',
        filing_date: '2026-03-05',
        insider_name: 'Tim Cook',
        relationship: 'CEO',
        shares_to_sell: 50000,
        estimated_value: 9750000.0,
        is_10b51_plan: false,
        filing_url: 'https://sec.gov/filing/1',
      },
      {
        id: 2,
        symbol: 'MSFT',
        accession_number: '0001234567-26-000002',
        filing_date: '2026-02-28',
        insider_name: 'Satya Nadella',
        relationship: 'CEO',
        shares_to_sell: 30000,
        estimated_value: 12600000.0,
        is_10b51_plan: true,
        filing_url: 'https://sec.gov/filing/2',
      },
    ],
    total_count: 2,
  },
}

export const moversResponse = {
  gainers: [
    { symbol: 'NVDA', name: 'NVIDIA Corp.', change_pct: 5.2, price: 875.00, overall_status: 'excellent' },
  ],
  losers: [
    { symbol: 'INTC', name: 'Intel Corp.', change_pct: -3.1, price: 32.50, overall_status: 'poor' },
  ],
}

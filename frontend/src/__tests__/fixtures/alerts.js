// ABOUTME: Alerts page fixture data for test suites
// ABOUTME: Matches the shape returned by GET /api/alerts

export const alertsListResponse = {
  alerts: [
    {
      id: 1,
      symbol: 'AAPL',
      condition_type: 'price_below',
      condition_params: { value: 150 },
      status: 'active',
      created_at: '2024-01-01T00:00:00Z',
    },
    {
      id: 2,
      symbol: 'NVDA',
      condition_type: 'score_above',
      condition_params: { value: 80 },
      status: 'triggered',
      triggered_at: '2024-01-15T10:00:00Z',
      created_at: '2024-01-01T00:00:00Z',
    },
  ],
}

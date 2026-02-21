// ABOUTME: Portfolio fixture data for test suites
// ABOUTME: Matches the shape returned by GET /api/portfolios

export const portfoliosListResponse = {
  portfolios: [
    {
      id: 1,
      name: 'My Portfolio',
      description: 'Primary investment portfolio',
      total_value: 50000,
      total_gain_loss: 3500,
      total_gain_loss_pct: 7.5,
      holdings_count: 5,
    },
  ],
}

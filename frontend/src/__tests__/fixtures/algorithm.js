// ABOUTME: Algorithm configuration fixture data for test suites
// ABOUTME: Matches the shape returned by GET /api/algorithm/config

export const algorithmConfigResponse = {
  thresholds: {
    excellent: { min_score: 80, label: 'Excellent' },
    good: { min_score: 60, label: 'Good' },
    fair: { min_score: 40, label: 'Fair' },
    poor: { min_score: 0, label: 'Poor' },
  },
  weights: {
    pe_ratio: 0.2,
    revenue_growth: 0.2,
    earnings_growth: 0.2,
    debt_to_equity: 0.15,
    roe: 0.15,
    fcf_yield: 0.1,
  },
}

export const validationResultResponse = {
  job_id: 'val-123',
  status: 'completed',
  accuracy: 0.82,
  precision: 0.79,
  recall: 0.85,
}

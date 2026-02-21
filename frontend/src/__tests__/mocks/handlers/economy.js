// ABOUTME: MSW handlers for economy/FRED indicator endpoints
// ABOUTME: Returns minimal dashboard data for all FRED series used by Economy page

import { http, HttpResponse } from 'msw'

const dashboardData = {
  FEDFUNDS: { observations: [{ date: '2024-01-01', value: '5.25' }] },
  DGS10: { observations: [{ date: '2024-01-01', value: '4.20' }] },
  CPIAUCSL: { observations: [{ date: '2024-01-01', value: '310.5' }] },
  BAA10Y: { observations: [{ date: '2024-01-01', value: '1.5' }] },
  PPIACO: { observations: [{ date: '2024-01-01', value: '235.0' }] },
  T10Y2Y: { observations: [{ date: '2024-01-01', value: '0.5' }] },
  GDP: { observations: [{ date: '2024-01-01', value: '27000' }] },
  CP: { observations: [{ date: '2024-01-01', value: '3000' }] },
  VIXCLS: { observations: [{ date: '2024-01-01', value: '15.0' }] },
}

export const economyHandlers = [
  http.get('/api/fred/dashboard', () => HttpResponse.json(dashboardData)),
]

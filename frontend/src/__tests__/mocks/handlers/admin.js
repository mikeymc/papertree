// ABOUTME: MSW handlers for admin endpoints
// ABOUTME: Covers conversations, feedback, job stats, portfolios, strategies, user actions

import { http, HttpResponse } from 'msw'

const conversationsResponse = {
  conversations: [
    {
      id: 1,
      title: 'Analyzing AAPL earnings',
      user_email: 'user@example.com',
      created_at: '2024-01-15T10:00:00Z',
      updated_at: '2024-01-15T10:30:00Z',
    },
    {
      id: 2,
      title: 'Portfolio review',
      user_email: 'admin@example.com',
      created_at: '2024-01-14T09:00:00Z',
      updated_at: '2024-01-14T09:45:00Z',
    },
  ],
}

const messagesResponse = {
  messages: [
    { role: 'user', content: 'What do you think of AAPL?', sources: [] },
    { role: 'assistant', content: 'AAPL looks strong with solid fundamentals.', sources: [] },
  ],
}

const feedbackResponse = {
  feedback: [
    {
      id: 1,
      user_email: 'user@example.com',
      feedback_type: 'bug',
      message: 'The chart does not load on Safari.',
      created_at: '2024-01-15T10:00:00Z',
      metadata: JSON.stringify({ page: '/dashboard', browser: 'Safari' }),
    },
  ],
}

const jobStatsResponse = {
  stats: [
    {
      job_type: 'screening',
      total_runs: 24,
      success_count: 22,
      failure_count: 2,
      avg_duration: 45.3,
      last_run: '2024-01-15T10:00:00Z',
    },
  ],
  jobs: [
    {
      id: 1,
      job_type: 'screening',
      status: 'completed',
      started_at: '2024-01-15T10:00:00Z',
      completed_at: '2024-01-15T10:01:00Z',
      duration: 60,
    },
  ],
  time_range: 24,
}

const jobScheduleResponse = {
  schedule: [
    { job_type: 'screening', cron: '0 6 * * 1-5', next_run: '2024-01-16T06:00:00Z', enabled: true },
  ],
}

const adminPortfoliosResponse = {
  portfolios: [
    {
      id: 1,
      name: 'Main Portfolio',
      user_email: 'user@example.com',
      value: 125000,
      gain_loss_pct: 7.3,
    },
    {
      id: 2,
      name: 'Growth Portfolio',
      user_email: 'admin@example.com',
      value: 85000,
      gain_loss_pct: -1.2,
    },
  ],
}

const adminStrategiesResponse = {
  strategies: [
    {
      id: 1,
      name: 'Lynch Tenbagger',
      user_email: 'user@example.com',
      portfolio_name: 'Main Portfolio',
      status: 'active',
    },
    {
      id: 2,
      name: 'Buffett Fortress',
      user_email: 'admin@example.com',
      portfolio_name: 'Growth Portfolio',
      status: 'paused',
    },
  ],
}

const userActionsResponse = {
  events: [
    {
      id: 1,
      path: '/api/stock/AAPL',
      user_email: 'user@example.com',
      user_name: 'Test User',
      details: { symbol: 'AAPL' },
      created_at: '2024-01-15T10:00:00Z',
    },
  ],
  stats: [
    {
      user_id: 1,
      name: 'Test User',
      email: 'user@example.com',
      total_hits: 142,
      last_activity: '2024-01-15T10:00:00Z',
    },
  ],
}

export const adminHandlers = [
  http.get('/api/admin/conversations', () => HttpResponse.json(conversationsResponse)),
  http.get('/api/admin/conversations/:id/messages', () => HttpResponse.json(messagesResponse)),
  http.get('/api/admin/feedback', () => HttpResponse.json(feedbackResponse)),
  http.get('/api/admin/job_stats', () => HttpResponse.json(jobStatsResponse)),
  http.get('/api/admin/job_schedule', () => HttpResponse.json(jobScheduleResponse)),
  http.get('/api/admin/portfolios', () => HttpResponse.json(adminPortfoliosResponse)),
  http.get('/api/admin/strategies', () => HttpResponse.json(adminStrategiesResponse)),
  http.get('/api/admin/user_actions', () => HttpResponse.json(userActionsResponse)),
]

// ABOUTME: MSW handlers for onboarding flow endpoints
// ABOUTME: Covers strategy templates, expertise levels, character selection, and completion

import { http, HttpResponse } from 'msw'
import { strategyTemplates } from '../../fixtures/stocks.js'
import { charactersResponse } from '../../fixtures/settings.js'

export const onboardingHandlers = [
  http.get('/api/strategy-templates', () => HttpResponse.json({ templates: {
    global_titans: { id: 'global_titans', name: 'Global Titans', description: 'Large-cap global leaders' },
    lynch_tenbagger: { id: 'lynch_tenbagger', name: 'Lynch Tenbagger', description: 'Peter Lynch growth strategy' },
    buffett_fortress: { id: 'buffett_fortress', name: 'Buffett Fortress', description: 'Warren Buffett value strategy' },
  }})),

  http.put('/api/settings/expertise-level', () => HttpResponse.json({ success: true })),

  http.put('/api/settings/character', () => HttpResponse.json({ success: true })),

  http.post('/api/user/complete_onboarding', () => HttpResponse.json({ success: true })),

  http.post('/api/strategies/quick-start', () => HttpResponse.json({ success: true, portfolio_id: 1 })),
]

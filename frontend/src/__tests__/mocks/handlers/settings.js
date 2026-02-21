// ABOUTME: MSW handlers for settings and character API endpoints
// ABOUTME: Covers all settings tabs: appearance, character, expertise, email briefs

import { http, HttpResponse } from 'msw'
import { settingsResponse, charactersResponse, activeCharacterResponse, expertiseLevelResponse, emailBriefsResponse } from '../../fixtures/settings.js'

export const settingsHandlers = [
  http.get('/api/settings', () => HttpResponse.json(settingsResponse)),
  http.put('/api/settings', async ({ request }) => {
    const body = await request.json()
    return HttpResponse.json({ ...settingsResponse, ...body })
  }),

  http.get('/api/characters', () => HttpResponse.json({ characters: charactersResponse })),
  http.get('/api/settings/character', () => HttpResponse.json(activeCharacterResponse)),
  http.put('/api/settings/character', async ({ request }) => {
    const body = await request.json()
    return HttpResponse.json({ character_id: body.character_id })
  }),

  http.get('/api/settings/expertise-level', () => HttpResponse.json(expertiseLevelResponse)),
  http.put('/api/settings/expertise-level', async ({ request }) => {
    const body = await request.json()
    return HttpResponse.json({ expertise_level: body.expertise_level })
  }),

  http.get('/api/settings/email-briefs', () => HttpResponse.json(emailBriefsResponse)),
  http.put('/api/settings/email-briefs', async ({ request }) => {
    const body = await request.json()
    return HttpResponse.json({ ...emailBriefsResponse, ...body })
  }),
]

// ABOUTME: Settings fixture data for test suites
// ABOUTME: Matches shapes returned by settings and character API endpoints

export const settingsResponse = {
  notifications_enabled: true,
  email_alerts: false,
  timezone: 'America/New_York',
}

export const charactersResponse = [
  { id: 1, name: 'Peter Lynch', description: 'Growth at reasonable price', slug: 'lynch' },
  { id: 2, name: 'Warren Buffett', description: 'Value investing', slug: 'buffett' },
]

export const activeCharacterResponse = { active_character: 'lynch', character_id: 1 }

export const expertiseLevelResponse = { expertise_level: 'intermediate' }

export const emailBriefsResponse = { enabled: false, frequency: 'weekly' }

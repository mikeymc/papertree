// ABOUTME: Combines all MSW domain handlers into a single defaultHandlers array
// ABOUTME: Order matters — dashboard handlers win for /api/dashboard/* (first-match)

import { authHandlers } from './auth.js'
import { dashboardHandlers } from './dashboard.js'
import { stockHandlers } from './stocks.js'
import { alertsHandlers } from './alerts.js'
import { portfoliosHandlers } from './portfolios.js'
import { strategiesHandlers } from './strategies.js'
import { settingsHandlers } from './settings.js'
import { algorithmHandlers } from './algorithm.js'
import { onboardingHandlers } from './onboarding.js'
import { feedbackHandlers } from './feedback.js'
import { economyHandlers } from './economy.js'

export const defaultHandlers = [
  ...authHandlers,
  ...dashboardHandlers,
  ...stockHandlers,
  ...alertsHandlers,
  ...portfoliosHandlers,
  ...strategiesHandlers,
  ...settingsHandlers,
  ...algorithmHandlers,
  ...onboardingHandlers,
  ...feedbackHandlers,
  ...economyHandlers,
]

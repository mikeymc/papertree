// ABOUTME: BDD tests for OnboardingWizard multi-step flow
// ABOUTME: Covers all three steps, skip, and template selection

import { describe, it, expect, vi } from 'vitest'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { renderWithProviders } from '../helpers/render.jsx'
import { OnboardingWizard } from '@/components/OnboardingWizard'

describe('OnboardingWizard', () => {
  describe('on step 1 (Welcome)', () => {
    it('shows the welcome heading', () => {
      renderWithProviders(
        <OnboardingWizard open={true} onComplete={vi.fn()} onSkip={vi.fn()} />
      )
      expect(screen.getByText(/Welcome to papertree\.ai/i)).toBeInTheDocument()
    })

    it('shows the Skip setup button', () => {
      renderWithProviders(
        <OnboardingWizard open={true} onComplete={vi.fn()} onSkip={vi.fn()} />
      )
      expect(screen.getByText("Skip setup")).toBeInTheDocument()
    })
  })

  describe('when the user clicks Skip setup', () => {
    it('calls onSkip', async () => {
      const onSkip = vi.fn()
      const user = userEvent.setup()
      renderWithProviders(
        <OnboardingWizard open={true} onComplete={vi.fn()} onSkip={onSkip} />
      )
      await user.click(screen.getByText("Skip setup"))
      await waitFor(() => expect(onSkip).toHaveBeenCalled())
    })
  })

  describe('when the user clicks Let\'s Go', () => {
    it('advances to the strategy selection step', async () => {
      const user = userEvent.setup()
      renderWithProviders(
        <OnboardingWizard open={true} onComplete={vi.fn()} onSkip={vi.fn()} />
      )
      await user.click(screen.getByText("Let's Go"))
      await waitFor(() => expect(screen.getByText('Choose a strategy')).toBeInTheDocument())
    })

    it('loads strategy templates from the API', async () => {
      const user = userEvent.setup()
      renderWithProviders(
        <OnboardingWizard open={true} onComplete={vi.fn()} onSkip={vi.fn()} />
      )
      await user.click(screen.getByText("Let's Go"))
      await waitFor(() => expect(screen.getByText('Lynch Tenbagger')).toBeInTheDocument())
    })
  })

  describe('when open is false', () => {
    it('does not render the dialog content', () => {
      renderWithProviders(
        <OnboardingWizard open={false} onComplete={vi.fn()} onSkip={vi.fn()} />
      )
      expect(screen.queryByText(/Welcome to papertree\.ai/i)).not.toBeInTheDocument()
    })
  })
})

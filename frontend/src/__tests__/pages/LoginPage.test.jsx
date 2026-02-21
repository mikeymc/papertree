// ABOUTME: BDD tests for LoginPage
// ABOUTME: Mocks AuthForms to isolate page rendering from form logic

import { describe, it, expect, vi } from 'vitest'
import { renderWithProviders, screen } from '../helpers/render.jsx'
import LoginPage from '@/pages/LoginPage'

vi.mock('@/components/auth/AuthForms', () => ({
  AuthForms: () => <div data-testid="auth-forms">Auth Forms</div>,
}))

describe('LoginPage', () => {
  describe('on initial render', () => {
    it('renders the auth forms component', () => {
      renderWithProviders(<LoginPage />)
      expect(screen.getByTestId('auth-forms')).toBeInTheDocument()
    })
  })
})

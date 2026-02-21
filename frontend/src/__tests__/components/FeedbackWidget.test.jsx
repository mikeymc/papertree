// ABOUTME: BDD tests for FeedbackWidget component
// ABOUTME: Covers form rendering, disabled state, submission success, and API errors

import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { server } from '../mocks/server.js'
import { FeedbackWidget } from '@/components/FeedbackWidget'

describe('FeedbackWidget', () => {
  describe('when opened', () => {
    it('shows the Send Feedback heading', () => {
      render(<FeedbackWidget isOpen={true} onClose={vi.fn()} />)
      expect(screen.getByText('Send Feedback')).toBeInTheDocument()
    })

    it('disables the submit button when the textarea is empty', () => {
      const { container } = render(<FeedbackWidget isOpen={true} onClose={vi.fn()} />)
      const submitBtn = container.querySelector('button[type="submit"]')
      expect(submitBtn).toBeDisabled()
    })
  })

  describe('when the user types feedback', () => {
    it('enables the submit button', async () => {
      const user = userEvent.setup()
      const { container } = render(<FeedbackWidget isOpen={true} onClose={vi.fn()} />)
      await user.type(screen.getByPlaceholderText(/Tell us what you think/i), 'Great app!')
      const submitBtn = container.querySelector('button[type="submit"]')
      expect(submitBtn).not.toBeDisabled()
    })
  })

  describe('when the form is submitted successfully', () => {
    it('shows the thank you message', async () => {
      const user = userEvent.setup()
      const { container } = render(<FeedbackWidget isOpen={true} onClose={vi.fn()} />)
      await user.type(screen.getByPlaceholderText(/Tell us what you think/i), 'Great app!')
      const submitBtn = container.querySelector('button[type="submit"]')
      await user.click(submitBtn)
      await waitFor(() => expect(screen.getByText(/Thank you for your feedback/i)).toBeInTheDocument())
    })
  })

  describe('when the API returns an error', () => {
    it('shows an error message', async () => {
      server.use(http.post('/api/feedback', () => new HttpResponse(null, { status: 500 })))
      const user = userEvent.setup()
      const { container } = render(<FeedbackWidget isOpen={true} onClose={vi.fn()} />)
      await user.type(screen.getByPlaceholderText(/Tell us what you think/i), 'Bug report')
      const submitBtn = container.querySelector('button[type="submit"]')
      await user.click(submitBtn)
      await waitFor(() => expect(screen.getByText(/Failed to submit feedback/i)).toBeInTheDocument())
    })
  })

  describe('when isOpen is false', () => {
    it('renders nothing', () => {
      const { container } = render(<FeedbackWidget isOpen={false} onClose={vi.fn()} />)
      expect(container.firstChild).toBeNull()
    })
  })
})

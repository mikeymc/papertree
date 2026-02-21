// ABOUTME: BDD tests for SearchPopover component
// ABOUTME: Covers debounced search, result display, keyboard nav, and selection

import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import SearchPopover from '@/components/SearchPopover'

function renderSearchPopover(onSelect = vi.fn()) {
  return render(
    <BrowserRouter>
      <SearchPopover onSelect={onSelect} />
    </BrowserRouter>
  )
}

describe('SearchPopover', () => {
  describe('on initial render', () => {
    it('shows a search input', () => {
      renderSearchPopover()
      expect(screen.getByRole('textbox')).toBeInTheDocument()
    })
  })

  describe('when the user types a query', () => {
    it('shows matching results in the dropdown', async () => {
      const user = userEvent.setup()
      renderSearchPopover()
      await user.type(screen.getByRole('textbox'), 'AAPL')
      await waitFor(() => expect(screen.getByText('Apple Inc.')).toBeInTheDocument())
    })
  })

  describe('when the user selects a result', () => {
    it('calls onSelect with the stock symbol', async () => {
      const onSelect = vi.fn()
      const user = userEvent.setup()
      renderSearchPopover(onSelect)
      await user.type(screen.getByRole('textbox'), 'AAPL')
      await waitFor(() => expect(screen.getByText('Apple Inc.')).toBeInTheDocument())
      await user.click(screen.getByText('Apple Inc.'))
      expect(onSelect).toHaveBeenCalledWith('AAPL')
    })
  })

  describe('when the user presses Enter', () => {
    it('selects the highlighted result and calls onSelect', async () => {
      const onSelect = vi.fn()
      const user = userEvent.setup()
      renderSearchPopover(onSelect)
      await user.type(screen.getByRole('textbox'), 'AAPL')
      await waitFor(() => expect(screen.getByText('Apple Inc.')).toBeInTheDocument())
      await user.keyboard('{Enter}')
      expect(onSelect).toHaveBeenCalledWith('AAPL')
    })
  })

  describe('when the user presses Escape', () => {
    it('closes the dropdown', async () => {
      const user = userEvent.setup()
      renderSearchPopover()
      await user.type(screen.getByRole('textbox'), 'AAPL')
      await waitFor(() => expect(screen.getByText('Apple Inc.')).toBeInTheDocument())
      await user.keyboard('{Escape}')
      await waitFor(() => expect(screen.queryByText('Apple Inc.')).not.toBeInTheDocument())
    })
  })
})

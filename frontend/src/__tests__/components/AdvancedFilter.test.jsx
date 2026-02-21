// ABOUTME: BDD tests for AdvancedFilter component
// ABOUTME: Covers filter inputs, reset behavior, and isOpen guard

import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import AdvancedFilter from '@/components/AdvancedFilter'

const defaultFilters = {
  countries: [],
  institutionalOwnership: { max: null },
  revenueGrowth: { min: null },
  incomeGrowth: { min: null },
  debtToEquity: { max: null },
  marketCap: { max: null },
  peRatio: { max: null },
}

describe('AdvancedFilter', () => {
  describe('when isOpen is false', () => {
    it('renders nothing', () => {
      const { container } = render(
        <AdvancedFilter
          filters={defaultFilters}
          onFiltersChange={vi.fn()}
          isOpen={false}
          onToggle={vi.fn()}
        />
      )
      expect(container.firstChild).toBeNull()
    })
  })

  describe('when isOpen is true', () => {
    it('shows the Inst. Own % label', () => {
      render(
        <AdvancedFilter
          filters={defaultFilters}
          onFiltersChange={vi.fn()}
          isOpen={true}
          onToggle={vi.fn()}
        />
      )
      expect(screen.getByText(/Inst\. Own/i)).toBeInTheDocument()
    })

    it('calls onFiltersChange when inst ownership changes', async () => {
      const onFiltersChange = vi.fn()
      const user = userEvent.setup()
      render(
        <AdvancedFilter
          filters={defaultFilters}
          onFiltersChange={onFiltersChange}
          isOpen={true}
          onToggle={vi.fn()}
        />
      )
      const input = screen.getByPlaceholderText('75')
      await user.type(input, '50')
      expect(onFiltersChange).toHaveBeenCalled()
    })

    it('resets all filters when the reset button is clicked', async () => {
      const onFiltersChange = vi.fn()
      const user = userEvent.setup()
      render(
        <AdvancedFilter
          filters={{ ...defaultFilters, institutionalOwnership: { max: 50 } }}
          onFiltersChange={onFiltersChange}
          isOpen={true}
          onToggle={vi.fn()}
        />
      )
      const buttons = screen.getAllByRole('button')
      const resetBtn = buttons.find(b => b.querySelector('svg'))
      await user.click(resetBtn)
      const lastCall = onFiltersChange.mock.calls[onFiltersChange.mock.calls.length - 1][0]
      expect(lastCall.institutionalOwnership.max).toBeNull()
    })
  })
})

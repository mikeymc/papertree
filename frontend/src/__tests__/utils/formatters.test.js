// ABOUTME: BDD tests for formatting utility functions
// ABOUTME: Covers formatLargeCurrency, parseDate, and formatLocal comprehensively

import { describe, it, expect } from 'vitest'
import { formatLargeCurrency, parseDate, formatLocal } from '@/utils/formatters.js'

describe('formatLargeCurrency', () => {
  describe('when given null or undefined', () => {
    it('returns a dash', () => {
      expect(formatLargeCurrency(null)).toBe('-')
      expect(formatLargeCurrency(undefined)).toBe('-')
    })
  })

  describe('when given a non-numeric string', () => {
    it('returns a dash', () => {
      expect(formatLargeCurrency('abc')).toBe('-')
    })
  })

  describe('when given a value in the trillions', () => {
    it('formats with T suffix and 2 decimal places', () => {
      expect(formatLargeCurrency(3_000_000_000_000)).toBe('$3.00T')
      expect(formatLargeCurrency(1_500_000_000_000)).toBe('$1.50T')
    })
  })

  describe('when given a value in the billions', () => {
    it('formats with B suffix and 2 decimal places', () => {
      expect(formatLargeCurrency(2_500_000_000)).toBe('$2.50B')
    })
  })

  describe('when given a value in the millions', () => {
    it('formats with M suffix and 2 decimal places', () => {
      expect(formatLargeCurrency(500_000_000)).toBe('$500.00M')
    })
  })

  describe('when given a value in the thousands', () => {
    it('formats with K suffix and 2 decimal places', () => {
      expect(formatLargeCurrency(5_000)).toBe('$5.00K')
    })
  })

  describe('when given a small value', () => {
    it('formats with 2 decimal places and no suffix', () => {
      expect(formatLargeCurrency(99.5)).toBe('$99.50')
    })
  })

  describe('when showCurrencySymbol is false', () => {
    it('omits the dollar sign', () => {
      expect(formatLargeCurrency(1_000_000_000, false)).toBe('1.00B')
    })
  })
})

describe('parseDate', () => {
  describe('when given null or empty input', () => {
    it('returns null', () => {
      expect(parseDate(null)).toBeNull()
      expect(parseDate('')).toBeNull()
      expect(parseDate(undefined)).toBeNull()
    })
  })

  describe('when given an ISO string with Z timezone', () => {
    it('returns a valid Date', () => {
      const result = parseDate('2024-01-15T10:00:00Z')
      expect(result).toBeInstanceOf(Date)
      expect(result.getFullYear()).toBe(2024)
    })
  })

  describe('when given a naked ISO string without timezone', () => {
    it('treats it as UTC and returns a valid Date', () => {
      const result = parseDate('2024-01-15T10:00:00')
      expect(result).toBeInstanceOf(Date)
      expect(result.getFullYear()).toBe(2024)
    })
  })

  describe('when given a Date object', () => {
    it('returns the same Date object', () => {
      const date = new Date('2024-06-01')
      const result = parseDate(date)
      expect(result).toBeInstanceOf(Date)
    })
  })

  describe('when given an invalid string', () => {
    it('returns null', () => {
      expect(parseDate('not-a-date')).toBeNull()
    })
  })
})

describe('formatLocal', () => {
  describe('when given a valid ISO date string', () => {
    it('returns a formatted date string', () => {
      const result = formatLocal('2024-01-15T10:00:00Z')
      expect(result).toMatch(/Jan/)
      expect(result).toMatch(/15/)
    })
  })

  describe('when given null or invalid input', () => {
    it('returns an em dash', () => {
      expect(formatLocal(null)).toBe('—')
      expect(formatLocal('')).toBe('—')
    })
  })

  describe('when includeYear is false', () => {
    it('omits the year from the output', () => {
      const result = formatLocal('2024-01-15T10:00:00Z', false)
      expect(result).not.toMatch(/2024/)
    })
  })

  describe('when includeTime is false', () => {
    it('omits the time from the output', () => {
      const result = formatLocal('2024-01-15T10:00:00Z', true, false)
      expect(result).not.toMatch(/\d{2}:\d{2}/)
    })
  })
})

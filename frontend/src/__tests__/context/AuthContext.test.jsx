// ABOUTME: BDD tests for AuthContext — auth check, logout, and state management
// ABOUTME: Uses MSW to control /api/auth/user responses per test

import { describe, it, expect } from 'vitest'
import { renderHook, waitFor, act } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { server } from '../mocks/server.js'
import { AuthProvider, useAuth } from '@/context/AuthContext'
import { authenticatedUser } from '../fixtures/users.js'

function wrapper({ children }) {
  return <AuthProvider>{children}</AuthProvider>
}

describe('AuthContext', () => {
  describe('when the API returns a valid user', () => {
    it('sets the user in context', async () => {
      const { result } = renderHook(() => useAuth(), { wrapper })
      await waitFor(() => expect(result.current.loading).toBe(false))
      expect(result.current.user).toMatchObject({ email: authenticatedUser.email })
    })
  })

  describe('when the API returns 401', () => {
    it('sets user to null', async () => {
      server.use(http.get('/api/auth/user', () => new HttpResponse(null, { status: 401 })))
      const { result } = renderHook(() => useAuth(), { wrapper })
      await waitFor(() => expect(result.current.loading).toBe(false))
      expect(result.current.user).toBeNull()
    })
  })

  describe('when the API throws a network error', () => {
    it('sets user to null', async () => {
      server.use(http.get('/api/auth/user', () => HttpResponse.error()))
      const { result } = renderHook(() => useAuth(), { wrapper })
      await waitFor(() => expect(result.current.loading).toBe(false))
      expect(result.current.user).toBeNull()
    })
  })

  describe('when logout is called', () => {
    it('clears the user from context', async () => {
      const { result } = renderHook(() => useAuth(), { wrapper })
      await waitFor(() => expect(result.current.loading).toBe(false))
      expect(result.current.user).not.toBeNull()

      await act(async () => { await result.current.logout() })
      expect(result.current.user).toBeNull()
    })
  })
})

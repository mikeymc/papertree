// ABOUTME: BDD tests for ChatContext — conversation CRUD operations
// ABOUTME: Tests state transitions for add, update, remove, and set

import { describe, it, expect } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { ChatProvider, useChatContext } from '@/context/ChatContext'

function wrapper({ children }) {
  return <ChatProvider>{children}</ChatProvider>
}

describe('ChatContext', () => {
  describe('on initial render', () => {
    it('starts with an empty conversation list', () => {
      const { result } = renderHook(() => useChatContext(), { wrapper })
      expect(result.current.conversations).toEqual([])
    })

    it('starts with no active conversation', () => {
      const { result } = renderHook(() => useChatContext(), { wrapper })
      expect(result.current.activeConversationId).toBeNull()
    })
  })

  describe('when addConversation is called', () => {
    it('prepends the conversation to the list', () => {
      const { result } = renderHook(() => useChatContext(), { wrapper })
      act(() => result.current.addConversation({ id: '1', title: 'First' }))
      act(() => result.current.addConversation({ id: '2', title: 'Second' }))
      expect(result.current.conversations[0].id).toBe('2')
      expect(result.current.conversations[1].id).toBe('1')
    })
  })

  describe('when updateConversationTitle is called', () => {
    it('updates only the matching conversation title', () => {
      const { result } = renderHook(() => useChatContext(), { wrapper })
      act(() => result.current.addConversation({ id: '1', title: 'Old Title' }))
      act(() => result.current.updateConversationTitle('1', 'New Title'))
      expect(result.current.conversations[0].title).toBe('New Title')
    })
  })

  describe('when removeConversation is called', () => {
    it('removes the matching conversation from the list', () => {
      const { result } = renderHook(() => useChatContext(), { wrapper })
      act(() => result.current.addConversation({ id: '1', title: 'To Remove' }))
      act(() => result.current.removeConversation('1'))
      expect(result.current.conversations).toEqual([])
    })
  })

  describe('when setActiveConversationId is called', () => {
    it('updates the active conversation id', () => {
      const { result } = renderHook(() => useChatContext(), { wrapper })
      act(() => result.current.setActiveConversationId('abc-123'))
      expect(result.current.activeConversationId).toBe('abc-123')
    })
  })
})

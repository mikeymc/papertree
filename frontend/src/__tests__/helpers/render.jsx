// ABOUTME: renderWithProviders helper — wraps components in full app provider stack
// ABOUTME: Mirrors the provider nesting from main.jsx for realistic test rendering

import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter, MemoryRouter } from 'react-router-dom'
import { AuthProvider } from '@/context/AuthContext'
import { ChatProvider } from '@/context/ChatContext'
import { ThemeProvider } from '@/components/theme-provider'

function AllProviders({ children, routerEntries }) {
  const Router = routerEntries
    ? ({ children }) => <MemoryRouter initialEntries={routerEntries}>{children}</MemoryRouter>
    : BrowserRouter

  return (
    <Router>
      <AuthProvider>
        <ChatProvider>
          <ThemeProvider defaultTheme="light" storageKey="vite-ui-theme" disableFetch={true}>
            {children}
          </ThemeProvider>
        </ChatProvider>
      </AuthProvider>
    </Router>
  )
}

export function renderWithProviders(ui, { routerEntries, ...options } = {}) {
  return render(ui, {
    wrapper: ({ children }) => (
      <AllProviders routerEntries={routerEntries}>{children}</AllProviders>
    ),
    ...options,
  })
}

export { screen, waitFor, within, userEvent }

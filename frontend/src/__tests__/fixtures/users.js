// ABOUTME: User fixture data for test suites
// ABOUTME: Provides consistent user objects reused across auth and page tests

export const authenticatedUser = {
  id: 'user-123',
  email: 'test@example.com',
  name: 'Test User',
  is_admin: false,
  has_completed_onboarding: true,
  feature_flags: { dashboard: false },
}

export const adminUser = {
  id: 'admin-456',
  email: 'admin@example.com',
  name: 'Admin User',
  is_admin: true,
  has_completed_onboarding: true,
  feature_flags: { dashboard: true },
}

export const newUser = {
  id: 'new-789',
  email: 'new@example.com',
  name: 'New User',
  is_admin: false,
  has_completed_onboarding: false,
  feature_flags: { dashboard: false },
}

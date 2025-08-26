import { describe, it, expect, beforeAll, afterAll, vi } from 'vitest'
import React from 'react'
import { render } from '@testing-library/react'
import App from './App'

// Mock fetch globally for this test suite
beforeAll(() => {
  global.fetch = vi.fn(() =>
    Promise.resolve({
      ok: true,
      status: 200,
      text: async () => JSON.stringify([]),   // supports res.text()
      json: async () => ([]),                 // supports res.json()
    })
  ) as any
})

afterAll(() => {
  vi.restoreAllMocks()
})

describe('App', () => {
  it('renders title and tagline', () => {
    const { getByText } = render(<App />)
    expect(getByText(/AI-Powered Interview Preparation/i)).toBeTruthy()
    expect(getByText(/Generate realistic interview questions/i)).toBeTruthy()
  })
})

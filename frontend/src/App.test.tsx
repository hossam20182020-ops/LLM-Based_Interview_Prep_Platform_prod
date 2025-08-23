import { describe, it, expect } from 'vitest'
import React from 'react'
import { render } from '@testing-library/react'
import App from './App'

describe('App', () => {
  it('renders title and tagline', () => {
    const { getByText } = render(<App />)
    expect(getByText(/AI-Powered Interview Preparation/i)).toBeTruthy()
    // Tagline added below the title
    expect(getByText(/Generate realistic interview questions/i)).toBeTruthy()
  })
})

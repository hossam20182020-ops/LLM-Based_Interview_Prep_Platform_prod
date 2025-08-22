import { describe, it, expect } from 'vitest'
import React from 'react'
import { render } from '@testing-library/react'
import App from './App'

describe('App', () => {
  it('renders title', () => {
    const { getByText } = render(<App />)
    expect(getByText(/LLM Interview Prep/i)).toBeTruthy()
  })
})

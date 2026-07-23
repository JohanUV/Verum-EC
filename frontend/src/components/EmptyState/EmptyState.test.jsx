import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import EmptyState from './EmptyState.jsx'

describe('EmptyState', () => {
  it('renderiza el contenido hijo', () => {
    render(<EmptyState icono="fa-user-shield"><p>Sin resultados</p></EmptyState>)
    expect(screen.getByText('Sin resultados')).toBeTruthy()
  })
})

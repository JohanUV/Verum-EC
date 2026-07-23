import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import RiskPill from './RiskPill.jsx'

describe('RiskPill', () => {
  it('muestra "Alerta" para semaforo alerta', () => {
    render(<RiskPill semaforo="alerta" />)
    expect(screen.getByText('Alerta')).toBeTruthy()
  })
  it('muestra "Revisar" para semaforo atencion', () => {
    render(<RiskPill semaforo="atencion" />)
    expect(screen.getByText('Revisar')).toBeTruthy()
  })
  it('usa "Limpio" como valor por defecto', () => {
    render(<RiskPill semaforo="desconocido" />)
    expect(screen.getByText('Limpio')).toBeTruthy()
  })
})

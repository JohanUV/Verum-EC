import { describe, expect, it } from 'vitest'
import { RUTAS, rutasPermitidas } from './routes.jsx'

describe('RUTAS', () => {
  it('define cedula, nombre e historial (la busqueda masiva fue eliminada)', () => {
    expect(RUTAS.map(r => r.id)).toEqual(['cedula', 'nombre', 'historial'])
  })

  it('historial exige el permiso "historial"', () => {
    expect(RUTAS.find(r => r.id === 'historial').permiso).toBe('historial')
  })
})

describe('rutasPermitidas', () => {
  it('un rol sin permisos extra solo ve las rutas libres', () => {
    const ids = rutasPermitidas(() => false).map(r => r.id)
    expect(ids).toEqual(['cedula', 'nombre'])
  })

  it('el admin ve todas las rutas', () => {
    const ids = rutasPermitidas(() => true).map(r => r.id)
    expect(ids).toEqual(['cedula', 'nombre', 'historial'])
  })
})

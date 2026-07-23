import { afterEach, describe, expect, it, vi } from 'vitest'
import { getJSON, postJSON } from './api.js'

afterEach(() => vi.restoreAllMocks())

describe('postJSON', () => {
  it('envia JSON y devuelve ok + data', async () => {
    global.fetch = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ folio: 'VK-1' }) })
    const r = await postJSON('/api/verificar', { cedula: '123' })
    expect(global.fetch).toHaveBeenCalledWith('/api/verificar', expect.objectContaining({
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ cedula: '123' }),
    }))
    expect(r.ok).toBe(true)
    expect(r.data.folio).toBe('VK-1')
  })

  it('devuelve ok=false cuando el servidor responde error', async () => {
    global.fetch = vi.fn().mockResolvedValue({ ok: false, json: async () => ({ error: 'Cedula invalida' }) })
    const r = await postJSON('/api/verificar', { cedula: 'x' })
    expect(r.ok).toBe(false)
    expect(r.data.error).toBe('Cedula invalida')
  })

  it('tolera respuestas sin JSON', async () => {
    global.fetch = vi.fn().mockResolvedValue({ ok: false, json: async () => { throw new Error('no json') } })
    const r = await postJSON('/api/x')
    expect(r.data).toEqual({})
  })
})

describe('getJSON', () => {
  it('lee JSON de la URL', async () => {
    global.fetch = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ historial: [] }) })
    const r = await getJSON('/api/historial')
    expect(r.ok).toBe(true)
    expect(r.data.historial).toEqual([])
  })
})

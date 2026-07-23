import { describe, expect, it } from 'vitest'
import { COLOR_SCORE, esc } from './formato.js'

describe('COLOR_SCORE', () => {
  it('score 0 es verde (sin riesgo)', () => {
    expect(COLOR_SCORE(0)).toBe('var(--success)')
  })
  it('score medio es amarillo', () => {
    expect(COLOR_SCORE(30)).toBe('var(--warning)')
  })
  it('score alto es rojo', () => {
    expect(COLOR_SCORE(80)).toBe('var(--danger)')
  })
})

describe('esc', () => {
  it('escapa caracteres HTML peligrosos', () => {
    expect(esc('<script>"a" & b</script>'))
      .toBe('&lt;script&gt;&quot;a&quot; &amp; b&lt;/script&gt;')
  })
  it('tolera null y undefined', () => {
    expect(esc(null)).toBe('')
    expect(esc(undefined)).toBe('')
  })
})

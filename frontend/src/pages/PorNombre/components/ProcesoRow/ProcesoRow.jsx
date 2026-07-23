// Fila expandible de un proceso judicial: al abrirla carga las partes (CLEX).
import { useState } from 'react'
import { postJSON } from '@/services/api'
import { useToast } from '@/hooks/useToast/useToast.js'

export default function ProcesoRow({ p }) {
  const showToast = useToast()
  const [abierto, setAbierto] = useState(false)
  // detalle: null (sin cargar) | {cargando:true} | {error} | {actores,demandados,...}
  const [detalle, setDetalle] = useState(null)

  async function toggle() {
    const abrir = !abierto
    setAbierto(abrir)
    if (!abrir || detalle) return
    setDetalle({ cargando: true })
    try {
      const { ok, data } = await postJSON('/api/proceso-detalle', { idJuicio: p.numero })
      if (!ok) { setDetalle({ error: data.error || 'Detalle no disponible' }); return }
      setDetalle(data)
    } catch (e) {
      setDetalle({ error: 'Error de conexion' })
    }
  }

  async function abrirPortal(ev) {
    ev.stopPropagation()
    try {
      await navigator.clipboard.writeText(p.numero)
      showToast('N° de proceso copiado. Pegalo en el buscador del portal.', 'success')
    } catch (e) {
      showToast('Proceso: ' + p.numero + ' (copialo manualmente)', 'success')
    }
    window.open('https://procesosjudiciales.funcionjudicial.gob.ec/busqueda-filtros', '_blank')
  }

  const lista = arr => (arr && arr.length)
    ? arr.map((n, i) => <li key={i}>{n}</li>)
    : <li style={{ color: 'var(--text-muted)' }}>— Sin registros —</li>

  return (
    <>
      <tr className="proc-row" onClick={toggle}>
        <td><i className={`fas fa-chevron-right chev ${abierto ? 'open' : ''}`}></i>{p.numero}</td>
        <td>{p.tipo}</td>
        <td>{p.provincia || '—'}</td>
        <td>{p.anio}</td>
        <td>{p.rol}</td>
        <td><span className={`pill ${p.estado === 'Activo' ? 'activo' : 'inactivo'}`}>{p.estado}</span></td>
      </tr>
      {abierto && (
        <tr className="detail-tr">
          <td colSpan={6}>
            {detalle && detalle.cargando && (
              <div style={{ padding: '1.25rem', color: 'var(--text-muted)' }}>
                <i className="fas fa-spinner fa-spin"></i> Cargando partes del proceso...
              </div>
            )}
            {detalle && detalle.error && (
              <div style={{ padding: '1.25rem', color: 'var(--warning)' }}>
                <i className="fas fa-lock"></i> {detalle.error}
              </div>
            )}
            {detalle && !detalle.cargando && !detalle.error && (
              <div className="proc-detail">
                <div className="pd-grid">
                  <div>
                    <div className="pd-label"><i className="fas fa-user-check"></i> Actor(es) / Demandante</div>
                    <ul>{lista(detalle.actores)}</ul>
                  </div>
                  <div>
                    <div className="pd-label"><i className="fas fa-user-tag"></i> Demandado(s)</div>
                    <ul>{lista(detalle.demandados)}</ul>
                  </div>
                </div>
                <div className="pd-foot">
                  <i className="fas fa-building-columns"></i> {detalle.judicatura || '—'}{detalle.ciudad ? ` · ${detalle.ciudad}` : ''}
                </div>
                <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginTop: '0.85rem', alignItems: 'center' }}>
                  <code style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border)', padding: '6px 10px', borderRadius: 8, fontSize: '0.82rem', color: 'var(--text-primary)' }}>{p.numero}</code>
                  <button className="rc-link" style={{ cursor: 'pointer', border: '1px solid var(--border)' }} onClick={abrirPortal}>
                    <i className="fas fa-copy"></i> Copiar y abrir portal oficial
                  </button>
                </div>
              </div>
            )}
          </td>
        </tr>
      )}
    </>
  )
}

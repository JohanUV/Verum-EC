// Historial de consultas (auditoria LOPDP). Solo visible con permiso "historial".
import { useEffect, useState } from 'react'
import { getJSON } from '@/services/api'
import { COLOR_SCORE } from '@/utils/formato'
import EmptyState from '@/components/EmptyState/EmptyState.jsx'
import RiskPill from '@/components/RiskPill/RiskPill.jsx'

export default function Historial({ activa, onReconsultar }) {
  // estado: {tipo:'cargando'} | {tipo:'error'} | {tipo:'ok', historial}
  const [estado, setEstado] = useState({ tipo: 'cargando' })

  useEffect(() => { if (activa) cargar() }, [activa])

  async function cargar() {
    setEstado({ tipo: 'cargando' })
    try {
      const { data } = await getJSON('/api/historial')
      setEstado({ tipo: 'ok', historial: data.historial || [] })
    } catch (e) {
      setEstado({ tipo: 'error' })
    }
  }

  return (
    <>
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 10 }}>
          <div>
            <h3 style={{ margin: 0, fontSize: '1rem' }}><i className="fas fa-clock-rotate-left" aria-hidden="true"></i> Historial de consultas</h3>
            <p style={{ margin: '4px 0 0', fontSize: '0.8rem', color: 'var(--text-muted)' }}>Registro de auditoría de las verificaciones realizadas.</p>
          </div>
          <button className="btn" onClick={cargar}
                  style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', color: 'var(--text-primary)', height: 'auto', padding: '10px 18px' }}>
            <i className="fas fa-rotate"></i> Actualizar
          </button>
        </div>
      </div>

      {estado.tipo === 'cargando' && (
        <EmptyState icono="fa-spinner fa-spin"><p>Cargando...</p></EmptyState>
      )}
      {estado.tipo === 'error' && (
        <EmptyState icono="fa-triangle-exclamation"><p>No se pudo cargar el historial.</p></EmptyState>
      )}
      {estado.tipo === 'ok' && estado.historial.length === 0 && (
        <EmptyState icono="fa-clock-rotate-left"><p>Aún no hay consultas registradas.</p></EmptyState>
      )}
      {estado.tipo === 'ok' && estado.historial.length > 0 && (
        <div className="card">
          <table className="proc-table">
            <thead><tr><th>Fecha</th><th>Folio</th><th>Usuario</th><th>Cédula</th><th>Titular</th><th>Propósito</th><th>Riesgo</th><th>Resultado</th></tr></thead>
            <tbody>
              {estado.historial.map((e, i) => (
                <tr key={`${e.folio || e.fecha}-${i}`} style={{ cursor: 'pointer' }} onClick={() => onReconsultar(e.cedula)}>
                  <td>{e.fecha}</td>
                  <td style={{ fontSize: '.8em' }}>{e.folio || '—'}</td>
                  <td>{e.usuario}</td>
                  <td>{e.cedula}</td>
                  <td>{e.titular || '—'}</td>
                  <td style={{ fontSize: '.82em' }}>{e.proposito || '—'}</td>
                  <td style={{ textAlign: 'center', color: COLOR_SCORE(e.score), fontWeight: 700 }}>{e.score ?? 0}</td>
                  <td><RiskPill semaforo={e.semaforo} /></td>
                </tr>
              ))}
            </tbody>
          </table>
          <p style={{ fontSize: '.78rem', color: 'var(--text-muted)', marginTop: 10 }}>Haz clic en una fila para volver a verificar esa cédula.</p>
        </div>
      )}
    </>
  )
}

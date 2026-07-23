// Busqueda de procesos judiciales por nombre (Funcion Judicial).
import { useState } from 'react'
import { postJSON } from '@/services/api'
import { useToast } from '@/hooks/useToast/useToast.js'
import Loading from '@/components/Loading/Loading.jsx'
import EmptyState from '@/components/EmptyState/EmptyState.jsx'
import ProcesoRow from './components/ProcesoRow/ProcesoRow.jsx'

// El nombre solo admite letras y espacios (sin numeros ni simbolos).
function sanitizarNombre(raw) {
  return raw.replace(/[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ .'-]/g, '').toUpperCase()
}

export default function PorNombre() {
  const showToast = useToast()
  const [nombre, setNombre] = useState('')
  const [error, setError] = useState('')
  const [cargando, setCargando] = useState(false)
  const [data, setData] = useState(null)

  function onChange(raw) {
    setNombre(sanitizarNombre(raw))
    if (error) setError('')
  }

  async function buscar() {
    const valor = nombre.trim()
    if (valor.length < 5) { setError('Ingresa al menos un apellido y un nombre (mínimo 5 letras).'); return }
    setCargando(true)
    setData(null)
    try {
      const { ok, data: d } = await postJSON('/api/buscar-nombre', { nombre: valor })
      if (!ok) { showToast(d.error || 'Error en la consulta'); return }
      setData(d)
    } catch (e) {
      showToast('Error de conexión')
    } finally {
      setCargando(false)
    }
  }

  return (
    <>
      <div className="card">
        <div className="search-box">
          <div className="form-group">
            <label htmlFor="nombre"><i className="fas fa-user-tag" aria-hidden="true"></i> Nombres y Apellidos</label>
            <input id="nombre" type="text" value={nombre} placeholder="Ej: PÉREZ GARCÍA JUAN CARLOS"
                   autoComplete="off" spellCheck="false"
                   aria-invalid={error ? 'true' : 'false'}
                   className={error ? 'invalid' : ''}
                   style={{ letterSpacing: 'normal' }}
                   onChange={e => onChange(e.target.value)}
                   onKeyDown={e => { if (e.key === 'Enter') buscar() }} />
            {error
              ? <div className="field-error" role="alert"><i className="fas fa-circle-exclamation" aria-hidden="true"></i> {error}</div>
              : <div className="field-hint"><i className="fas fa-user-tag" aria-hidden="true"></i> Solo letras (sin números). Escribe primero los apellidos.</div>}
          </div>
          <button className="btn btn-primary" disabled={cargando} onClick={buscar}>
            <i className="fas fa-magnifying-glass" aria-hidden="true"></i> Buscar Procesos
          </button>
        </div>
        <div className="info-banner" style={{ marginTop: '1rem', marginBottom: 0 }}>
          <i className="fas fa-circle-info" aria-hidden="true"></i>
          <span>La búsqueda por nombre consulta solo <strong>procesos judiciales</strong> (Función Judicial).
          Las fuentes públicas no exponen la cédula de las partes, por lo que no es posible distinguir entre
          personas con el mismo nombre. Para el informe completo de antecedentes, usa la pestaña <strong>Por Cédula</strong>.</span>
        </div>
      </div>

      {cargando && <Loading texto="Buscando procesos judiciales..." />}

      {!cargando && !data && (
        <EmptyState icono="fa-folder-open">
          <p>Ingresa un nombre para buscar procesos judiciales asociados</p>
        </EmptyState>
      )}

      {!cargando && data && data.total === 0 && (
        <EmptyState icono="fa-folder-open">
          <p>Sin procesos judiciales para "<strong>{data.nombre}</strong>"</p>
        </EmptyState>
      )}

      {!cargando && data && data.total > 0 && (
        <>
          <div className="semaforo atencion" style={{ marginBottom: '1.25rem' }}>
            <div className="semaforo-icon"><i className="fas fa-folder-open" aria-hidden="true"></i></div>
            <div className="semaforo-text">
              <h2>{data.total} proceso(s) encontrado(s)</h2>
              <p>Coincidencias con el nombre "{data.nombre}". Haz clic en un proceso para ver las partes.</p>
            </div>
          </div>
          <div className="card">
            <table className="proc-table">
              <thead><tr><th>N° Proceso</th><th>Tipo / Delito</th><th>Provincia</th><th>Año</th><th>Rol</th><th>Estado</th></tr></thead>
              <tbody>
                {data.procesos.map((p, i) => <ProcesoRow key={`${p.numero}-${i}`} p={p} />)}
              </tbody>
            </table>
          </div>
        </>
      )}
    </>
  )
}

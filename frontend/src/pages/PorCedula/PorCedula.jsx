// Pagina principal: verificacion completa por cedula (o nombre -> cedula via SRI).
import { useEffect, useRef, useState } from 'react'
import { postJSON } from '@/services/api'
import { useToast } from '@/hooks/useToast/useToast.js'
import Loading from '@/components/Loading/Loading.jsx'
import EmptyState from '@/components/EmptyState/EmptyState.jsx'
import Informe from './components/Informe/Informe.jsx'

const PROPOSITOS = [
  'Proceso de selección laboral',
  'Diligencia debida de cliente/proveedor',
  'Verificación de contraparte contractual',
  'Control interno / cumplimiento',
  'Solicitud del propio titular',
  'Otro (fin legítimo declarado)',
]

// Cedulas de ejemplo (validas segun el algoritmo modulo 10) para probar el flujo.
const EJEMPLOS = [
  { ced: '0959083015', tag: 'Guayas' },
  { ced: '1809139098', tag: 'Tungurahua' },
]

// Modo detectado a partir de lo que escribe el usuario.
function detectarModo(raw) {
  const s = raw.trim()
  if (!s) return 'vacio'
  return /\d/.test(s[0]) ? 'cedula' : 'nombre'
}

// Sanitiza la entrada segun el modo: la cedula solo admite digitos (max 10);
// el nombre solo admite letras y espacios (sin numeros).
function sanitizar(raw) {
  const modo = detectarModo(raw)
  if (modo === 'cedula') return { modo, valor: raw.replace(/\D/g, '').slice(0, 10) }
  if (modo === 'nombre') return { modo, valor: raw.replace(/[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ .'-]/g, '').toUpperCase() }
  return { modo, valor: '' }
}

export default function PorCedula({ reconsulta }) {
  const showToast = useToast()
  const [entrada, setEntrada] = useState('')
  const [modo, setModo] = useState('vacio')
  const [error, setError] = useState('')
  const [proposito, setProposito] = useState(PROPOSITOS[0])
  const [cargando, setCargando] = useState(false)
  // vista: {tipo:'vacio'} | {tipo:'informe',data} | {tipo:'selector',lista} | {tipo:'sin-persona'}
  const [vista, setVista] = useState({ tipo: 'vacio' })
  const propositoRef = useRef(proposito)
  propositoRef.current = proposito

  // Click en una fila del historial -> re-verificar esa cedula
  useEffect(() => {
    if (reconsulta && reconsulta.cedula) {
      setEntrada(reconsulta.cedula)
      setModo('cedula')
      ejecutarVerificacion(reconsulta.cedula)
    }
  }, [reconsulta])

  function onChange(raw) {
    const { modo: m, valor } = sanitizar(raw)
    setEntrada(valor)
    setModo(m)
    if (error) setError('')
  }

  function usarEjemplo(ced) {
    setEntrada(ced)
    setModo('cedula')
    setError('')
    ejecutarVerificacion(ced)
  }

  function verificar() {
    const valor = entrada.trim()
    if (!valor) { setError('Ingresa una cédula (10 dígitos) o los apellidos y nombres completos.'); return }
    if (modo === 'cedula') {
      if (valor.length !== 10) { setError('La cédula debe tener exactamente 10 dígitos.'); return }
      ejecutarVerificacion(valor)
    } else {
      if (valor.length < 5) { setError('Ingresa apellidos y nombres completos (mínimo 5 caracteres).'); return }
      buscarCedulaPorNombre(valor)
    }
  }

  async function ejecutarVerificacion(cedula) {
    setCargando(true)
    setVista({ tipo: 'vacio' })
    try {
      const { ok, data } = await postJSON('/api/verificar', { cedula, proposito: propositoRef.current })
      if (!ok) { showToast(data.error || 'Error en la consulta'); return }
      setVista({ tipo: 'informe', data })
    } catch (e) {
      showToast('Error de conexión')
    } finally {
      setCargando(false)
    }
  }

  async function buscarCedulaPorNombre(nombre) {
    setCargando(true)
    setVista({ tipo: 'vacio' })
    try {
      const { ok, data } = await postJSON('/api/cedula-por-nombre', { nombre })
      if (!ok) { showToast(data.error || 'Error en la consulta'); return }
      if (!data.total) { setVista({ tipo: 'sin-persona' }); return }
      // 1 coincidencia -> verificar directo. Varias -> mostrar selector.
      if (data.total === 1) {
        setEntrada(data.coincidencias[0].identificacion)
        setModo('cedula')
        ejecutarVerificacion(data.coincidencias[0].identificacion)
      } else {
        setVista({ tipo: 'selector', lista: data.coincidencias })
      }
    } catch (e) {
      showToast('Error de conexión')
    } finally {
      setCargando(false)
    }
  }

  function seleccionarPersona(cedula) {
    setEntrada(cedula)
    setModo('cedula')
    ejecutarVerificacion(cedula)
  }

  return (
    <>
      <div className="card">
        <div className="search-box">
          <div className="form-group">
            <label htmlFor="entrada"><i className="fas fa-id-card" aria-hidden="true"></i> Cédula o Apellidos y Nombres completos</label>
            <input id="entrada" type="text" value={entrada}
                   inputMode={modo === 'nombre' ? 'text' : 'numeric'}
                   autoComplete="off" spellCheck="false"
                   aria-invalid={error ? 'true' : 'false'}
                   className={error ? 'invalid' : ''}
                   placeholder="Ej: 0959083015  o  PÉREZ GARCÍA JUAN CARLOS"
                   onChange={e => onChange(e.target.value)}
                   onKeyDown={e => { if (e.key === 'Enter') verificar() }} />
            {error
              ? <div className="field-error" role="alert"><i className="fas fa-circle-exclamation" aria-hidden="true"></i> {error}</div>
              : modo === 'cedula'
                ? <div className="field-hint"><i className="fas fa-hashtag" aria-hidden="true"></i> Modo cédula · solo números ({entrada.length}/10)</div>
                : modo === 'nombre'
                  ? <div className="field-hint"><i className="fas fa-user-tag" aria-hidden="true"></i> Modo nombre · solo letras (sin números)</div>
                  : <div className="field-hint"><i className="fas fa-keyboard" aria-hidden="true"></i> Escribe una cédula de 10 dígitos o un nombre completo</div>}
          </div>
          <div className="form-group">
            <label htmlFor="proposito"><i className="fas fa-clipboard-check" aria-hidden="true"></i> Propósito de la consulta (LOPDP)</label>
            <select id="proposito" value={proposito} onChange={e => setProposito(e.target.value)}>
              {PROPOSITOS.map(p => <option key={p} value={p}>{p}</option>)}
            </select>
          </div>
          <div className="search-action">
            <span className="label-spacer" aria-hidden="true">&nbsp;</span>
            <button className="btn btn-primary" disabled={cargando} onClick={verificar}>
              <i className="fas fa-magnifying-glass" aria-hidden="true"></i> Verificar Antecedentes
            </button>
          </div>
        </div>
        <p className="hint-text">
          <i className="fas fa-circle-info" aria-hidden="true"></i>{' '}
          Ingresa la <strong>cédula</strong> (10 dígitos) o los <strong>apellidos y nombres completos</strong>; en ese caso se busca la cédula en el SRI y se selecciona la persona.
        </p>

        <div className="ej-chips" style={{ marginTop: 12 }}>
          <span className="field-hint" style={{ marginTop: 0, marginRight: 4 }}>Ejemplos:</span>
          {EJEMPLOS.map(e => (
            <button className="ej-chip" key={e.ced} onClick={() => usarEjemplo(e.ced)}
                    aria-label={`Verificar cédula de ejemplo ${e.ced}`}>
              <i className="fas fa-id-card" aria-hidden="true"></i>
              {e.ced}<span className="tag">{e.tag}</span>
            </button>
          ))}
        </div>
      </div>

      {cargando && <Loading texto="Consultando fuentes oficiales..." />}

      {!cargando && vista.tipo === 'vacio' && (
        <EmptyState icono="fa-user-shield">
          <p>Ingresa una cédula para generar el informe de antecedentes</p>
        </EmptyState>
      )}

      {!cargando && vista.tipo === 'sin-persona' && (
        <EmptyState icono="fa-user-slash">
          <p>No se encontró ninguna persona con ese nombre en el SRI.</p>
          <p style={{ fontSize: '.8rem', color: 'var(--text-muted)' }}>Revisa el orden: apellidos y luego nombres.</p>
        </EmptyState>
      )}

      {!cargando && vista.tipo === 'selector' && (
        <div className="card">
          <div className="info-banner">
            <i className="fas fa-users" aria-hidden="true"></i>
            <span>Se encontraron <strong>{vista.lista.length}</strong> coincidencias en el SRI. Selecciona la persona a verificar.</span>
          </div>
          <table className="proc-table" style={{ marginTop: '1rem' }}>
            <thead><tr><th>Cédula</th><th>Nombre completo</th><th>Estado</th><th></th></tr></thead>
            <tbody>
              {vista.lista.map(p => (
                <tr key={p.identificacion} style={{ cursor: 'pointer' }} onClick={() => seleccionarPersona(p.identificacion)}>
                  <td>{p.identificacion}</td>
                  <td>{p.nombreCompleto}</td>
                  <td>{p.fallecido ? <span style={{ color: 'var(--danger)' }}>Fallecido</span> : 'Activo'}</td>
                  <td><i className="fas fa-magnifying-glass" aria-hidden="true"></i> Verificar</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {!cargando && vista.tipo === 'informe' && <Informe data={vista.data} />}
    </>
  )
}

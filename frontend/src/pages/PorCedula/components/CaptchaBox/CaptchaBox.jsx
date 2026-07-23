// Relay de captcha (Bachiller MinEduc / SENESCYT): pide la imagen al backend,
// el usuario la resuelve y se reenvia la consulta JSF.
import { useEffect, useRef, useState } from 'react'
import { postJSON } from '@/services/api'

export default function CaptchaBox({ clave, cedula, ronda }) {
  const [fase, setFase] = useState('cargando')   // cargando | listo | error-inicio
  const [token, setToken] = useState(null)
  const [imagen, setImagen] = useState(null)
  const [captcha, setCaptcha] = useState('')
  const [errorInicio, setErrorInicio] = useState('')
  // resultado: {tipo:'error'|'aviso'|'titulos', ...}
  const [resultado, setResultado] = useState(null)
  const [consultando, setConsultando] = useState(false)
  const inputRef = useRef(null)

  useEffect(() => { iniciar() }, [ronda])   // el boton "Consultar titulo" y el refresh suben `ronda`

  async function iniciar() {
    setFase('cargando')
    setResultado(null)
    setCaptcha('')
    try {
      const { ok, data } = await postJSON('/api/captcha/iniciar', { fuente: clave })
      if (!ok) {
        setErrorInicio(data.error || 'No se pudo iniciar la consulta.')
        setFase('error-inicio')
        return
      }
      setToken(data.token)
      setImagen(data.imagen)
      setFase('listo')
      setTimeout(() => inputRef.current && inputRef.current.focus(), 0)
    } catch (e) {
      setErrorInicio('Error de red al cargar el captcha.')
      setFase('error-inicio')
    }
  }

  async function enviar() {
    const texto = captcha.trim()
    if (!texto) { setResultado({ tipo: 'error', color: 'var(--warning)', mensaje: 'Escribe el texto del captcha.' }); return }
    setConsultando(true)
    setResultado({ tipo: 'aviso', mensaje: 'Consultando…' })
    try {
      const { ok, data } = await postJSON('/api/captcha/consultar', { token, captcha: texto, cedula: cedula || '' })
      if (data.error === 'captcha') {
        setResultado({ tipo: 'error', color: 'var(--danger)', mensaje: data.mensaje })
        iniciar()  // refresca con un captcha nuevo
        return
      }
      if (!ok || (data.error && !data.ok)) {
        setResultado({ tipo: 'error', color: 'var(--danger)', mensaje: data.mensaje || data.error || 'No se pudo consultar.' })
        return
      }
      if (data.sin_resultados) {
        setResultado({ tipo: 'aviso', mensaje: data.mensaje })
        return
      }
      setResultado({ tipo: 'titulos', data })
    } catch (e) {
      setResultado({ tipo: 'error', color: 'var(--danger)', mensaje: 'Error de red al consultar.' })
    } finally {
      setConsultando(false)
    }
  }

  return (
    <div className="captcha-box">
      {fase === 'cargando' && (
        <span style={{ color: 'var(--text-muted)' }}><i className="fas fa-spinner fa-spin"></i> Cargando captcha…</span>
      )}
      {fase === 'error-inicio' && (
        <span style={{ color: 'var(--danger)' }}>{errorInicio}</span>
      )}
      {fase === 'listo' && (
        <>
          <div className="cap-row">
            <img src={imagen} className="cap-img" alt="captcha" />
            <button type="button" className="cap-refresh" title="Otra imagen" onClick={iniciar}>
              <i className="fas fa-rotate"></i>
            </button>
            <input ref={inputRef} className="cap-input" placeholder="Escribe el captcha"
                   autoComplete="off" maxLength={10} value={captcha}
                   onChange={e => setCaptcha(e.target.value)}
                   onKeyDown={e => { if (e.key === 'Enter') enviar() }} />
            <button type="button" className="cap-go" disabled={consultando} onClick={enviar}>
              <i className="fas fa-magnifying-glass"></i> Consultar
            </button>
          </div>
          <div className="cap-result">
            {resultado && resultado.tipo === 'error' && <span style={{ color: resultado.color }}>{resultado.mensaje}</span>}
            {resultado && resultado.tipo === 'aviso' && <span style={{ color: 'var(--text-muted)' }}>{resultado.mensaje}</span>}
            {resultado && resultado.tipo === 'titulos' && <Titulos d={resultado.data} />}
          </div>
        </>
      )}
    </div>
  )
}

function Titulos({ d }) {
  const titulos = d.titulos || []
  return (
    <>
      {(d.nombres || d.identificacion) && (
        <div className="cap-pers">
          <i className="fas fa-id-card"></i> <strong>{d.nombres || ''}</strong>
          {d.identificacion && <span className="cap-ced">{d.identificacion}</span>}
        </div>
      )}
      {titulos.length === 0 && <span style={{ color: 'var(--text-muted)' }}>Sin títulos registrados.</span>}
      {titulos.length > 0 && (
        <div className="cap-count"><i className="fas fa-circle-check"></i> {titulos.length} título(s) registrado(s)</div>
      )}
      {titulos.map((t, i) => <TituloCard key={i} t={t} />)}
    </>
  )
}

function TituloCard({ t }) {
  // Las columnas vienen tal cual del portal oficial; se detectan por nombre.
  const cols = Object.keys(t)
  const find = re => cols.find(c => re.test(c))
  const cTit = find(/t[íi]tulo|nivel|grado\s*acad/i)
  const cEsp = find(/especialidad|carrera|menci/i)
  const titulo = (cTit && t[cTit]) ? t[cTit] : 'Título'
  const esp = (cEsp && t[cEsp]) ? t[cEsp] : ''

  const campos = cols.filter(c => {
    const v = (t[c] || '').trim()
    if (!v) return false
    if (/^n[ºo°]\.?$/i.test(c.trim())) return false          // columna "Nº"
    if (c === cTit || c === cEsp) return false               // ya en el encabezado
    if (/certificad/i.test(c) && /imprimir|ver|descargar/i.test(v)) return false
    return true
  })

  return (
    <div className="cap-card">
      <div className="cap-card-h">
        <i className="fas fa-graduation-cap"></i> <span>{titulo}</span>
        {esp && <span className="cap-esp">{esp}</span>}
      </div>
      <div className="cap-fields">
        {campos.map(c => (
          <div className="cap-f" key={c}>
            <span className="cap-k">{c}</span>
            <span className="cap-v">{(t[c] || '').trim()}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

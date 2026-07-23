import { useEffect, useState } from 'react'
import { ROL, USUARIO, puede } from '@/utils/sesion'
import { ToastProvider } from '@/contexts/ToastContext/ToastContext.jsx'
import { rutasPermitidas } from '@/routes/routes.jsx'

// Logo Verum: sello de verificacion (anillo dorado dentado + check azul-teal).
function LogoVerum() {
  return (
    <div className="logo-mark">
      <svg viewBox="0 0 40 40" role="img" aria-label="Verum">
        <defs>
          <linearGradient id="verum-g" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stopColor="#7dd3fc" />
            <stop offset="1" stopColor="#14b8a6" />
          </linearGradient>
        </defs>
        <circle cx="20" cy="20" r="18" fill="none" stroke="#d9b45b" strokeWidth="1.5"
                strokeDasharray="1.5 2.6" opacity="0.75" />
        <circle cx="20" cy="20" r="14" fill="none" stroke="url(#verum-g)" strokeWidth="2" />
        <path d="M13 20.5l4.6 4.6 9-10" fill="none" stroke="url(#verum-g)"
              strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    </div>
  )
}

export default function App() {
  const [tab, setTab] = useState('cedula')
  const [light, setLight] = useState(() => localStorage.getItem('verum-theme') === 'light')
  // Cedula pendiente de re-verificar (click en una fila del historial)
  const [reconsulta, setReconsulta] = useState(null)
  const rutas = rutasPermitidas(puede)

  useEffect(() => {
    document.body.classList.toggle('light-mode', light)
    localStorage.setItem('verum-theme', light ? 'light' : 'dark')
  }, [light])

  async function logout() {
    await fetch('/api/logout', { method: 'POST' })
    window.location.href = '/'
  }

  function reconsultar(cedula) {
    setTab('cedula')
    setReconsulta({ cedula, n: Date.now() })
  }

  return (
    <ToastProvider>
      <div className="container">
        <header>
          <div className="header-actions">
            <div className="header-user">
              <i className="fas fa-user-circle" aria-hidden="true"></i><span>{USUARIO}</span>
              <span style={{ opacity: .6, fontSize: '.8em', marginLeft: 6, textTransform: 'capitalize' }}>({ROL})</span>
            </div>
            <button className="btn-icon" title="Cambiar tema" aria-label="Cambiar tema claro u oscuro"
                    onClick={() => setLight(l => !l)}>
              <i className={`fas ${light ? 'fa-moon' : 'fa-sun'}`} aria-hidden="true"></i>
            </button>
            <button className="btn-icon btn-logout" title="Cerrar sesión" aria-label="Cerrar sesión" onClick={logout}>
              <i className="fas fa-right-from-bracket" aria-hidden="true"></i>
            </button>
          </div>
          <div className="logo"><LogoVerum /></div>
          <h1>Verum<span className="tld"> EC</span></h1>
          <p className="tagline">Verificación y debida diligencia de personas · Ecuador</p>
        </header>

        <nav className="tabs" aria-label="Secciones">
          {rutas.map(r => (
            <button key={r.id} className={`tab ${tab === r.id ? 'active' : ''}`}
                    aria-current={tab === r.id ? 'page' : undefined} onClick={() => setTab(r.id)}>
              <i className={`fas ${r.icono}`} aria-hidden="true"></i> {r.texto}
            </button>
          ))}
        </nav>

        {/* Todas las secciones se mantienen montadas (ocultas con CSS) para
            conservar sus resultados al cambiar de pestaña. */}
        {rutas.map(r => (
          <div key={r.id} className={`tab-content ${tab === r.id ? 'active' : ''}`}>
            <r.Componente activa={tab === r.id} reconsulta={reconsulta} onReconsultar={reconsultar} />
          </div>
        ))}

        <div className="disclaimer">
          <i className="fas fa-triangle-exclamation" aria-hidden="true"></i>{' '}
          Herramienta académica. La información proviene de fuentes públicas y puede no estar actualizada.
          Las fuentes marcadas como <strong>informativas</strong> no exponen API y deben verificarse en el portal oficial.
        </div>
      </div>
    </ToastProvider>
  )
}

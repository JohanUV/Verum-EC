// Tarjeta de una fuente del informe, con acciones de captcha o SIIRS si aplica.
import { useState } from 'react'
import { ICON_STATUS } from '@/utils/formato'
import CaptchaBox from '../CaptchaBox/CaptchaBox.jsx'
import SiirsBox from '../SiirsBox/SiirsBox.jsx'

export default function ResultCard({ m, indice, cedula }) {
  const [capVisible, setCapVisible] = useState(false)
  const [capRonda, setCapRonda] = useState(0)   // fuerza recarga del captcha
  const [siirsVisible, setSiirsVisible] = useState(false)

  const badgeTxt = m.tipo === 'real' ? 'API en vivo' : (m.tipo === 'captcha' ? 'Captcha' : 'Informativo')
  const esCaptcha = (m.clave === 'bachiller' || m.clave === 'senescyt')
  const esRegSoc = (m.clave === 'registro_social')
  const visibles = (m.datos || []).slice(0, 5)

  return (
    <div className={`result-card ${m.nivel}`} style={{ animationDelay: `${indice * 0.05}s` }}>
      <div className="rc-head">
        <div className="rc-icon"><i className={`fas ${m.icono}`}></i></div>
        <div>
          <div className="rc-title">{m.fuente}</div>
          <span className={`rc-badge ${m.tipo}`}>{badgeTxt}</span>
        </div>
        <i className={`fas ${ICON_STATUS[m.nivel]} rc-status ${m.nivel}`}></i>
      </div>
      <div className="rc-resumen">{m.resumen}</div>

      {visibles.length > 0 && (
        <div className="rc-data">
          {visibles.map((d, j) => 'campo' in d ? (
            <div className="rc-row" key={j}>
              <span className="k">{d.campo}</span>
              <span className="v">{d.valor}</span>
            </div>
          ) : (
            <div className="rc-row" key={j}>
              <span className="k">
                {d.tipo || 'Registro'}
                {[d.rol, d.provincia, d.estado].filter(Boolean).length > 0 &&
                  <small style={{ opacity: .6 }}> ({[d.rol, d.provincia, d.estado].filter(Boolean).join(' · ')})</small>}
              </span>
              <span className="v">{d.fecha || ''}</span>
            </div>
          ))}
        </div>
      )}
      {(m.datos || []).length > 5 && (
        <div className="rc-more">+ {m.datos.length - 5} registro(s) mas...</div>
      )}

      {m.enlace && (
        <a className="rc-link" href={m.enlace} target="_blank" rel="noreferrer">
          <i className="fas fa-up-right-from-square"></i> Portal oficial
        </a>
      )}
      {esCaptcha && (
        <button className="rc-cta" onClick={() => { setCapVisible(true); setCapRonda(n => n + 1) }}>
          <i className="fas fa-unlock-keyhole"></i> Consultar titulo (captcha)
        </button>
      )}
      {esRegSoc && (
        <button className="rc-cta" onClick={() => setSiirsVisible(true)}>
          <i className="fas fa-up-right-from-square"></i> Abrir SIIRS (copia la cedula)
        </button>
      )}

      {esCaptcha && capVisible && <CaptchaBox clave={m.clave} cedula={cedula} ronda={capRonda} />}
      {esRegSoc && siirsVisible && <SiirsBox cedula={cedula} />}
    </div>
  )
}

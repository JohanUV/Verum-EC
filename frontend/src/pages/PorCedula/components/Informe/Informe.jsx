// Informe consolidado: semaforo, metricas y resultados agrupados por categoria.
import { COLOR_SCORE, ICON_SEMAFORO, TXT_SEMAFORO, agruparPorCategoria } from '@/utils/formato'
import { puede } from '@/utils/sesion'
import { exportarPDF } from '@/services/pdf'
import { useToast } from '@/hooks/useToast/useToast.js'
import ResultCard from '../ResultCard/ResultCard.jsx'

export default function Informe({ data }) {
  const showToast = useToast()
  const r = data.resumen
  const grupos = agruparPorCategoria(data.resultados)

  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <span style={{ fontSize: '.8rem', color: 'var(--text-muted)' }}>
          {data.folio && <><i className="fas fa-hashtag" aria-hidden="true"></i> Folio {data.folio}</>}
          {data.demo && <span className="demo-badge"><i className="fas fa-flask" aria-hidden="true"></i> Datos de demostración</span>}
        </span>
        {puede('exportar') && (
          <button className="btn" onClick={() => exportarPDF(data, showToast)}
                  style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', color: 'var(--text-primary)', height: 'auto', padding: '10px 20px' }}>
            <i className="fas fa-file-pdf" style={{ color: 'var(--danger)' }} aria-hidden="true"></i> Exportar PDF
          </button>
        )}
      </div>

      <div className={`semaforo ${data.semaforo}`}>
        <div className="semaforo-icon"><i className={`fas ${ICON_SEMAFORO[data.semaforo]}`} aria-hidden="true"></i></div>
        <div className="semaforo-text">
          <h2>
            {TXT_SEMAFORO[data.semaforo]}
            {data.titular && <> · <span style={{ color: 'var(--accent-light)' }}>{data.titular}</span></>}
          </h2>
          <p>{data.mensaje} · Cédula {data.cedula}</p>
        </div>
        <div className="semaforo-meta">
          <div><div className="num" style={{ color: COLOR_SCORE(data.score) }}>{data.score ?? 0}</div><div className="lbl">Riesgo /100</div></div>
          <div><div className="num">{r.fuentes_consultadas}</div><div className="lbl">Fuentes</div></div>
          <div><div className="num">{r.con_hallazgos}</div><div className="lbl">Con datos</div></div>
          <div><div className="num">{r.alertas}</div><div className="lbl">Alertas</div></div>
        </div>
      </div>

      {/* Resultados agrupados por categoria (Judicial, Tributario, etc.) */}
      {grupos.map(cat => {
        const alertas = cat.items.filter(m => m.nivel === 'alerta').length
        return (
          <section className="cat-section" key={cat.id} aria-label={cat.titulo}>
            <div className="cat-head">
              <div className="cat-icon"><i className={`fas ${cat.icono}`} aria-hidden="true"></i></div>
              <div>
                <div className="cat-title">{cat.titulo}</div>
                <div className="cat-sub">{cat.sub}</div>
              </div>
              <span className={`cat-count ${alertas ? 'has-alert' : ''}`}>
                {alertas ? `${alertas} alerta(s)` : `${cat.items.length} fuente(s)`}
              </span>
            </div>
            <div className="results-grid">
              {cat.items.map((m, i) => (
                <ResultCard key={m.fuente} m={m} indice={i} cedula={data.cedula} />
              ))}
            </div>
          </section>
        )
      })}
    </>
  )
}

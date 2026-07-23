// Servicio de exportacion del informe a PDF (html2pdf via CDN en index.html).
import { esc } from '@/utils/formato'
import { USUARIO } from '@/utils/sesion'

// Paleta para el informe impreso (tema claro, apto para tinta)
const PDF_COLORS = {
  limpio:   { c: '#15803d', bg: '#f0fdf4', txt: 'SIN ANTECEDENTES RELEVANTES' },
  atencion: { c: '#b45309', bg: '#fffbeb', txt: 'REQUIERE ATENCION' },
  alerta:   { c: '#b91c1c', bg: '#fef2f2', txt: 'ALERTA - HALLAZGOS RELEVANTES' },
}

function construirInformePDF(data) {
  const sem = PDF_COLORS[data.semaforo] || PDF_COLORS.limpio
  const r = data.resumen || {}
  const fecha = new Date().toLocaleString('es-EC', { dateStyle: 'long', timeStyle: 'short' })

  const tarjetas = (data.resultados || []).map(m => {
    const col = (PDF_COLORS[m.nivel] || PDF_COLORS.limpio).c
    const tipo = m.tipo === 'real' ? 'API en vivo' : 'Informativo'
    let filas = ''
    if (m.datos && m.datos.length) {
      filas = '<table style="width:100%;border-collapse:collapse;margin-top:6px;font-size:10px">' +
        m.datos.map(d => {
          let k, v
          if ('campo' in d) { k = d.campo; v = d.valor }
          else {
            const ex = [d.rol, d.provincia, d.estado].filter(Boolean).join(' · ')
            k = (d.tipo || 'Registro') + (ex ? ' (' + ex + ')' : ''); v = d.fecha || ''
          }
          return `<tr>
              <td style="padding:4px 8px;border:1px solid #e5e7eb;background:#f9fafb;width:48%;vertical-align:top;color:#374151">${esc(k)}</td>
              <td style="padding:4px 8px;border:1px solid #e5e7eb;color:#111827">${esc(v)}</td></tr>`
        }).join('') + '</table>'
    }
    const link = m.enlace ? `<div style="font-size:9px;color:#6b7280;margin-top:5px;word-break:break-all">Portal oficial: ${esc(m.enlace)}</div>` : ''
    return `
      <div style="page-break-inside:avoid;border:1px solid #e5e7eb;border-left:4px solid ${col};border-radius:6px;padding:10px 12px;margin-bottom:10px;background:#fff">
          <div style="display:flex;justify-content:space-between;align-items:center">
              <span style="font-size:13px;font-weight:700;color:#111827">${esc(m.fuente)}</span>
              <span style="font-size:9px;font-weight:700;color:#fff;background:${m.tipo === 'real' ? '#0e7490' : '#6b7280'};padding:2px 8px;border-radius:10px">${tipo}</span>
          </div>
          <div style="font-size:11px;color:${col};font-weight:600;margin-top:4px">${esc(m.resumen)}</div>
          ${filas}${link}
      </div>`
  }).join('')

  // Marca de agua: lineas diagonales repetidas, tenues, sobre el contenido
  let marca = ''
  for (let y = -10; y < 150; y += 26) {
    marca += `<div style="position:absolute;top:${y}mm;left:-20mm;width:240mm;text-align:center;
        transform:rotate(-30deg);font-size:34px;font-weight:800;color:#000;opacity:0.05;
        letter-spacing:8px;white-space:nowrap">VERUM · CONFIDENCIAL · ${esc(data.folio || '')}</div>`
  }

  return `
  <div style="position:relative;font-family:Arial,Helvetica,sans-serif;color:#111827;padding:0;background:#fff;width:190mm">
      <div style="position:absolute;inset:0;overflow:hidden;pointer-events:none;z-index:0">${marca}</div>
      <div style="position:relative;z-index:1">
      <div style="background:#0e0e1a;color:#fff;padding:16px 20px;border-radius:6px;display:flex;justify-content:space-between;align-items:center">
          <div>
              <div style="font-size:22px;font-weight:800;letter-spacing:1px">VERUM<span style="color:#7dd3fc"> EC</span></div>
              <div style="font-size:11px;color:#cbd5e1">Informe de Verificación de Antecedentes</div>
          </div>
          <div style="text-align:right;font-size:10px;color:#cbd5e1">
              <div style="font-weight:700;color:#fff">Folio: ${esc(data.folio || 'N/D')}</div>
              <div>Generado: ${esc(fecha)}</div>
              <div>Fuentes consultadas: ${esc(r.fuentes_consultadas || 0)}</div>
          </div>
      </div>

      <table style="width:100%;border-collapse:collapse;margin-top:14px;font-size:11px">
          <tr>
              <td style="padding:6px 10px;border:1px solid #e5e7eb;background:#f9fafb;font-weight:700;width:25%">Cedula</td>
              <td style="padding:6px 10px;border:1px solid #e5e7eb">${esc(data.cedula || '')}</td>
          </tr>
          <tr>
              <td style="padding:6px 10px;border:1px solid #e5e7eb;background:#f9fafb;font-weight:700">Titular</td>
              <td style="padding:6px 10px;border:1px solid #e5e7eb">${esc(data.titular || 'No determinado')}</td>
          </tr>
          <tr>
              <td style="padding:6px 10px;border:1px solid #e5e7eb;background:#f9fafb;font-weight:700">Propósito (LOPDP)</td>
              <td style="padding:6px 10px;border:1px solid #e5e7eb">${esc(data.proposito || 'No especificado')}</td>
          </tr>
          <tr>
              <td style="padding:6px 10px;border:1px solid #e5e7eb;background:#f9fafb;font-weight:700">Emitido por</td>
              <td style="padding:6px 10px;border:1px solid #e5e7eb">${esc(data.usuario || USUARIO || '—')}</td>
          </tr>
      </table>

      <div style="margin-top:14px;padding:14px 18px;border-radius:6px;background:${sem.bg};border:1px solid ${sem.c}">
          <div style="display:flex;justify-content:space-between;align-items:center">
              <div style="font-size:16px;font-weight:800;color:${sem.c}">${sem.txt}</div>
              <div style="text-align:center"><div style="font-size:22px;font-weight:800;color:${sem.c}">${esc(data.score ?? 0)}<span style="font-size:11px;color:#6b7280">/100</span></div><div style="font-size:9px;color:#6b7280">${esc(data.etiqueta_riesgo || 'Riesgo')}</div></div>
          </div>
          <div style="font-size:11px;color:#374151;margin-top:3px">${esc(data.mensaje || '')}</div>
          <div style="margin-top:8px;font-size:11px;color:#374151">
              <strong>${esc(r.fuentes_consultadas || 0)}</strong> fuentes &nbsp;·&nbsp;
              <strong>${esc(r.con_hallazgos || 0)}</strong> con datos &nbsp;·&nbsp;
              <strong style="color:${PDF_COLORS.alerta.c}">${esc(r.alertas || 0)}</strong> alertas
          </div>
      </div>

      <div style="margin-top:16px;font-size:13px;font-weight:700;color:#111827;border-bottom:2px solid #0e0e1a;padding-bottom:4px">
          Detalle por fuente
      </div>
      <div style="margin-top:10px">${tarjetas}</div>

      <div style="margin-top:18px;padding-top:10px;border-top:1px solid #e5e7eb;font-size:9px;color:#6b7280">
          Folio ${esc(data.folio || 'N/D')} &middot; Emitido por ${esc(data.usuario || USUARIO || '—')} &middot; Propósito declarado: ${esc(data.proposito || 'No especificado')}.<br>
          Documento generado automáticamente por Verum a partir de fuentes públicas del Ecuador.
          Las fuentes marcadas como "Informativo" no exponen API y deben verificarse en el portal oficial.
          Este informe tiene caracter referencial y no sustituye certificados oficiales. Tratamiento de datos conforme a la LOPDP.
      </div>
      </div>
  </div>`
}

export function exportarPDF(data, showToast) {
  if (!data) { showToast('Primero realiza una consulta'); return }
  if (typeof window.html2pdf === 'undefined') { showToast('La libreria de PDF no cargo. Recarga la pagina.'); return }
  const ced = data.cedula || 'informe'
  showToast('Generando PDF...', 'success')

  const cont = document.createElement('div')
  cont.style.position = 'fixed'
  cont.style.left = '-9999px'
  cont.style.top = '0'
  cont.style.background = '#fff'
  cont.innerHTML = construirInformePDF(data)
  document.body.appendChild(cont)

  window.html2pdf().set({
    margin: [10, 10, 12, 10],
    filename: 'Verum_' + ced + '.pdf',
    image: { type: 'jpeg', quality: 0.98 },
    html2canvas: { scale: 2, backgroundColor: '#ffffff', useCORS: true },
    jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
    pagebreak: { mode: ['css', 'legacy'] },
  }).from(cont.firstElementChild).save().then(() => {
    document.body.removeChild(cont)
  }).catch(() => {
    document.body.removeChild(cont)
    showToast('No se pudo generar el PDF')
  })
}

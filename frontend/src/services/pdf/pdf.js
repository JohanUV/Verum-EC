// Servicio de exportacion del informe a PDF con TEXTO NATIVO (jsPDF).
// jsPDF lo carga el template como script suelto y expone window.jspdf.jsPDF.
// Ojo: el bundle de html2pdf NO define ese global, aunque lo incluya dentro.
// A diferencia del render por imagen (html2canvas),
// esto produce un documento vectorial: texto nitido y seleccionable, archivo
// liviano, paginacion automatica sin cortar tarjetas y marca de agua en todas
// las paginas.
import { USUARIO } from '@/utils/sesion'

// --- Geometria de pagina (A4 vertical, en mm) ------------------------------
const PAGE = { w: 210, h: 297 }
const M = { top: 14, bottom: 16, left: 12, right: 12 }
const CW = PAGE.w - M.left - M.right // ancho util del contenido

// Semaforo -> color, fondo y etiqueta del informe impreso (tema claro).
const SEM = {
  limpio:   { rgb: [21, 128, 61],  bg: [240, 253, 244], txt: 'SIN ANTECEDENTES RELEVANTES' },
  atencion: { rgb: [180, 83, 9],   bg: [255, 251, 235], txt: 'REQUIERE ATENCION' },
  alerta:   { rgb: [185, 28, 28],  bg: [254, 242, 242], txt: 'ALERTA - HALLAZGOS RELEVANTES' },
}
const INK = [17, 24, 39]
const MUTED = [107, 114, 128]
const BORDER = [225, 227, 232]
const DARK = [14, 14, 26]
const ROW_BG = [249, 250, 251]

// Altura aproximada de una linea de texto (pt -> mm) para reservar espacio.
// jsPDF usa lineHeightFactor 1.15 por defecto, que replicamos aqui.
const lh = (pt) => pt * 0.3528 * 1.15

// --- Utilidades de paginacion ----------------------------------------------
function marcaAgua(doc, folio) {
  doc.setFont('helvetica', 'bold')
  doc.setFontSize(28)
  doc.setTextColor(233, 233, 237)
  const t = `VERUM · CONFIDENCIAL · ${folio || ''}`
  for (let y = 55; y < PAGE.h; y += 58) {
    doc.text(t, 14, y, { angle: 26 })
  }
  doc.setTextColor(...INK)
}

function nuevaPagina(st) {
  st.doc.addPage()
  marcaAgua(st.doc, st.folio)
  st.y = M.top
}

// Salta de pagina si el bloque de alto `h` no cabe en la actual.
function need(st, h) {
  if (st.y + h > PAGE.h - M.bottom) nuevaPagina(st)
}

// --- Bloques del informe ---------------------------------------------------
function encabezado(st, data, fecha, r) {
  const d = st.doc
  const y = st.y
  d.setFillColor(...DARK)
  d.roundedRect(M.left, y, CW, 20, 2, 2, 'F')

  d.setFont('helvetica', 'bold'); d.setFontSize(20)
  d.setTextColor(255, 255, 255)
  d.text('VERUM', M.left + 6, y + 9)
  const wV = d.getTextWidth('VERUM')
  d.setTextColor(125, 211, 252)
  d.text(' EC', M.left + 6 + wV, y + 9)
  d.setFont('helvetica', 'normal'); d.setFontSize(9)
  d.setTextColor(203, 213, 225)
  d.text('Informe de Verificacion de Antecedentes', M.left + 6, y + 15)

  const rx = PAGE.w - M.right - 6
  d.setFont('helvetica', 'bold'); d.setFontSize(8)
  d.setTextColor(255, 255, 255)
  d.text(`Folio: ${data.folio || 'N/D'}`, rx, y + 7, { align: 'right' })
  d.setFont('helvetica', 'normal')
  d.setTextColor(203, 213, 225)
  d.text(`Generado: ${fecha}`, rx, y + 12, { align: 'right' })
  d.text(`Fuentes consultadas: ${r.fuentes_consultadas || 0}`, rx, y + 16.5, { align: 'right' })

  st.y += 20 + 6
}

function filaInfo(st, k, v) {
  const d = st.doc
  const kW = CW * 0.28, vW = CW - kW
  d.setFont('helvetica', 'normal'); d.setFontSize(9.5)
  const vLines = d.splitTextToSize(String(v ?? ''), vW - 6)
  const rowH = Math.max(lh(9.5) * vLines.length + 4.5, 8)
  need(st, rowH)
  const y = st.y
  d.setFillColor(...ROW_BG); d.rect(M.left, y, kW, rowH, 'F')
  d.setDrawColor(...BORDER)
  d.rect(M.left, y, kW, rowH)
  d.rect(M.left + kW, y, vW, rowH)
  d.setTextColor(...INK); d.setFont('helvetica', 'bold')
  d.text(String(k), M.left + 3, y + 5.5)
  d.setFont('helvetica', 'normal')
  d.text(vLines, M.left + kW + 3, y + 5.5)
  st.y += rowH
}

function semaforo(st, data, r) {
  const d = st.doc
  const s = SEM[data.semaforo] || SEM.limpio
  const boxH = 26
  need(st, boxH + 6)
  const y = st.y
  d.setFillColor(...s.bg); d.setDrawColor(...s.rgb)
  d.roundedRect(M.left, y, CW, boxH, 2, 2, 'FD')

  d.setFont('helvetica', 'bold'); d.setFontSize(14)
  d.setTextColor(...s.rgb)
  d.text(s.txt, M.left + 5, y + 8)

  // Score a la derecha
  const sx = PAGE.w - M.right - 5
  d.setFontSize(18)
  const score = `${data.score ?? 0}`
  d.text(score, sx, y + 8, { align: 'right' })
  const wScore = d.getTextWidth(score)
  d.setFont('helvetica', 'normal'); d.setFontSize(8); d.setTextColor(...MUTED)
  d.text('/100', sx - wScore - 1, y + 8, { align: 'right' })
  d.text(String(data.etiqueta_riesgo || 'Riesgo'), sx, y + 12.5, { align: 'right' })

  d.setFont('helvetica', 'normal'); d.setFontSize(9.5); d.setTextColor(55, 65, 81)
  const msg = d.splitTextToSize(String(data.mensaje || ''), CW - 45)
  d.text(msg, M.left + 5, y + 15)

  d.setFontSize(9.5); d.setTextColor(...INK)
  d.text(
    `${r.fuentes_consultadas || 0} fuentes   ·   ${r.con_hallazgos || 0} con datos   ·   ${r.alertas || 0} alertas`,
    M.left + 5, y + 22,
  )
  st.y += boxH + 6
}

function tituloSeccion(st, texto) {
  const d = st.doc
  need(st, 12)
  d.setFont('helvetica', 'bold'); d.setFontSize(12); d.setTextColor(...INK)
  d.text(texto, M.left, st.y + 4)
  d.setDrawColor(...DARK); d.setLineWidth(0.5)
  d.line(M.left, st.y + 6.5, PAGE.w - M.right, st.y + 6.5)
  d.setLineWidth(0.2)
  st.y += 11
}

function filaDato(st, k, v) {
  const d = st.doc
  const x = M.left + 5, w = CW - 5
  const kW = w * 0.45, vW = w - kW
  d.setFont('helvetica', 'normal'); d.setFontSize(9)
  const kLines = d.splitTextToSize(String(k || ''), kW - 5)
  const vLines = d.splitTextToSize(String(v || ''), vW - 5)
  const rowH = Math.max(lh(9) * kLines.length, lh(9) * vLines.length) + 3.5
  need(st, rowH)
  const y = st.y
  d.setFillColor(...ROW_BG); d.rect(x, y, kW, rowH, 'F')
  d.setDrawColor(...BORDER)
  d.rect(x, y, kW, rowH)
  d.rect(x + kW, y, vW, rowH)
  d.setTextColor(55, 65, 81); d.text(kLines, x + 2.5, y + 4.5)
  d.setTextColor(...INK); d.text(vLines, x + kW + 2.5, y + 4.5)
  st.y += rowH
}

function tarjeta(st, m) {
  const d = st.doc
  const col = (SEM[m.nivel] || SEM.limpio).rgb
  const tipo = m.tipo === 'real' ? 'API en vivo' : 'Informativo'

  // Encabezado de la tarjeta (barra de color + titulo + badge + resumen).
  d.setFontSize(10)
  const resumenLines = d.splitTextToSize(String(m.resumen || ''), CW - 12)
  const headH = 8 + lh(10) * resumenLines.length + 2
  // Evita que el encabezado quede huerfano al final de la pagina.
  need(st, headH + 8)
  const y = st.y

  d.setFillColor(...col); d.rect(M.left, y, 1.5, headH, 'F')

  d.setFont('helvetica', 'bold'); d.setFontSize(11); d.setTextColor(...INK)
  d.text(String(m.fuente || ''), M.left + 5, y + 5)

  d.setFont('helvetica', 'bold'); d.setFontSize(7.5)
  const bw = d.getTextWidth(tipo) + 6
  const bx = PAGE.w - M.right - bw
  d.setFillColor(...(m.tipo === 'real' ? [14, 116, 144] : [107, 114, 128]))
  d.roundedRect(bx, y + 1, bw, 5, 1, 1, 'F')
  d.setTextColor(255, 255, 255)
  d.text(tipo, bx + 3, y + 4.5)

  d.setFont('helvetica', 'bold'); d.setFontSize(10); d.setTextColor(...col)
  d.text(resumenLines, M.left + 5, y + 10)
  st.y += headH

  if (m.datos && m.datos.length) {
    for (const dr of m.datos) {
      let k, v
      if ('campo' in dr) { k = dr.campo; v = dr.valor }
      else {
        const ex = [dr.rol, dr.provincia, dr.estado].filter(Boolean).join(' · ')
        k = (dr.tipo || 'Registro') + (ex ? ` (${ex})` : ''); v = dr.fecha || ''
      }
      filaDato(st, k, v)
    }
  }

  if (m.enlace) {
    d.setFont('helvetica', 'normal'); d.setFontSize(8)
    const lines = d.splitTextToSize(`Portal oficial: ${m.enlace}`, CW - 6)
    const h = lh(8) * lines.length + 2
    need(st, h)
    d.setTextColor(...MUTED)
    d.text(lines, M.left + 5, st.y + 3.5)
    st.y += h
  }

  st.y += 5 // separacion entre tarjetas
}

function notaLegal(st, data) {
  const d = st.doc
  st.y += 3
  need(st, 8)
  d.setDrawColor(...BORDER); d.line(M.left, st.y, PAGE.w - M.right, st.y)
  st.y += 4
  d.setFont('helvetica', 'normal'); d.setFontSize(8); d.setTextColor(...MUTED)
  const txt = `Folio ${data.folio || 'N/D'} · Emitido por ${data.usuario || USUARIO || '—'} · `
    + `Proposito declarado: ${data.proposito || 'No especificado'}. `
    + 'Documento generado automaticamente por Verum a partir de fuentes publicas del Ecuador. '
    + 'Las fuentes marcadas como "Informativo" no exponen API y deben verificarse en el portal oficial. '
    + 'Este informe tiene caracter referencial y no sustituye certificados oficiales. '
    + 'Tratamiento de datos conforme a la LOPDP.'
  const lines = d.splitTextToSize(txt, CW)
  for (const ln of lines) {
    need(st, lh(8) + 0.5)
    d.text(ln, M.left, st.y + 3)
    st.y += lh(8) + 0.5
  }
}

function pieDePagina(doc, page, total) {
  doc.setFont('helvetica', 'normal'); doc.setFontSize(8); doc.setTextColor(...MUTED)
  const y = PAGE.h - 8
  doc.text('Verum EC · Documento confidencial', M.left, y)
  doc.text(`Pagina ${page} de ${total}`, PAGE.w - M.right, y, { align: 'right' })
}

// --- API publica -----------------------------------------------------------
export function exportarPDF(data, showToast) {
  if (!data) { showToast('Primero realiza una consulta'); return }
  const Ctor = window.jspdf && window.jspdf.jsPDF
  if (!Ctor) { showToast('La libreria de PDF no cargo. Recarga la pagina.'); return }

  try {
    showToast('Generando PDF...', 'success')
    const doc = new Ctor({ unit: 'mm', format: 'a4', orientation: 'portrait' })
    doc.setLineWidth(0.2)

    const r = data.resumen || {}
    const fecha = new Date().toLocaleString('es-EC', { dateStyle: 'long', timeStyle: 'short' })
    const st = { doc, y: M.top, folio: data.folio }

    marcaAgua(doc, st.folio)
    encabezado(st, data, fecha, r)

    st.y += 2
    filaInfo(st, 'Cedula', data.cedula || '')
    filaInfo(st, 'Titular', data.titular || 'No determinado')
    filaInfo(st, 'Proposito (LOPDP)', data.proposito || 'No especificado')
    filaInfo(st, 'Emitido por', data.usuario || USUARIO || '—')
    st.y += 6

    semaforo(st, data, r)
    tituloSeccion(st, 'Detalle por fuente')
    for (const m of (data.resultados || [])) tarjeta(st, m)
    notaLegal(st, data)

    // Pie con numeracion en todas las paginas (una vez conocido el total).
    const total = doc.internal.getNumberOfPages()
    for (let p = 1; p <= total; p++) {
      doc.setPage(p)
      pieDePagina(doc, p, total)
    }

    doc.save('Verum_' + (data.cedula || 'informe') + '.pdf')
  } catch (e) {
    showToast('No se pudo generar el PDF')
  }
}

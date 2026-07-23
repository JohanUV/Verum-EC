// Constantes de presentacion y utilidades de formato.
export const ICON_STATUS = { limpio: 'fa-circle-check', atencion: 'fa-circle-exclamation', alerta: 'fa-triangle-exclamation' }
export const ICON_SEMAFORO = { limpio: 'fa-shield-check', atencion: 'fa-shield-halved', alerta: 'fa-shield-virus' }
export const TXT_SEMAFORO = { limpio: 'Perfil Limpio', atencion: 'Requiere Revisión', alerta: 'Hallazgos Relevantes' }

// Color del score de riesgo (0 verde -> 100 rojo)
export function COLOR_SCORE(s) {
  s = s || 0
  if (s >= 60) return 'var(--danger)'
  if (s >= 25) return 'var(--warning)'
  if (s > 0) return '#fbbf24'
  return 'var(--success)'
}

// --- Categorias del informe ------------------------------------------------
// Agrupan las fuentes por ambito para que el informe sea mas facil de leer.
// El orden aqui define el orden de aparicion de las secciones.
export const CATEGORIAS = [
  { id: 'judicial',    titulo: 'Judicial y penal',          icono: 'fa-scale-balanced',       sub: 'Procesos judiciales y récord policial' },
  { id: 'tributario',  titulo: 'Tributario (SRI)',          icono: 'fa-file-invoice-dollar',  sub: 'Contribuyente, deudas y establecimientos' },
  { id: 'obligaciones',titulo: 'Obligaciones y multas',     icono: 'fa-money-bill-wave',      sub: 'Pensiones alimenticias y tránsito' },
  { id: 'sanciones',   titulo: 'Sanciones internacionales', icono: 'fa-ban',                  sub: 'Cotejo en listas OFAC / ONU' },
  { id: 'educacion',   titulo: 'Educación y títulos',       icono: 'fa-graduation-cap',       sub: 'Bachiller y educación superior' },
  { id: 'social',      titulo: 'Programas sociales',        icono: 'fa-house-user',           sub: 'Registro Social (MIES)' },
  { id: 'otros',       titulo: 'Otras fuentes',             icono: 'fa-layer-group',          sub: 'Fuentes adicionales' },
]

// Determina la categoria de un resultado a partir de su fuente/clave.
export function categoriaDe(m) {
  const f = (m.fuente || '').toLowerCase()
  const clave = m.clave || ''
  if (f.includes('judicial') || f.includes('policial') || f.includes('penal')) return 'judicial'
  if (f.includes('sri')) return 'tributario'
  if (f.includes('pension') || f.includes('multa') || f.includes('ant') || f.includes('tránsito') || f.includes('transito')) return 'obligaciones'
  if (f.includes('sanci') || f.includes('ofac') || f.includes('onu')) return 'sanciones'
  if (clave === 'senescyt' || clave === 'bachiller' || f.includes('título') || f.includes('titulo') || f.includes('senescyt') || f.includes('bachiller') || f.includes('educación') || f.includes('educacion')) return 'educacion'
  if (clave === 'registro_social' || f.includes('registro social')) return 'social'
  return 'otros'
}

// Agrupa los resultados por categoria, respetando el orden de CATEGORIAS.
// Devuelve [{ ...categoria, items:[...] }] omitiendo las categorias vacias.
export function agruparPorCategoria(resultados) {
  return CATEGORIAS
    .map(cat => ({ ...cat, items: (resultados || []).filter(m => categoriaDe(m) === cat.id) }))
    .filter(cat => cat.items.length > 0)
}

// Escape HTML para las cadenas que se interpolan en el informe PDF
// (el resto de la interfaz la escapa React automaticamente).
export function esc(s) {
  return String(s == null ? '' : s).replace(/[&<>"]/g, c =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]))
}

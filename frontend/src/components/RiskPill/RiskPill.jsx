const PILL_MAP = {
  alerta: ['Alerta', 'var(--danger)', 'rgba(248,113,113,.15)'],
  atencion: ['Revisar', 'var(--warning)', 'rgba(251,191,36,.15)'],
  limpio: ['Limpio', 'var(--success)', 'rgba(52,211,153,.15)'],
}

export default function RiskPill({ semaforo }) {
  const [txt, col, bg] = PILL_MAP[semaforo] || PILL_MAP.limpio
  return <span className="pill" style={{ background: bg, color: col }}>{txt}</span>
}

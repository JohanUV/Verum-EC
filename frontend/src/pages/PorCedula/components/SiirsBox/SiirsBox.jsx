// Registro Social (SIIRS): consulta manual asistida — copia la cedula al
// portapapeles y abre el portal oficial (reCAPTCHA no automatizable).
import { useEffect, useState } from 'react'

const SIIRS_URL = 'https://siirs.registrosocial.gob.ec/pages/publico/busquedaPublica.jsf'

export default function SiirsBox({ cedula }) {
  const [copiada, setCopiada] = useState(false)

  useEffect(() => {
    (async () => {
      if (cedula) {
        try { await navigator.clipboard.writeText(cedula); setCopiada(true) } catch (e) { setCopiada(false) }
      }
      window.open(SIIRS_URL, '_blank', 'noopener')
    })()
  }, [])

  return (
    <div className="siirs-box">
      <div className="siirs-note">
        <div>
          {copiada
            ? <><i className="fas fa-clipboard-check" style={{ color: 'var(--success)' }}></i> Cedula <strong>{cedula}</strong> copiada al portapapeles.</>
            : <><i className="fas fa-circle-info"></i> Copia la cedula <strong>{cedula}</strong> manualmente.</>}
        </div>
        <ol className="siirs-steps">
          <li>Pega la cedula en el campo de busqueda del SIIRS.</li>
          <li>Ingresa la <strong>fecha de expedicion</strong> de la cedula.</li>
          <li>Resuelve el <strong>reCAPTCHA</strong> y consulta.</li>
        </ol>
      </div>
    </div>
  )
}

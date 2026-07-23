// Contexto de notificaciones flotantes (toast). El provider renderiza el aviso
// y expone showToast(mensaje, tipo) a toda la aplicacion.
import { createContext, useCallback, useRef, useState } from 'react'

export const ToastContext = createContext(() => {})

export function ToastProvider({ children }) {
  const [toast, setToast] = useState(null)
  const timer = useRef(null)

  const showToast = useCallback((msg, type) => {
    clearTimeout(timer.current)
    setToast({ msg, type: type || 'error' })
    timer.current = setTimeout(() => setToast(null), 3500)
  }, [])

  return (
    <ToastContext.Provider value={showToast}>
      {children}
      {toast && (
        <div className={`toast ${toast.type}`} style={{ display: 'block' }}>{toast.msg}</div>
      )}
    </ToastContext.Provider>
  )
}

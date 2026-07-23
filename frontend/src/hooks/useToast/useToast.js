// Hook de acceso al contexto de notificaciones: const showToast = useToast()
import { useContext } from 'react'
import { ToastContext } from '@/contexts/ToastContext/ToastContext.jsx'

export const useToast = () => useContext(ToastContext)

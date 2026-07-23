// Datos de sesion inyectados por Flask en index.html antes de cargar el bundle.
export const PERMISOS = window.PERMISOS || []
export const ROL = window.ROL || ''
export const USUARIO = window.USUARIO || ''

export const puede = (p) => PERMISOS.includes(p)

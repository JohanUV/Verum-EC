// Definicion de las secciones (pestanas) de la aplicacion y su permiso requerido.
import { Historial, PorCedula, PorNombre } from '@/pages'

export const RUTAS = [
  { id: 'cedula', icono: 'fa-id-card', texto: 'Por Cédula', Componente: PorCedula },
  { id: 'nombre', icono: 'fa-user-tag', texto: 'Por Nombre', Componente: PorNombre },
  { id: 'historial', icono: 'fa-clock-rotate-left', texto: 'Historial', permiso: 'historial', Componente: Historial },
]

// Filtra las rutas visibles segun los permisos del rol en sesion.
export const rutasPermitidas = (puede) => RUTAS.filter(r => !r.permiso || puede(r.permiso))

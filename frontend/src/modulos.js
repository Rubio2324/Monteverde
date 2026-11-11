// Tarjetas del tablero. Cada rol ve solo las suyas (hoy: Administrador).
export const MODULOS = [
  {
    ruta: '/beneficiarios',
    titulo: 'Beneficiarios',
    descripcion: 'Fichas, estados, historial y acudientes.',
    icono: 'users',
    roles: ['Administrador'],
  },
  {
    ruta: '/cursos',
    titulo: 'Cursos',
    descripcion: 'Oferta academica y matriculas.',
    icono: 'book',
    roles: ['Administrador'],
  },
  {
    ruta: '/inscripciones',
    titulo: 'Inscripciones',
    descripcion: 'Importar desde Google Forms y revisar.',
    icono: 'inbox',
    roles: ['Administrador'],
  },
  {
    ruta: '/auditoria',
    titulo: 'Auditoria',
    descripcion: 'Trazabilidad de todas las acciones.',
    icono: 'shield',
    roles: ['Administrador'],
  },
]

export const modulosDe = (roles) =>
  MODULOS.filter((m) => m.roles.some((r) => roles.includes(r)))
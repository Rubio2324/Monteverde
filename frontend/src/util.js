export const DIAS = ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo']

export const fecha = (iso) => (iso ? iso.split('-').reverse().join('/') : '—')

export const hora = (h) => (h ? h.slice(0, 5) : '—')

export const horario = (c) =>
  c.dia || c.hora_inicio
    ? `${c.dia ?? ''} ${c.hora_inicio ? `${hora(c.hora_inicio)}–${hora(c.hora_fin)}` : ''}`.trim()
    : '—'

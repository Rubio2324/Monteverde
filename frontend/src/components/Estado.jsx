export const ETIQUETAS = {
  aspirante: 'Aspirante',
  admitido: 'Admitido',
  no_admitido: 'No admitido',
  matriculado: 'Matriculado',
  egresado: 'Egresado',
  retirado: 'Retirado',
}

export default function Estado({ valor }) {
  if (!valor) return <span className="badge b-sin">Sin estado</span>
  return <span className={`badge b-${valor}`}>{ETIQUETAS[valor] ?? valor}</span>
}
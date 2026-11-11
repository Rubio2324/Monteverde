import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'

export default function CursosDeBeneficiario({ documento }) {
  const [cursos, setCursos] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api(`/beneficiarios/${documento}/cursos`)
      .then(setCursos)
      .catch((e) => setError(e.message))
  }, [documento])

  return (
    <section className="glass seccion">
      <h2>Cursos</h2>
      {error && <div className="alerta" role="alert">{error}</div>}
      {cursos && cursos.length === 0 && <p className="tenue">No esta matriculado en ningun curso.</p>}
      <ul className="lista">
        {cursos?.map((m) => (
          <li key={m.id_matricula}>
            <strong><Link to={`/cursos/${m.id_curso}`} className="enlace">{m.curso}</Link></strong>
            <span>
              {m.numero_asistencias} asistencias · {m.aprobo === null ? 'sin resultado' : m.aprobo ? 'aprobo' : 'no aprobo'}
              {m.nota_definitiva !== null && m.nota_definitiva !== undefined ? ` · nota ${m.nota_definitiva}` : ''}
            </span>
          </li>
        ))}
      </ul>
    </section>
  )
}

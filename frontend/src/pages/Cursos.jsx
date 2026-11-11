import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../api'
import { useCatalogos } from '../catalogos'
import { horario } from '../util'

const TAMANO = 10

export default function Cursos() {
  const navegar = useNavigate()
  const cat = useCatalogos()
  const [programa, setPrograma] = useState('')
  const [page, setPage] = useState(1)
  const [datos, setDatos] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    let vigente = true
    const params = new URLSearchParams({ page, size: TAMANO })
    if (programa) params.set('id_programa', programa)
    setError('')
    api(`/cursos?${params}`)
      .then((d) => vigente && setDatos(d))
      .catch((e) => vigente && setError(e.message))
    return () => {
      vigente = false
    }
  }, [programa, page])

  const paginas = datos ? Math.max(1, Math.ceil(datos.total / datos.size)) : 1

  return (
    <>
      <div className="cabecera">
        <div>
          <h1>Cursos</h1>
          <p>{datos ? `${datos.total} cursos` : 'Cargando…'}</p>
        </div>
        <Link to="/cursos/nuevo" className="btn btn-enlace">+ Nuevo curso</Link>
      </div>

      <div className="herramientas">
        <select
          value={programa}
          onChange={(e) => {
            setPrograma(e.target.value)
            setPage(1)
          }}
        >
          <option value="">Todos los programas</option>
          {cat?.programas.map((p) => (
            <option key={p.id} value={p.id}>{p.nombre}</option>
          ))}
        </select>
      </div>

      {error && <div className="alerta" role="alert">{error}</div>}

      <section className="glass tabla-caja">
        <table className="tabla">
          <thead>
            <tr>
              <th>Curso</th>
              <th>Programa</th>
              <th>Profesor</th>
              <th>Horario</th>
              <th>Matriculados</th>
            </tr>
          </thead>
          <tbody>
            {datos?.items.map((c) => (
              <tr key={c.id_curso} onClick={() => navegar(`/cursos/${c.id_curso}`)}>
                <td className="nombre">{c.nombre}</td>
                <td>{c.programa}</td>
                <td>{c.profesor}</td>
                <td>{horario(c)}</td>
                <td>{c.matriculados}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {datos && datos.items.length === 0 && <div className="vacio">No hay cursos todavia</div>}

        <div className="paginacion">
          <span>Pagina {page} de {paginas}</span>
          <div>
            <button className="btn-suave" disabled={page <= 1} onClick={() => setPage(page - 1)}>Anterior</button>
            <button className="btn-suave" disabled={page >= paginas} onClick={() => setPage(page + 1)}>Siguiente</button>
          </div>
        </div>
      </section>
    </>
  )
}

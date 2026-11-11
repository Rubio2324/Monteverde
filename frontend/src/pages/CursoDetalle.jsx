import { useCallback, useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api'
import Estado from '../components/Estado'
import { fecha, horario } from '../util'

export default function CursoDetalle() {
  const { id } = useParams()
  const [curso, setCurso] = useState(null)
  const [matriculas, setMatriculas] = useState([])
  const [error, setError] = useState('')
  const [q, setQ] = useState('')
  const [resultados, setResultados] = useState([])
  const [mensaje, setMensaje] = useState('')
  const [enviando, setEnviando] = useState(null)

  const cargar = useCallback(async () => {
    try {
      const [c, m] = await Promise.all([api(`/cursos/${id}`), api(`/cursos/${id}/matriculas`)])
      setCurso(c)
      setMatriculas(m)
      setError('')
    } catch (e) {
      setError(e.message)
    }
  }, [id])

  useEffect(() => {
    cargar()
  }, [cargar])

  // Buscador de beneficiarios (espera a que termines de escribir)
  useEffect(() => {
    const texto = q.trim()
    if (texto.length < 2) {
      setResultados([])
      return
    }
    let vigente = true
    const t = setTimeout(() => {
      api(`/beneficiarios?q=${encodeURIComponent(texto)}&size=6`)
        .then((d) => vigente && setResultados(d.items))
        .catch((e) => vigente && setMensaje(e.message))
    }, 450)
    return () => {
      vigente = false
      clearTimeout(t)
    }
  }, [q])

  const inscritos = new Set(matriculas.map((m) => m.numero_identificacion_persona))

  async function matricular(documento) {
    setMensaje('')
    setEnviando(documento)
    try {
      await api(`/cursos/${id}/matriculas`, {
        method: 'POST',
        body: { numero_identificacion_persona: documento },
      })
      await cargar()
    } catch (err) {
      setMensaje(err.message)
    } finally {
      setEnviando(null)
    }
  }

  if (!curso) {
    return (
      <>
        <Link to="/cursos" className="volver">← Cursos</Link>
        {error ? <div className="alerta" role="alert">{error}</div> : <p className="tenue">Cargando…</p>}
      </>
    )
  }

  return (
    <>
      <Link to="/cursos" className="volver">← Cursos</Link>

      <section className="glass encabezado-ficha">
        <div>
          <h1>{curso.nombre}</h1>
          <p className="tenue">{curso.programa} · {curso.profesor}</p>
        </div>
        <div className="acciones">
          <span className="badge b-admitido">{curso.matriculados} matriculados</span>
          <Link to={`/cursos/${id}/editar`} className="btn-suave">Editar</Link>
        </div>
      </section>

      <div className="ficha-rejilla">
        <section className="glass seccion">
          <h2>Datos del curso</h2>
          <div className="datos">
            <div className="dato"><span>Horario</span><strong>{horario(curso)}</strong></div>
            <div className="dato"><span>Calificable</span><strong>{curso.es_calificable ? 'Si' : 'No'}</strong></div>
            <div className="dato"><span>Inicio</span><strong>{fecha(curso.fecha_inicio)}</strong></div>
            <div className="dato"><span>Fin</span><strong>{fecha(curso.fecha_fin)}</strong></div>
          </div>
        </section>

        <section className="glass seccion">
          <h2>Matricular beneficiario</h2>
          <input
            placeholder="Busca por documento o nombre (minimo 2 letras)"
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
          <p className="tenue pequeno">Solo se matriculan beneficiarios admitidos o matriculados.</p>
          <ul className="lista">
            {resultados.map((b) => (
              <li key={b.numero_identificacion}>
                <strong>{b.nombres} {b.apellidos}</strong>
                <span>{b.tipo_identificacion} {b.numero_identificacion}</span>
                <div className="fila-acciones">
                  <Estado valor={b.estado} />
                  <button
                    type="button"
                    className="btn-suave"
                    disabled={inscritos.has(b.numero_identificacion) || enviando === b.numero_identificacion}
                    onClick={() => matricular(b.numero_identificacion)}
                  >
                    {inscritos.has(b.numero_identificacion) ? 'Ya matriculado' : 'Matricular'}
                  </button>
                </div>
              </li>
            ))}
          </ul>
          {mensaje && <div className="alerta" role="alert">{mensaje}</div>}
        </section>
      </div>

      <section className="glass tabla-caja bloque">
        <table className="tabla">
          <thead>
            <tr>
              <th>Beneficiario</th>
              <th>Documento</th>
              <th>Asistencias</th>
              <th>Aprobo</th>
              <th>Nota</th>
            </tr>
          </thead>
          <tbody>
            {matriculas.map((m) => (
              <tr key={m.id_matricula}>
                <td className="nombre">
                  <Link to={`/beneficiarios/${m.numero_identificacion_persona}`} className="enlace">
                    {m.nombres} {m.apellidos}
                  </Link>
                </td>
                <td className="doc">{m.numero_identificacion_persona}</td>
                <td>{m.numero_asistencias}</td>
                <td>{m.aprobo === null ? '—' : m.aprobo ? 'Si' : 'No'}</td>
                <td>{m.nota_definitiva ?? '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {matriculas.length === 0 && <div className="vacio">Aun no hay matriculados</div>}
      </section>
    </>
  )
}

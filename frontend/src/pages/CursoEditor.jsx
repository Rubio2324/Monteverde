import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { api } from '../api'
import { useCatalogos } from '../catalogos'
import { DIAS } from '../util'

const VACIO = {
  nombre: '',
  id_programa: '',
  numero_identificacion_profesor: '',
  dia: '',
  hora_inicio: '',
  hora_fin: '',
  fecha_inicio: '',
  fecha_fin: '',
  es_calificable: false,
}

// Sirve para crear (/cursos/nuevo) y para editar (/cursos/:id/editar)
export default function CursoEditor() {
  const { id } = useParams()
  const editar = Boolean(id)
  const navegar = useNavigate()
  const cat = useCatalogos()
  const [profesores, setProfesores] = useState([])
  const [f, setF] = useState(VACIO)
  const [cargando, setCargando] = useState(editar)
  const [error, setError] = useState('')
  const [enviando, setEnviando] = useState(false)

  const poner = (k) => (e) => setF({ ...f, [k]: e.target.value })

  useEffect(() => {
    api('/profesores').then(setProfesores).catch(() => {})
  }, [])

  useEffect(() => {
    if (!id) return
    api(`/cursos/${id}`)
      .then((c) => {
        setF({
          nombre: c.nombre,
          id_programa: String(c.id_programa),
          numero_identificacion_profesor: c.numero_identificacion_profesor,
          dia: c.dia || '',
          hora_inicio: (c.hora_inicio || '').slice(0, 5),
          hora_fin: (c.hora_fin || '').slice(0, 5),
          fecha_inicio: c.fecha_inicio || '',
          fecha_fin: c.fecha_fin || '',
          es_calificable: c.es_calificable,
        })
      })
      .catch((e) => setError(e.message))
      .finally(() => setCargando(false))
  }, [id])

  async function enviar(e) {
    e.preventDefault()
    setError('')
    setEnviando(true)
    const cuerpo = {
      nombre: f.nombre.trim(),
      id_programa: Number(f.id_programa),
      numero_identificacion_profesor: f.numero_identificacion_profesor,
      dia: f.dia || null,
      hora_inicio: f.hora_inicio || null,
      hora_fin: f.hora_fin || null,
      fecha_inicio: f.fecha_inicio || null,
      fecha_fin: f.fecha_fin || null,
      es_calificable: f.es_calificable,
    }
    try {
      const curso = editar
        ? await api(`/cursos/${id}`, { method: 'PATCH', body: cuerpo })
        : await api('/cursos', { method: 'POST', body: cuerpo })
      navegar(`/cursos/${curso.id_curso}`)
    } catch (err) {
      setError(err.message)
      setEnviando(false)
    }
  }

  const volver = editar ? `/cursos/${id}` : '/cursos'

  return (
    <>
      <Link to={volver} className="volver">← {editar ? 'Volver al curso' : 'Cursos'}</Link>
      <div className="cabecera">
        <div>
          <h1>{editar ? 'Editar curso' : 'Nuevo curso'}</h1>
        </div>
      </div>

      {cargando ? (
        <p className="tenue">Cargando…</p>
      ) : (
        <form className="glass form-panel" onSubmit={enviar}>
          <div className="form-rejilla">
            <label className="campo-ancho">
              Nombre del curso
              <input value={f.nombre} onChange={poner('nombre')} maxLength={150} required />
            </label>
            <label>
              Programa
              <select value={f.id_programa} onChange={poner('id_programa')} required>
                <option value="">Selecciona…</option>
                {cat?.programas.map((p) => <option key={p.id} value={p.id}>{p.nombre}</option>)}
              </select>
            </label>
            <label>
              Profesor
              <select value={f.numero_identificacion_profesor} onChange={poner('numero_identificacion_profesor')} required>
                <option value="">Selecciona…</option>
                {profesores.map((p) => (
                  <option key={p.numero_identificacion} value={p.numero_identificacion} disabled={p.estado !== 'activo'}>
                    {p.nombres} {p.apellidos}{p.estado !== 'activo' ? ' (inactivo)' : ''}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Dia
              <select value={f.dia} onChange={poner('dia')}>
                <option value="">Sin definir</option>
                {DIAS.map((d) => <option key={d} value={d}>{d}</option>)}
              </select>
            </label>
            <label>
              Hora de inicio
              <input type="time" value={f.hora_inicio} onChange={poner('hora_inicio')} />
            </label>
            <label>
              Hora de fin
              <input type="time" value={f.hora_fin} onChange={poner('hora_fin')} />
            </label>
            <label>
              Fecha de inicio
              <input type="date" value={f.fecha_inicio} onChange={poner('fecha_inicio')} />
            </label>
            <label>
              Fecha de fin
              <input type="date" value={f.fecha_fin} onChange={poner('fecha_fin')} />
            </label>
            <label className="check campo-ancho">
              <input
                type="checkbox"
                checked={f.es_calificable}
                onChange={(e) => setF({ ...f, es_calificable: e.target.checked })}
              />
              El curso es calificable
            </label>
          </div>

          {error && <div className="alerta" role="alert">{error}</div>}

          <div className="form-pie">
            <Link to={volver} className="btn-suave">Cancelar</Link>
            <button className="btn" disabled={enviando}>
              {enviando ? 'Guardando…' : editar ? 'Guardar cambios' : 'Crear curso'}
            </button>
          </div>
        </form>
      )}
    </>
  )
}

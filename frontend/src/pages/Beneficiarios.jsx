import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'
import Estado, { ETIQUETAS } from '../components/Estado'

const TAMANO = 10

export default function Beneficiarios() {
  const navegar = useNavigate()
  const [texto, setTexto] = useState('')
  const [busqueda, setBusqueda] = useState('')
  const [estado, setEstado] = useState('')
  const [page, setPage] = useState(1)
  const [datos, setDatos] = useState(null)
  const [error, setError] = useState('')

  // Espera a que el usuario deje de escribir antes de consultar
  useEffect(() => {
    const t = setTimeout(() => {
      setBusqueda(texto.trim())
      setPage(1)
    }, 450)
    return () => clearTimeout(t)
  }, [texto])

  useEffect(() => {
    let vigente = true
    const params = new URLSearchParams({ page, size: TAMANO })
    if (busqueda) params.set('q', busqueda)
    if (estado) params.set('estado', estado)
    setError('')
    api(`/beneficiarios?${params}`)
      .then((d) => vigente && setDatos(d))
      .catch((e) => vigente && setError(e.message))
    return () => {
      vigente = false
    }
  }, [busqueda, estado, page])

  const paginas = datos ? Math.max(1, Math.ceil(datos.total / datos.size)) : 1

  return (
    <>
      <div className="cabecera">
        <div>
          <h1>Beneficiarios</h1>
          <p>{datos ? `${datos.total} registrados` : 'Cargando…'}</p>
        </div>
      </div>

      <div className="herramientas">
        <input
          placeholder="Buscar por documento, nombres o apellidos"
          value={texto}
          onChange={(e) => setTexto(e.target.value)}
        />
        <select
          value={estado}
          onChange={(e) => {
            setEstado(e.target.value)
            setPage(1)
          }}
        >
          <option value="">Todos los estados</option>
          {Object.entries(ETIQUETAS).map(([valor, nombre]) => (
            <option key={valor} value={valor}>{nombre}</option>
          ))}
        </select>
      </div>

      {error && <div className="alerta" role="alert">{error}</div>}

      <section className="glass tabla-caja">
        <table className="tabla">
          <thead>
            <tr>
              <th>Documento</th>
              <th>Nombre</th>
              <th>Grado</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            {datos?.items.map((b) => (
              <tr key={b.numero_identificacion} onClick={() => navegar(`/beneficiarios/${b.numero_identificacion}`)}>
                <td className="doc">{b.tipo_identificacion} {b.numero_identificacion}</td>
                <td className="nombre">{b.nombres} {b.apellidos}</td>
                <td>{b.grado || '—'}</td>
                <td><Estado valor={b.estado} /></td>
              </tr>
            ))}
          </tbody>
        </table>
        {datos && datos.items.length === 0 && <div className="vacio">No hay resultados</div>}

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
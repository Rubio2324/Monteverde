import { useState } from 'react'
import { api } from '../api'

const VINCULOS = ['Madre', 'Padre', 'Abuela', 'Abuelo', 'Tia', 'Tio', 'Hermana', 'Hermano', 'Tutor legal', 'Otro']
const TIPOS = ['CC', 'CE', 'TI', 'OTRO']
const VACIO = {
  numero_identificacion: '',
  tipo_identificacion: 'CC',
  nombres: '',
  apellidos: '',
  vinculo: 'Madre',
  telefono: '',
  correo: '',
  ocupacion: '',
}

export default function Acudientes({ documento, lista, onCambio }) {
  const [abierto, setAbierto] = useState(false)
  const [f, setF] = useState(VACIO)
  const [error, setError] = useState('')
  const [enviando, setEnviando] = useState(false)
  const [quitar, setQuitar] = useState(null)

  const poner = (k) => (e) => setF({ ...f, [k]: e.target.value })

  async function vincular(e) {
    e.preventDefault()
    setError('')
    setEnviando(true)
    try {
      await api(`/beneficiarios/${documento}/acudientes`, {
        method: 'POST',
        body: {
          ...f,
          numero_identificacion: f.numero_identificacion.trim(),
          nombres: f.nombres.trim(),
          apellidos: f.apellidos.trim(),
          telefono: f.telefono.trim() || null,
          correo: f.correo.trim() || null,
          ocupacion: f.ocupacion.trim() || null,
        },
      })
      setF(VACIO)
      setAbierto(false)
      await onCambio()
    } catch (err) {
      setError(err.message)
    } finally {
      setEnviando(false)
    }
  }

  async function desvincular(id) {
    setError('')
    try {
      await api(`/beneficiarios/${documento}/acudientes/${id}`, { method: 'DELETE' })
      setQuitar(null)
      await onCambio()
    } catch (err) {
      setError(err.message)
      setQuitar(null)
    }
  }

  return (
    <section className="glass seccion">
      <div className="seccion-titulo">
        <h2>Acudientes</h2>
        <button type="button" className="btn-suave" onClick={() => setAbierto(!abierto)}>
          {abierto ? 'Cerrar' : '+ Vincular'}
        </button>
      </div>

      {lista.length === 0 && <p className="tenue">Sin acudientes vinculados.</p>}
      <ul className="lista">
        {lista.map((a) => (
          <li key={a.numero_identificacion}>
            <strong>{a.nombres} {a.apellidos}</strong>
            <span>{a.vinculo} · {a.tipo_identificacion} {a.numero_identificacion}</span>
            <span>{[a.telefono, a.correo].filter(Boolean).join(' · ') || 'Sin contacto'}</span>
            <div className="fila-acciones">
              {quitar === a.numero_identificacion ? (
                <>
                  <span>¿Desvincular?</span>
                  <button type="button" className="btn-suave peligro" onClick={() => desvincular(a.numero_identificacion)}>Si, quitar</button>
                  <button type="button" className="btn-suave" onClick={() => setQuitar(null)}>No</button>
                </>
              ) : (
                <button type="button" className="btn-suave" onClick={() => setQuitar(a.numero_identificacion)}>Quitar</button>
              )}
            </div>
          </li>
        ))}
      </ul>

      {abierto && (
        <form className="mini-form" onSubmit={vincular}>
          <div className="form-rejilla">
            <label>
              Tipo
              <select value={f.tipo_identificacion} onChange={poner('tipo_identificacion')}>
                {TIPOS.map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
            </label>
            <label>
              Documento
              <input value={f.numero_identificacion} onChange={poner('numero_identificacion')} inputMode="numeric" pattern="\d{5,15}" title="Entre 5 y 15 digitos" required />
            </label>
            <label>
              Nombres
              <input value={f.nombres} onChange={poner('nombres')} maxLength={120} required />
            </label>
            <label>
              Apellidos
              <input value={f.apellidos} onChange={poner('apellidos')} maxLength={120} required />
            </label>
            <label>
              Vinculo
              <select value={f.vinculo} onChange={poner('vinculo')}>
                {VINCULOS.map((v) => <option key={v} value={v}>{v}</option>)}
              </select>
            </label>
            <label>
              Telefono
              <input value={f.telefono} onChange={poner('telefono')} maxLength={30} />
            </label>
            <label>
              Correo
              <input type="email" value={f.correo} onChange={poner('correo')} maxLength={150} />
            </label>
            <label>
              Ocupacion
              <input value={f.ocupacion} onChange={poner('ocupacion')} maxLength={120} />
            </label>
          </div>
          <p className="tenue pequeno">Si el documento ya existe como acudiente (por ejemplo, de un hermano), se reutiliza.</p>
          <button className="btn" disabled={enviando}>{enviando ? 'Vinculando…' : 'Vincular acudiente'}</button>
        </form>
      )}

      {error && <div className="alerta" role="alert">{error}</div>}
    </section>
  )
}
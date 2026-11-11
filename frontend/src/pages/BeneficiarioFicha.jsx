import { useCallback, useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api'
import { nombreDe, useCatalogos } from '../catalogos'
import Estado, { ETIQUETAS } from '../components/Estado'

// Mismas transiciones que valida el backend
const TRANSICIONES = {
  aspirante: ['admitido', 'no_admitido'],
  admitido: ['matriculado', 'retirado'],
  no_admitido: ['aspirante'],
  matriculado: ['egresado', 'retirado'],
  egresado: [],
  retirado: ['admitido'],
}

const fecha = (iso) => (iso ? iso.split('-').reverse().join('/') : '—')
const sn = (v) => (v === null || v === undefined ? '—' : v ? 'Si' : 'No')

function edad(iso) {
  if (!iso) return null
  const n = new Date(iso)
  const hoy = new Date()
  let e = hoy.getFullYear() - n.getFullYear()
  if (hoy.getMonth() < n.getMonth() || (hoy.getMonth() === n.getMonth() && hoy.getDate() < n.getDate())) e -= 1
  return e
}

function Dato({ etiqueta, valor, ancho }) {
  const vacio = valor === null || valor === undefined || valor === ''
  return (
    <div className={ancho ? 'dato ancho' : 'dato'}>
      <span>{etiqueta}</span>
      <strong>{vacio ? '—' : valor}</strong>
    </div>
  )
}

export default function BeneficiarioFicha() {
  const { documento } = useParams()
  const cat = useCatalogos()
  const [ficha, setFicha] = useState(null)
  const [historial, setHistorial] = useState([])
  const [acudientes, setAcudientes] = useState([])
  const [error, setError] = useState('')
  const [nuevo, setNuevo] = useState('')
  const [obs, setObs] = useState('')
  const [mensaje, setMensaje] = useState('')
  const [enviando, setEnviando] = useState(false)

  const cargar = useCallback(async () => {
    try {
      const [f, h, a] = await Promise.all([
        api(`/beneficiarios/${documento}`),
        api(`/beneficiarios/${documento}/historial`),
        api(`/beneficiarios/${documento}/acudientes`),
      ])
      setFicha(f)
      setHistorial(h)
      setAcudientes(a)
      setError('')
    } catch (e) {
      setError(e.message)
    }
  }, [documento])

  useEffect(() => {
    cargar()
  }, [cargar])

  async function aplicar(e) {
    e.preventDefault()
    setMensaje('')
    setEnviando(true)
    try {
      await api(`/beneficiarios/${documento}/estado`, {
        method: 'PATCH',
        body: { estado: nuevo, observaciones: obs.trim() || null },
      })
      setNuevo('')
      setObs('')
      await cargar()
    } catch (err) {
      setMensaje(err.message)
    } finally {
      setEnviando(false)
    }
  }

  if (!ficha) {
    return (
      <>
        <Link to="/beneficiarios" className="volver">← Beneficiarios</Link>
        {error ? <div className="alerta" role="alert">{error}</div> : <p className="tenue">Cargando…</p>}
      </>
    )
  }

  const barrio = cat?.barrios.find((b) => b.id === ficha.id_barrio)
  const permitidas = TRANSICIONES[ficha.estado || 'aspirante']
  const anios = edad(ficha.fecha_nacimiento)

  return (
    <>
      <Link to="/beneficiarios" className="volver">← Beneficiarios</Link>

      <section className="glass encabezado-ficha">
        <div>
          <h1>{ficha.nombres} {ficha.apellidos}</h1>
          <p className="tenue">{ficha.tipo_identificacion} {ficha.numero_identificacion}</p>
        </div>
        <Estado valor={ficha.estado} />
      </section>

      <div className="ficha-rejilla">
        <section className="glass seccion">
          <h2>Datos personales</h2>
          <div className="datos">
            <Dato etiqueta="Nacimiento" valor={`${fecha(ficha.fecha_nacimiento)}${anios !== null ? ` (${anios} años)` : ''}`} />
            <Dato etiqueta="Grado" valor={ficha.grado} />
            <Dato etiqueta="Institucion" valor={nombreDe(cat?.instituciones, ficha.id_institucion)} />
            <Dato etiqueta="Subgrupo" valor={ficha.subgrupo} />
            <Dato etiqueta="EPS" valor={nombreDe(cat?.eps, ficha.id_eps)} />
            <Dato etiqueta="Religion" valor={nombreDe(cat?.religiones, ficha.id_religion)} />
            <Dato etiqueta="Bautizado" valor={sn(ficha.bautizado)} />
            <Dato etiqueta="Primera comunion" valor={sn(ficha.primera_comunion)} />
          </div>
        </section>

        <section className="glass seccion">
          <h2>Contacto y ubicacion</h2>
          <div className="datos">
            <Dato etiqueta="Telefono" valor={ficha.telefono} />
            <Dato etiqueta="Correo" valor={ficha.correo} />
            <Dato etiqueta="Direccion" valor={ficha.direccion} />
            <Dato
              etiqueta="Barrio"
              valor={barrio ? `${barrio.nombre}${barrio.localidad ? ` · ${barrio.localidad.replaceAll('_', ' ')}` : ''}` : null}
            />
            <Dato etiqueta="Estrato" valor={ficha.estrato_socioeconomico} />
            <Dato etiqueta="Autoriza datos" valor={sn(ficha.autoriza_tratamiento_datos)} />
            <Dato etiqueta="Observaciones" valor={ficha.observaciones} ancho />
          </div>
        </section>

        <section className="glass seccion">
          <h2>Acudientes</h2>
          {acudientes.length === 0 ? (
            <p className="tenue">Sin acudientes vinculados.</p>
          ) : (
            <ul className="lista">
              {acudientes.map((a) => (
                <li key={a.numero_identificacion}>
                  <strong>{a.nombres} {a.apellidos}</strong>
                  <span>{a.vinculo} · {a.tipo_identificacion} {a.numero_identificacion}</span>
                  <span>{[a.telefono, a.correo].filter(Boolean).join(' · ') || 'Sin contacto'}</span>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="glass seccion">
          <h2>Estado y trazabilidad</h2>
          {permitidas.length > 0 ? (
            <form className="cambio" onSubmit={aplicar}>
              <select value={nuevo} onChange={(e) => setNuevo(e.target.value)} required>
                <option value="">Cambiar estado a…</option>
                {permitidas.map((s) => (
                  <option key={s} value={s}>{ETIQUETAS[s]}</option>
                ))}
              </select>
              <input placeholder="Observaciones (opcional)" value={obs} onChange={(e) => setObs(e.target.value)} maxLength={500} />
              <button className="btn" disabled={enviando || !nuevo}>Aplicar</button>
            </form>
          ) : (
            <p className="tenue">Este estado no tiene mas transiciones.</p>
          )}
          {mensaje && <div className="alerta" role="alert">{mensaje}</div>}

          <ul className="linea">
            {historial.map((h, i) => (
              <li key={i}>
                <Estado valor={h.estado} />
                <span className="tenue">{fecha(h.fecha_estado)}</span>
                {h.observaciones && <em>{h.observaciones}</em>}
              </li>
            ))}
            {historial.length === 0 && <li className="tenue">Sin historial de estados.</li>}
          </ul>
        </section>
      </div>
    </>
  )
}
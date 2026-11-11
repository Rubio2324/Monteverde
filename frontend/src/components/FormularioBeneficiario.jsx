import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useCatalogos } from '../catalogos'

const TIPOS = ['TI', 'CC', 'RC', 'CE', 'OTRO']

const VACIO = {
  tipo_identificacion: 'TI',
  numero_identificacion: '',
  nombres: '',
  apellidos: '',
  fecha_nacimiento: '',
  autoriza_tratamiento_datos: false,
  telefono: '',
  correo: '',
  direccion: '',
  id_barrio: '',
  estrato_socioeconomico: '',
  id_eps: '',
  id_religion: '',
  bautizado: '',
  primera_comunion: '',
  id_institucion: '',
  grado: '',
  subgrupo: '',
  observaciones: '',
  foto_url: '',
  boletin_url: '',
}

const aTexto = (v) => (v === null || v === undefined ? '' : String(v))

function desdeFicha(ficha) {
  const f = { ...VACIO }
  for (const k of Object.keys(VACIO)) {
    f[k] = k === 'autoriza_tratamiento_datos' ? !!ficha[k] : aTexto(ficha[k])
  }
  return f
}

const texto = (v) => (v.trim() === '' ? null : v.trim())
const entero = (v) => (v === '' ? null : Number(v))
const logico = (v) => (v === '' ? null : v === 'true')

function armar(f) {
  return {
    tipo_identificacion: f.tipo_identificacion,
    nombres: f.nombres.trim(),
    apellidos: f.apellidos.trim(),
    fecha_nacimiento: f.fecha_nacimiento,
    autoriza_tratamiento_datos: f.autoriza_tratamiento_datos,
    telefono: texto(f.telefono),
    correo: texto(f.correo),
    direccion: texto(f.direccion),
    id_barrio: entero(f.id_barrio),
    estrato_socioeconomico: entero(f.estrato_socioeconomico),
    id_eps: entero(f.id_eps),
    id_religion: entero(f.id_religion),
    id_institucion: entero(f.id_institucion),
    bautizado: logico(f.bautizado),
    primera_comunion: logico(f.primera_comunion),
    grado: texto(f.grado),
    subgrupo: texto(f.subgrupo),
    observaciones: texto(f.observaciones),
    foto_url: texto(f.foto_url),
    boletin_url: texto(f.boletin_url),
  }
}

export default function FormularioBeneficiario({ inicial, modo, onEnviar, cancelarA }) {
  const cat = useCatalogos()
  const editar = modo === 'editar'
  const [f, setF] = useState(inicial ? desdeFicha(inicial) : VACIO)
  const [error, setError] = useState('')
  const [enviando, setEnviando] = useState(false)

  const poner = (k) => (e) => setF({ ...f, [k]: e.target.value })

  async function enviar(e) {
    e.preventDefault()
    setError('')
    setEnviando(true)
    try {
      const cuerpo = armar(f)
      await onEnviar(editar ? cuerpo : { numero_identificacion: f.numero_identificacion.trim(), ...cuerpo })
    } catch (err) {
      setError(err.message)
      setEnviando(false)
    }
  }

  const sino = (k) => (
    <select value={f[k]} onChange={poner(k)}>
      <option value="">Sin dato</option>
      <option value="true">Si</option>
      <option value="false">No</option>
    </select>
  )

  return (
    <form className="glass form-panel" onSubmit={enviar}>
      <h2>Identificacion</h2>
      <div className="form-rejilla">
        <label>
          Tipo de documento
          <select value={f.tipo_identificacion} onChange={poner('tipo_identificacion')}>
            {TIPOS.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
        </label>
        <label>
          Numero de documento
          <input
            value={f.numero_identificacion}
            onChange={poner('numero_identificacion')}
            inputMode="numeric"
            pattern="\d{5,15}"
            title="Entre 5 y 15 digitos"
            disabled={editar}
            required
          />
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
          Fecha de nacimiento
          <input type="date" value={f.fecha_nacimiento} onChange={poner('fecha_nacimiento')} required />
        </label>
        <label className="check campo-ancho">
          <input
            type="checkbox"
            checked={f.autoriza_tratamiento_datos}
            onChange={(e) => setF({ ...f, autoriza_tratamiento_datos: e.target.checked })}
          />
          El titular o su representante legal autoriza el tratamiento de datos personales (Ley 1581 de 2012)
        </label>
      </div>

      <h2>Contacto y ubicacion</h2>
      <div className="form-rejilla">
        <label>
          Telefono
          <input value={f.telefono} onChange={poner('telefono')} maxLength={30} />
        </label>
        <label>
          Correo
          <input type="email" value={f.correo} onChange={poner('correo')} maxLength={150} />
        </label>
        <label>
          Direccion
          <input value={f.direccion} onChange={poner('direccion')} maxLength={200} />
        </label>
        <label>
          Barrio
          <select value={f.id_barrio} onChange={poner('id_barrio')}>
            <option value="">Sin dato</option>
            {cat?.barrios.map((b) => (
              <option key={b.id} value={b.id}>
                {b.nombre}{b.localidad ? ` · ${b.localidad.replaceAll('_', ' ')}` : ''}
              </option>
            ))}
          </select>
        </label>
        <label>
          Estrato
          <input type="number" min="0" max="6" value={f.estrato_socioeconomico} onChange={poner('estrato_socioeconomico')} />
        </label>
        <label>
          EPS
          <select value={f.id_eps} onChange={poner('id_eps')}>
            <option value="">Sin dato</option>
            {cat?.eps.map((x) => <option key={x.id} value={x.id}>{x.nombre}</option>)}
          </select>
        </label>
      </div>

      <h2>Formacion y fe</h2>
      <div className="form-rejilla">
        <label>
          Institucion
          <select value={f.id_institucion} onChange={poner('id_institucion')}>
            <option value="">Sin dato</option>
            {cat?.instituciones.map((x) => <option key={x.id} value={x.id}>{x.nombre}</option>)}
          </select>
        </label>
        <label>
          Grado
          <input value={f.grado} onChange={poner('grado')} maxLength={30} />
        </label>
        <label>
          Subgrupo
          <input value={f.subgrupo} onChange={poner('subgrupo')} maxLength={30} />
        </label>
        <label>
          Religion
          <select value={f.id_religion} onChange={poner('id_religion')}>
            <option value="">Sin dato</option>
            {cat?.religiones.map((x) => <option key={x.id} value={x.id}>{x.nombre}</option>)}
          </select>
        </label>
        <label>
          Bautizado
          {sino('bautizado')}
        </label>
        <label>
          Primera comunion
          {sino('primera_comunion')}
        </label>
      </div>

      <h2>Enlaces y observaciones</h2>
      <div className="form-rejilla">
        <label>
          Foto (enlace de Google Drive)
          <input type="url" value={f.foto_url} onChange={poner('foto_url')} maxLength={500} />
        </label>
        <label>
          Boletin (enlace de Google Drive)
          <input type="url" value={f.boletin_url} onChange={poner('boletin_url')} maxLength={500} />
        </label>
        <label className="campo-ancho">
          Observaciones
          <textarea rows="3" value={f.observaciones} onChange={poner('observaciones')} />
        </label>
      </div>

      {error && <div className="alerta" role="alert">{error}</div>}

      <div className="form-pie">
        <Link to={cancelarA} className="btn-suave">Cancelar</Link>
        <button className="btn" disabled={enviando}>
          {enviando ? 'Guardando…' : editar ? 'Guardar cambios' : 'Registrar beneficiario'}
        </button>
      </div>
    </form>
  )
}
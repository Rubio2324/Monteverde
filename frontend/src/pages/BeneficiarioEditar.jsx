import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { api } from '../api'
import FormularioBeneficiario from '../components/FormularioBeneficiario'

export default function BeneficiarioEditar() {
  const { documento } = useParams()
  const navegar = useNavigate()
  const [ficha, setFicha] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api(`/beneficiarios/${documento}`).then(setFicha).catch((e) => setError(e.message))
  }, [documento])

  async function guardar(cuerpo) {
    await api(`/beneficiarios/${documento}`, { method: 'PATCH', body: cuerpo })
    navegar(`/beneficiarios/${documento}`)
  }

  return (
    <>
      <Link to={`/beneficiarios/${documento}`} className="volver">← Volver a la ficha</Link>
      {error && <div className="alerta" role="alert">{error}</div>}
      {ficha && (
        <>
          <div className="cabecera">
            <div>
              <h1>Editar beneficiario</h1>
              <p>{ficha.nombres} {ficha.apellidos} · {ficha.tipo_identificacion} {ficha.numero_identificacion}</p>
            </div>
          </div>
          <FormularioBeneficiario inicial={ficha} modo="editar" onEnviar={guardar} cancelarA={`/beneficiarios/${documento}`} />
        </>
      )}
    </>
  )
}
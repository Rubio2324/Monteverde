import { Link, useNavigate } from 'react-router-dom'
import { api } from '../api'
import FormularioBeneficiario from '../components/FormularioBeneficiario'

export default function BeneficiarioNuevo() {
  const navegar = useNavigate()

  async function guardar(cuerpo) {
    const ficha = await api('/beneficiarios', { method: 'POST', body: cuerpo })
    navegar(`/beneficiarios/${ficha.numero_identificacion}`)
  }

  return (
    <>
      <Link to="/beneficiarios" className="volver">← Beneficiarios</Link>
      <div className="cabecera">
        <div>
          <h1>Nuevo beneficiario</h1>
          <p>Registro manual. Usa datos reales solo en produccion.</p>
        </div>
      </div>
      <FormularioBeneficiario modo="crear" onEnviar={guardar} cancelarA="/beneficiarios" />
    </>
  )
}
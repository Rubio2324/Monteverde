import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuth } from './auth'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Login from './pages/Login'
import Placeholder from './pages/Placeholder'
import Beneficiarios from './pages/Beneficiarios'
import BeneficiarioFicha from './pages/BeneficiarioFicha'
import BeneficiarioNuevo from './pages/BeneficiarioNuevo'
import BeneficiarioEditar from './pages/BeneficiarioEditar'
import Cursos from './pages/Cursos'
import CursoDetalle from './pages/CursoDetalle'
import CursoEditor from './pages/CursoEditor'

function Protegida({ children }) {
  const { user, cargando } = useAuth()
  if (cargando) return null
  if (!user) return <Navigate to="/login" replace />
  return children
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        element={
          <Protegida>
            <Layout />
          </Protegida>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="beneficiarios" element={<Beneficiarios />} />
        <Route path="beneficiarios/nuevo" element={<BeneficiarioNuevo />} />
        <Route path="beneficiarios/:documento" element={<BeneficiarioFicha />} />
        <Route path="beneficiarios/:documento/editar" element={<BeneficiarioEditar />} />
        <Route path="cursos" element={<Cursos />} />
        <Route path="cursos/nuevo" element={<CursoEditor />} />
        <Route path="cursos/:id" element={<CursoDetalle />} />
        <Route path="cursos/:id/editar" element={<CursoEditor />} />
        <Route path="inscripciones" element={<Placeholder titulo="Inscripciones" />} />
        <Route path="auditoria" element={<Placeholder titulo="Auditoria" />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
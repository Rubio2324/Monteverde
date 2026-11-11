import { NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../auth'
import { modulosDe } from '../modulos'
import { Icono } from './Iconos'

export default function Layout() {
  const { user, salir } = useAuth()
  const modulos = modulosDe(user.roles)

  return (
    <div className="app">
      <header className="barra glass">
        <NavLink to="/" className="marca">
          <span className="marca-punto" />
          Monteverde
        </NavLink>
        <nav className="menu">
          <NavLink to="/" end>
            <Icono nombre="home" /> Inicio
          </NavLink>
          {modulos.map((m) => (
            <NavLink key={m.ruta} to={m.ruta}>
              <Icono nombre={m.icono} /> {m.titulo}
            </NavLink>
          ))}
        </nav>
        <div className="usuario">
          <div className="usuario-datos">
            <strong>{user.nombres}</strong>
            <span>{user.roles.join(' · ')}</span>
          </div>
          <button className="btn-icono" onClick={salir} title="Cerrar sesion">
            <Icono nombre="logout" />
          </button>
        </div>
      </header>
      <main className="contenido">
        <Outlet />
      </main>
    </div>
  )
}
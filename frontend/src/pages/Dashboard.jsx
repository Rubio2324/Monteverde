import { Link } from 'react-router-dom'
import { useAuth } from '../auth'
import { modulosDe } from '../modulos'
import { Icono } from '../components/Iconos'

function saludo() {
  const h = new Date().getHours()
  if (h < 5) return 'Buenas noches'
  if (h < 12) return 'Buenos dias'
  if (h < 19) return 'Buenas tardes'
  return 'Buenas noches'
}

// Reflejo de luz que sigue al cursor (efecto "liquid glass")
function seguirCursor(e) {
  const caja = e.currentTarget.getBoundingClientRect()
  e.currentTarget.style.setProperty('--mx', `${e.clientX - caja.left}px`)
  e.currentTarget.style.setProperty('--my', `${e.clientY - caja.top}px`)
}

export default function Dashboard() {
  const { user } = useAuth()
  const modulos = modulosDe(user.roles)

  return (
    <>
      <section className="bienvenida">
        <h1>
          {saludo()}, {user.nombres.split(' ')[0]}
        </h1>
        <p>¿Que quieres gestionar hoy?</p>
      </section>

      <section className="rejilla">
        {modulos.map((m) => (
          <Link key={m.ruta} to={m.ruta} className="tarjeta glass" onMouseMove={seguirCursor}>
            <span className="tarjeta-icono">
              <Icono nombre={m.icono} />
            </span>
            <h2>{m.titulo}</h2>
            <p>{m.descripcion}</p>
          </Link>
        ))}
      </section>
    </>
  )
}
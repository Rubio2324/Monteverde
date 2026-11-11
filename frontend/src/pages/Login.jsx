import { useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth'

export default function Login() {
  const { user, entrar } = useAuth()
  const navegar = useNavigate()
  const [documento, setDocumento] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [enviando, setEnviando] = useState(false)

  if (user) return <Navigate to="/" replace />

  async function enviar(e) {
    e.preventDefault()
    setError('')
    setEnviando(true)
    try {
      await entrar(documento.trim(), password)
      navegar('/', { replace: true })
    } catch (err) {
      setError(err.message)
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div className="login">
      <form className="glass login-tarjeta" onSubmit={enviar}>
        <div className="marca marca-grande">
          <span className="marca-punto" />
          Monteverde
        </div>
        <p className="sub">Sistema de gestion y control de acceso</p>

        <label>
          Documento
          <input
            value={documento}
            onChange={(e) => setDocumento(e.target.value)}
            inputMode="numeric"
            autoComplete="username"
            autoFocus
            required
          />
        </label>
        <label>
          Contraseña
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
            required
          />
        </label>

        {error && <div className="alerta" role="alert">{error}</div>}

        <button className="btn" disabled={enviando}>
          {enviando ? 'Ingresando…' : 'Ingresar'}
        </button>
      </form>
    </div>
  )
}
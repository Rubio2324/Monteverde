import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import { api, getToken, setToken } from './api'

const Contexto = createContext(null)
export const useAuth = () => useContext(Contexto)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [cargando, setCargando] = useState(!!getToken())

  const salir = useCallback(() => {
    setToken(null)
    setUser(null)
  }, [])

  useEffect(() => {
    if (!getToken()) return
    api('/auth/me')
      .then(setUser)
      .catch(() => setToken(null))
      .finally(() => setCargando(false))
  }, [])

  useEffect(() => {
    window.addEventListener('mv:sesion-expirada', salir)
    return () => window.removeEventListener('mv:sesion-expirada', salir)
  }, [salir])

  async function entrar(documento, password) {
    const t = await api('/auth/login', {
      method: 'POST',
      body: { numero_identificacion: documento, password },
      auth: false,
    })
    setToken(t.access_token)
    const me = await api('/auth/me')
    if (!me.roles.includes('Administrador')) {
      salir()
      throw new Error('Por ahora solo el rol Administrador tiene tablero')
    }
    setUser(me)
  }

  return (
    <Contexto.Provider value={{ user, cargando, entrar, salir }}>
      {children}
    </Contexto.Provider>
  )
}
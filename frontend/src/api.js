const BASE = '/api/v1'
const CLAVE = 'mv_token'

export function getToken() {
  try { return sessionStorage.getItem(CLAVE) } catch { return null }
}

export function setToken(token) {
  try {
    if (token) sessionStorage.setItem(CLAVE, token)
    else sessionStorage.removeItem(CLAVE)
  } catch { /* sin almacenamiento: la sesion dura mientras no se recargue */ }
}

function mensaje(detail, estado) {
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail.map((d) => `${(d.loc || []).slice(1).join('.')}: ${d.msg}`).join(' | ')
  }
  return `Error ${estado}`
}

export async function api(ruta, { method = 'GET', body, auth = true } = {}) {
  const headers = {}
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  const token = getToken()
  if (auth && token) headers.Authorization = `Bearer ${token}`

  let res
  try {
    res = await fetch(BASE + ruta, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    })
  } catch {
    throw new Error('No hay conexion con el servidor')
  }

  if (res.status === 401 && auth) {
    window.dispatchEvent(new Event('mv:sesion-expirada'))
  }
  if (res.status === 204) return null
  const datos = await res.json().catch(() => null)
  if (!res.ok) throw new Error(mensaje(datos?.detail, res.status))
  return datos
}
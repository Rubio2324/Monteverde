import { useEffect, useState } from 'react'
import { api } from './api'

let cache = null

// Catalogos (barrios, EPS, religiones...) cargados una sola vez
export function useCatalogos() {
  const [cat, setCat] = useState(cache)
  useEffect(() => {
    if (cache) return
    api('/catalogos')
      .then((d) => {
        cache = d
        setCat(d)
      })
      .catch(() => {})
  }, [])
  return cat
}

export const nombreDe = (lista, id) =>
  id === null || id === undefined ? null : lista?.find((x) => x.id === id)?.nombre ?? `#${id}`
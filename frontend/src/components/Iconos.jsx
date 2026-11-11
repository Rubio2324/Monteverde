const base = {
  viewBox: '0 0 24 24',
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 1.7,
  strokeLinecap: 'round',
  strokeLinejoin: 'round',
}

const DIBUJOS = {
  home: <path d="M4 11l8-7 8 7v8a1 1 0 0 1-1 1h-4v-6h-6v6H5a1 1 0 0 1-1-1z" />,
  users: (
    <>
      <circle cx="9" cy="8" r="3.2" />
      <path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6" />
      <circle cx="17" cy="9" r="2.4" />
      <path d="M17 14.2c2.4.3 4 2.3 4 4.8" />
    </>
  ),
  book: (
    <>
      <path d="M4 19.5V5a1 1 0 0 1 1-1h14v14H6.5A2.5 2.5 0 0 0 4 20.5" />
      <path d="M8 8h7M8 11.5h5" />
    </>
  ),
  inbox: (
    <>
      <path d="M3 13l2.5-7.5A1 1 0 0 1 6.4 5h11.2a1 1 0 0 1 .9.5L21 13" />
      <path d="M3 13v5a1 1 0 0 0 1 1h16a1 1 0 0 0 1-1v-5h-5.5a2.5 2.5 0 0 1-5 0z" />
    </>
  ),
  shield: (
    <>
      <path d="M12 3l7 3v5.5c0 4.2-2.9 7.6-7 9.5-4.1-1.9-7-5.3-7-9.5V6z" />
      <path d="M9 12l2.2 2.2L15.5 10" />
    </>
  ),
  logout: (
    <>
      <path d="M10 4H6a1 1 0 0 0-1 1v14a1 1 0 0 0 1 1h4" />
      <path d="M15 8l4 4-4 4M19 12H9" />
    </>
  ),
}

export function Icono({ nombre, ...props }) {
  return (
    <svg {...base} {...props} aria-hidden="true">
      {DIBUJOS[nombre]}
    </svg>
  )
}
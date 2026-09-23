/** Turbine mark: same drawing as the dashboard masthead, coloured by currentColor */
export const Mark = () => (
  <svg className="mark-icon" viewBox="0 0 32 32" aria-hidden>
    <circle cx="16" cy="13" r="2.2" />
    <path d="M16 13 L16 2.5 M16 13 L25.2 18.3 M16 13 L6.8 18.3" />
    <path d="M16 15.2 L16 30" className="mast" />
  </svg>
)

/** SAMAL brand bar shared by the landing (overlay on the 3D scene) and the dashboard */
export default function SiteHeader({ href, label, overlay = false }: { href: string; label: string; overlay?: boolean }) {
  return (
    <header className={overlay ? 'site-header overlay' : 'site-header'}>
      <span className="site-logo">
        <Mark />
        SAMAL
      </span>
      <a className="site-nav" href={href}>
        {label}
      </a>
    </header>
  )
}

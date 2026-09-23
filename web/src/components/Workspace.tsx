import { useEffect, useState, type ReactNode } from 'react'

/** Media-query hook for the workspace breakpoints (narrow = docks overlay, mobile = one panel at a time). */
export function useMedia(query: string) {
  const [match, setMatch] = useState(() => window.matchMedia(query).matches)
  useEffect(() => {
    const mq = window.matchMedia(query)
    const on = () => setMatch(mq.matches)
    on()
    mq.addEventListener('change', on)
    return () => mq.removeEventListener('change', on)
  }, [query])
  return match
}

/** Per-viewer UI memory (active section); storage may be unavailable — then it is per-page only. */
export function usePersisted<T extends string>(key: string, initial: T, allowed: readonly T[]) {
  const [v, setV] = useState<T>(() => {
    try {
      const s = localStorage.getItem(key) as T | null
      return s && allowed.includes(s) ? s : initial
    } catch {
      return initial
    }
  })
  useEffect(() => {
    try {
      localStorage.setItem(key, v)
    } catch {
      /* ignore */
    }
  }, [key, v])
  return [v, setV] as const
}

const P = { fill: 'none', stroke: 'currentColor', strokeWidth: 1.7, strokeLinecap: 'round', strokeLinejoin: 'round' } as const
export const Icon = {
  forecast: (
    <svg viewBox="0 0 24 24" aria-hidden {...P}>
      <path d="M3 3v18h18" />
      <path d="M7 15l3.5-4 3 2.5L20 6" />
    </svg>
  ),
  table: (
    <svg viewBox="0 0 24 24" aria-hidden {...P}>
      <rect x="3.5" y="4" width="17" height="16" rx="2" />
      <path d="M3.5 9.5h17M3.5 14.5h17M10 9.5V20" />
    </svg>
  ),
  replay: (
    <svg viewBox="0 0 24 24" aria-hidden {...P}>
      <rect x="3.5" y="5" width="17" height="15" rx="2" />
      <path d="M3.5 9.5h17M8 3v4M16 3v4" />
      <path d="M8 13.5h.01M12 13.5h.01M16 13.5h.01M8 16.5h.01M12 16.5h.01" strokeWidth={2.4} />
    </svg>
  ),
  quality: (
    <svg viewBox="0 0 24 24" aria-hidden {...P}>
      <circle cx="12" cy="12" r="8.5" />
      <circle cx="12" cy="12" r="4.5" />
      <circle cx="12" cy="12" r="0.8" fill="currentColor" />
    </svg>
  ),
  params: (
    <svg viewBox="0 0 24 24" aria-hidden {...P}>
      <path d="M4 7h9M17 7h3M4 17h3M11 17h9" />
      <circle cx="15" cy="7" r="2" />
      <circle cx="9" cy="17" r="2" />
    </svg>
  ),
  agent: (
    <svg viewBox="0 0 24 24" aria-hidden {...P}>
      <path d="M3 12h4l2.5-6 5 12 2.5-6h4" />
    </svg>
  ),
  collapseLeft: (
    <svg viewBox="0 0 24 24" aria-hidden {...P}>
      <path d="M14 7l-5 5 5 5" />
    </svg>
  ),
  collapseRight: (
    <svg viewBox="0 0 24 24" aria-hidden {...P}>
      <path d="M10 7l5 5-5 5" />
    </svg>
  ),
}

export interface RailItem<K extends string> {
  key: K
  label: string
  icon: ReactNode
  hint?: string
  /** small status marker: 'busy' spinner, 'ready' dot, or a count */
  badge?: 'busy' | 'ready' | number | null
}

/** Section navigation: vertical rail on desktop, horizontal tab bar on phones. */
export function Rail<K extends string>({
  items,
  active,
  onSelect,
  tools,
}: {
  items: RailItem<K>[]
  active: K
  onSelect: (k: K) => void
  tools?: ReactNode
}) {
  return (
    <nav className="rail" aria-label="Разделы дашборда">
      <ul>
        {items.map((it) => (
          <li key={it.key}>
            <button
              type="button"
              className="rail-btn"
              aria-current={active === it.key ? 'page' : undefined}
              onClick={() => onSelect(it.key)}
              title={it.hint ? `${it.label} · ${it.hint}` : it.label}
            >
              <span className="rail-ico">
                {it.icon}
                {it.badge === 'busy' && <i className="rail-badge busy" aria-label="идёт расчёт" />}
                {it.badge === 'ready' && <i className="rail-badge ready" aria-label="есть данные" />}
                {typeof it.badge === 'number' && it.badge > 0 && <i className="rail-badge count">{it.badge}</i>}
              </span>
              <span className="rail-label">{it.label}</span>
            </button>
          </li>
        ))}
      </ul>
      {tools && <div className="rail-tools">{tools}</div>}
    </nav>
  )
}

/**
 * Docked side panel. Expanded: header (title or tabs) + scrollable body + optional sticky footer.
 * Collapsed: a thin strip with a vertical label that re-opens it. Content stays mounted either way.
 */
export function Dock({
  id,
  side,
  title,
  icon,
  open,
  hidden = false,
  collapsible = true,
  onToggle,
  head,
  footer,
  children,
}: {
  id: string
  side: 'left' | 'right'
  title: string
  icon: ReactNode
  open: boolean
  /** phones: only the dock chosen in the tab bar is shown */
  hidden?: boolean
  collapsible?: boolean
  onToggle: () => void
  head?: ReactNode
  footer?: ReactNode
  children: ReactNode
}) {
  return (
    <aside id={id} className={`dock dock-${side}`} data-open={open} aria-label={title} hidden={hidden}>
      {!open && (
        <button type="button" className="dock-strip" onClick={onToggle} aria-expanded={false} aria-controls={`${id}-body`} title={`Развернуть: ${title}`}>
          <span className="rail-ico">{icon}</span>
          <span className="dock-strip-label">{title}</span>
        </button>
      )}
      <div className="dock-inner" hidden={!open}>
        <div className="panel-head">
          {head ?? <h2 className="panel-title">{title}</h2>}
          {collapsible && (
            <button type="button" className="icon-btn" onClick={onToggle} aria-expanded aria-controls={`${id}-body`} title={`Свернуть: ${title}`}>
              {side === 'left' ? Icon.collapseLeft : Icon.collapseRight}
            </button>
          )}
        </div>
        <div className="panel-body" id={`${id}-body`}>
          {children}
        </div>
        {footer && <div className="panel-foot">{footer}</div>}
      </div>
    </aside>
  )
}

/** Header tabs for a dock (e.g. Агент / Происхождение / Запуски). */
export function DockTabs<K extends string>({
  label,
  tabs,
  active,
  onSelect,
}: {
  label: string
  tabs: { key: K; label: string; count?: number }[]
  active: K
  onSelect: (k: K) => void
}) {
  return (
    <div className="dock-tabs" role="tablist" aria-label={label}>
      {tabs.map((t) => (
        <button key={t.key} type="button" role="tab" aria-selected={active === t.key} onClick={() => onSelect(t.key)}>
          {t.label}
          {t.count != null && t.count > 0 && <i className="tab-count">{t.count}</i>}
        </button>
      ))}
    </div>
  )
}

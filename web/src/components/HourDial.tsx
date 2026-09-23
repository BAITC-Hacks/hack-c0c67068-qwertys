import { useRef, type KeyboardEvent, type PointerEvent } from 'react'

// Approximate daylight at Shelek in winter, UTC+5 (from the design handoff); decoration only.
const RISE = 7.1
const SET = 16.7
const isNight = (h: number) => h < RISE || h > SET
const hh = (h: number) => String(h).padStart(2, '0')

/** 24-hour clock position: 00 at the top, 12 at the bottom. */
function polar(h: number, r: number) {
  const a = (h / 24) * 2 * Math.PI
  return [50 + r * Math.sin(a), 50 - r * Math.cos(a)] as const
}

/** Issue hour picker from dashboard variant 2e: draggable 24 h dial plus a 24-cell strip. */
export function HourDial({ hour, onChange }: { hour: number; onChange: (h: number) => void }) {
  const dragging = useRef(false)

  const pick = (e: PointerEvent<SVGSVGElement>) => {
    const r = e.currentTarget.getBoundingClientRect()
    const a = Math.atan2(e.clientX - (r.left + r.width / 2), -(e.clientY - (r.top + r.height / 2)))
    const h = Math.round(((a + 2 * Math.PI) % (2 * Math.PI)) / ((2 * Math.PI) / 24)) % 24
    if (h !== hour) onChange(h)
  }
  const onKey = (e: KeyboardEvent) => {
    const step = { ArrowUp: 1, ArrowRight: 1, ArrowDown: -1, ArrowLeft: -1 }[e.key]
    if (step === undefined) return
    e.preventDefault()
    onChange((hour + step + 24) % 24)
  }

  const [s0x, s0y] = polar(SET, 44)
  const [s1x, s1y] = polar(RISE, 44)
  const [kx, ky] = polar(hour, 34)

  return (
    <section className="card dial-card" aria-labelledby="hour-h">
      <h2 id="hour-h">
        Час выпуска <small>{hh(hour)}:00 UTC+5</small>
      </h2>
      <div className="dial-row">
        <svg
          className="dial"
          viewBox="0 0 100 100"
          role="slider"
          tabIndex={0}
          aria-label="Час выпуска, UTC+5"
          aria-valuemin={0}
          aria-valuemax={23}
          aria-valuenow={hour}
          aria-valuetext={`${hh(hour)}:00`}
          onKeyDown={onKey}
          onPointerDown={(e) => {
            dragging.current = true
            e.currentTarget.setPointerCapture(e.pointerId)
            pick(e)
          }}
          onPointerMove={(e) => dragging.current && pick(e)}
          onPointerUp={() => (dragging.current = false)}
          onPointerCancel={() => (dragging.current = false)}
        >
          <circle className="dial-face" cx="50" cy="50" r="47" />
          <path className="dial-night" d={`M ${s0x} ${s0y} A 44 44 0 1 1 ${s1x} ${s1y}`} />
          {Array.from({ length: 24 }, (_, h) => {
            const big = h % 6 === 0
            const [x1, y1] = polar(h, big ? 38 : 41)
            const [x2, y2] = polar(h, 45)
            return <line key={h} className={big ? 'dial-tick big' : 'dial-tick'} x1={x1} y1={y1} x2={x2} y2={y2} />
          })}
          {[0, 6, 12, 18].map((h) => {
            const [x, y] = polar(h, 29)
            return (
              <text key={h} className="dial-num" x={x} y={y} textAnchor="middle" dominantBaseline="central">
                {hh(h)}
              </text>
            )
          })}
          <line className="dial-hand" x1="50" y1="50" x2={kx} y2={ky} />
          <circle className="dial-hub" cx="50" cy="50" r="2.5" />
        </svg>
        <p className="dial-note">
          <span>24-часовой циферблат</span>
          <span>00 сверху, 12 снизу</span>
          <span>серым — ночь (≈ зима)</span>
        </p>
      </div>
      <div className="hour-strip" role="group" aria-label="Выбор часа">
        {Array.from({ length: 24 }, (_, h) => (
          <button
            key={h}
            type="button"
            className={isNight(h) ? 'night' : undefined}
            aria-pressed={h === hour}
            aria-label={`${hh(h)}:00`}
            title={`${hh(h)}:00`}
            onClick={() => onChange(h)}
          />
        ))}
      </div>
    </section>
  )
}

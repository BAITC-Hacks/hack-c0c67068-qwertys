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

/**
 * Issue hour from dashboard variant 2e, display-only: the prepared weather cache supports a single
 * daily origin (17:00 UTC+5 = 12:00 UTC), so the dial shows it instead of offering arbitrary hours.
 */
export function HourDial({ hour }: { hour: number }) {
  const [s0x, s0y] = polar(SET, 44)
  const [s1x, s1y] = polar(RISE, 44)
  const [kx, ky] = polar(hour, 34)
  const utc = (hour - 5 + 24) % 24

  return (
    <section className="card dial-card" aria-labelledby="hour-h" aria-describedby="origin-support">
      <h2 id="hour-h">
        Час выпуска <small>{hh(hour)}:00 · {hh(utc)}:00 UTC</small>
      </h2>
      <div className="dial-row">
        <svg className="dial" viewBox="0 0 100 100" role="img" aria-label={`Час выпуска фиксирован: ${hh(hour)}:00 UTC+5`}>
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
          <b>Выпуск фиксирован</b>
          <span>
            {hh(hour)}:00 UTC+5 ({hh(utc)}:00 UTC)
          </span>
          <span>серым — ночь</span>
        </p>
      </div>
      <div className="hour-strip" aria-hidden>
        {Array.from({ length: 24 }, (_, h) => (
          <i key={h} className={[isNight(h) && 'night', h === hour && 'on'].filter(Boolean).join(' ') || undefined} />
        ))}
      </div>
      <p id="origin-support" className="muted dial-support">
        Подготовленный погодный кэш: ежедневный выпуск в 17:00 UTC+5 (12:00 UTC), 31.01–28.02, горизонты 24 и 48 ч. Произвольный
        час не поддерживается. Пересчёт +24 ч и февральский replay сохраняют этот час; переключатель часового пояса меняет только
        отображение.
      </p>
    </section>
  )
}

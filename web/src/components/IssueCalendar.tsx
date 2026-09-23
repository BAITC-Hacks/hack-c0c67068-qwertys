import { useState } from 'react'

const WEEKDAYS = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
const MONTHS = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']

/** Month grid for the issue date (dashboard variant 2e); only dates with a prepared weather cache are enabled. */
export function IssueCalendar({ value, dates, onChange }: { value: string; dates: string[]; onChange: (iso: string) => void }) {
  const months = [...new Set(dates.map((d) => d.slice(0, 7)))]
  const [month, setMonth] = useState(value.slice(0, 7))
  // follow external date changes (opened run, deep link) without an effect
  const [seen, setSeen] = useState(value)
  if (seen !== value) {
    setSeen(value)
    setMonth(value.slice(0, 7))
  }

  const allowed = new Set(dates)
  const idx = months.indexOf(month)
  const [y, m] = month.split('-').map(Number)
  const lead = (new Date(Date.UTC(y, m - 1, 1)).getUTCDay() + 6) % 7 // Monday-first
  const days = new Date(Date.UTC(y, m, 0)).getUTCDate()

  return (
    <section className="card cal" aria-labelledby="cal-h">
      <h2 id="cal-h">Дата выпуска</h2>
      <div className="cal-nav">
        <button type="button" className="btn icon" aria-label="Предыдущий месяц" disabled={idx <= 0} onClick={() => setMonth(months[idx - 1])}>
          ‹
        </button>
        <b>
          {MONTHS[m - 1]} {y}
        </b>
        <button type="button" className="btn icon" aria-label="Следующий месяц" disabled={idx < 0 || idx >= months.length - 1} onClick={() => setMonth(months[idx + 1])}>
          ›
        </button>
      </div>
      <div className="cal-grid">
        {WEEKDAYS.map((w) => (
          <span key={w} className="cal-wd" aria-hidden>
            {w}
          </span>
        ))}
        {Array.from({ length: lead }, (_, i) => (
          <span key={`pad${i}`} />
        ))}
        {Array.from({ length: days }, (_, i) => {
          const iso = `${month}-${String(i + 1).padStart(2, '0')}`
          return (
            <button
              key={iso}
              type="button"
              disabled={!allowed.has(iso)}
              aria-pressed={iso === value}
              aria-label={`${i + 1} ${MONTHS[m - 1].toLowerCase()} ${y}`}
              onClick={() => onChange(iso)}
            >
              {i + 1}
            </button>
          )
        })}
      </div>
    </section>
  )
}

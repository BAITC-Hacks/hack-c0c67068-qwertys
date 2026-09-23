import { useEffect, useRef, useState } from 'react'
import './landing.css'

const STEPS = [
  { title: 'Погода', text: 'Берёт прогон ECMWF IFS, доступный к моменту выпуска по правилу «прогон + 9 ч» (допущение)' },
  { title: 'Подготовка', text: 'Собирает почасовые входы на 24 или 48 часов вперёд' },
  { title: 'Модель', text: 'V1: кривая «прогноз ветра → мощность» для каждой турбины' },
  { title: 'Анализ', text: 'Проверяет время выпуска, горизонт, дубли и пропуски' },
  { title: 'Экспорт', text: 'Таблица, журнал действий агента и CSV для диспетчера' },
]

/** Hero: variant 3a from design_handoff_wind_landing — full-screen 3D scene, nothing on top by design. */
function Hero() {
  const stageRef = useRef<HTMLDivElement>(null)
  const fadeRef = useRef<HTMLDivElement>(null)
  const [failed, setFailed] = useState(false)

  useEffect(() => {
    let disposed = false
    let dispose = () => {}
    // three.js is loaded only here, so the dashboard bundle stays free of it
    import('./three/scene3d')
      .then(({ createScene }) => {
        if (disposed || !stageRef.current) return
        const scene = createScene(stageRef.current, {
          windAngle: 0.85,
          fov: 34,
          target: [0, 5.5, -10],
          sweep: { r: 48, h: 2.5, a0: -0.42, a1: 0.42, dur: 36 },
          still: matchMedia('(prefers-reduced-motion: reduce)').matches,
          fade: fadeRef.current,
        })
        // 17.01.2026 14:00 UTC+5 as in the handoff; 7.9 m/s is the prototype's animation-only
        // estimate (generic power curve inverted from the January backtest), not a measurement
        scene.set({ ws: 7.9, hour: 14 })
        dispose = scene.dispose
      })
      .catch((e) => {
        console.warn('3D scene unavailable', e)
        if (!disposed) setFailed(true)
      })
    return () => {
      disposed = true
      dispose()
    }
  }, [])

  return (
    <section className={`hero${failed ? ' no-webgl' : ''}`} role="img" aria-label="Low-poly ветропарк в степи, над ним дует ветер">
      <div ref={stageRef} className="hero-stage" />
      <div ref={fadeRef} className="hero-fade" />
    </section>
  )
}

export default function Landing() {
  return (
    <main className="landing">
      <Hero />
      <section className="lp">
        <p className="lp-eyebrow">
          <svg className="lp-mark" viewBox="0 0 32 32" aria-hidden>
            <circle cx="16" cy="13" r="2.2" />
            <path d="M16 13 L16 2.5 M16 13 L25.2 18.3 M16 13 L6.8 18.3" />
            <path d="M16 15.2 L16 30" className="mast" />
          </svg>
          Шелекский коридор · HackAlem AI 2026 · QwertyS
        </p>
        <h1>Почасовой прогноз выработки двух ветротурбин на 24–48 часов</h1>
        <p className="lp-lead">
          Агент берёт архивный прогноз погоды, который по правилу доступности вышел до момента выпуска, рассчитывает мощность и
          проверяет результат. Диспетчер получает таблицу, журнал действий и CSV.
        </p>
        <div className="lp-cta">
          <a className="btn primary lp-go" href="#/dashboard">
            Открыть дашборд <span aria-hidden>→</span>
          </a>
          <span className="lp-note">первый сценарий: 31.01.2026, 17:00 UTC+5, 48 ч</span>
        </div>

        <ol className="lp-steps" aria-label="Этапы агента">
          {STEPS.map((s) => (
            <li key={s.title}>
              <b>{s.title}</b>
              <span>{s.text}</span>
            </li>
          ))}
        </ol>

        <dl className="lp-facts">
          <div>
            <dt>турбины</dt>
            <dd>
              <span className="lp-site"><i className="pin t1" aria-hidden />Т1 43.6452° N 78.5356° E</span>
              <span className="lp-site"><i className="pin t2" aria-hidden />Т2 43.6432° N 78.5388° E</span>
            </dd>
          </div>
          <div>
            <dt>единицы</dt>
            <dd>нормализованная мощность 0…1, не МВт</dd>
          </div>
          <div>
            <dt>проверка на январе 2026</dt>
            <dd>
              MAE <b>0,190</b> · RMSE <b>0,243</b> (обе турбины)
            </dd>
          </div>
          <div>
            <dt>допущения</dt>
            <dd>время публикации погоды и часовой пояс SCADA (UTC+6); для февраля 2026 факта нет — точность не измерена</dd>
          </div>
        </dl>

        <footer className="lp-foot">
          <span>QwertyS · HackAlem AI 2026</span>
          <a href="#/dashboard">Дашборд диспетчера →</a>
        </footer>
      </section>
    </main>
  )
}

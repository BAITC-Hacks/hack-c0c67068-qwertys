import { useEffect, useRef, useState } from 'react'
import SiteHeader, { Mark } from './components/SiteHeader'
import './landing.css'

const STEPS = [
  { title: 'Weather', text: 'Picks the ECMWF IFS run available at issue time under the “run + 9 h” rule (an assumption)' },
  { title: 'Preparation', text: 'Builds hourly inputs 24 or 48 hours ahead' },
  { title: 'Model', text: 'V1: a “wind forecast → power” curve for each turbine' },
  { title: 'Analysis', text: 'Checks issue time, horizon, duplicates and gaps' },
  { title: 'Export', text: 'Table, agent action log and CSV for the dispatcher' },
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
          target: [0, 8, -10],
          sweep: { r: 48, h: 0.5, a0: -0.42, a1: 0.42, dur: 36 }, // near-level gaze: more sunset sky
          still: matchMedia('(prefers-reduced-motion: reduce)').matches,
          fade: fadeRef.current,
          hour: 15.94, // January sunset: only the top of the sun peeks over the far ridge, UTC+5 (decorative)
          sunAz: [-2.3, 0.35], // sun sets just right of the view centre
        })
        // 7.9 m/s is the prototype's animation-only estimate for 17.01.2026 14:00
        // (generic power curve inverted from the January backtest), not a measurement
        scene.set({ ws: 7.9 })
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
    <section className={`hero${failed ? ' no-webgl' : ''}`}>
      <div ref={stageRef} className="hero-stage" role="img" aria-label="Low-poly wind farm on the steppe, wind blowing across it" />
      <div ref={fadeRef} className="hero-fade" />
      <h1 className="hero-title">SAMAL</h1>
      <SiteHeader overlay href="#/dashboard" label="Dashboard" />
    </section>
  )
}

export default function Landing() {
  useEffect(() => {
    const prev = document.title
    document.title = 'SAMAL · wind power forecast'
    return () => {
      document.title = prev
    }
  }, [])

  return (
    <main className="landing" lang="en">
      <Hero />
      <section className="lp">
        <p className="lp-eyebrow">
          <Mark />
          Shelek corridor · HackAlem AI 2026 · QwertyS
        </p>
        <h2>Hourly power forecast for two wind turbines, 24–48 hours ahead</h2>
        <p className="lp-lead">
          The agent takes an archived weather forecast that, under the availability rule, was published before the issue time,
          computes power output and validates the result. The dispatcher gets a table, an action log and a CSV.
        </p>
        <div className="lp-cta">
          <a className="btn primary lp-go" href="#/dashboard">
            Open dashboard <span aria-hidden>→</span>
          </a>
          <span className="lp-note">first run: 31.01.2026, 17:00 UTC+5, 48 h</span>
        </div>

        <ol className="lp-steps" aria-label="Agent stages">
          {STEPS.map((s) => (
            <li key={s.title}>
              <b>{s.title}</b>
              <span>{s.text}</span>
            </li>
          ))}
        </ol>

        <dl className="lp-facts">
          <div>
            <dt>turbines</dt>
            <dd>
              <span className="lp-site"><i className="pin t1" aria-hidden />T1 43.6452° N 78.5356° E</span>
              <span className="lp-site"><i className="pin t2" aria-hidden />T2 43.6432° N 78.5388° E</span>
            </dd>
          </div>
          <div>
            <dt>units</dt>
            <dd>normalized power 0…1, not MW</dd>
          </div>
          <div>
            <dt>January 2026 check</dt>
            <dd>
              MAE <b>0.190</b> · RMSE <b>0.243</b> (both turbines)
            </dd>
          </div>
          <div>
            <dt>assumptions</dt>
            <dd>weather publication time and SCADA time zone (UTC+6); no actuals for February 2026, so its accuracy is not measured</dd>
          </div>
        </dl>

        <footer className="lp-foot">
          <span>QwertyS · HackAlem AI 2026</span>
          <a href="#/dashboard">Dispatcher dashboard →</a>
        </footer>
      </section>
    </main>
  )
}

import { StrictMode, useEffect, useSyncExternalStore } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import Landing from './Landing.tsx'
import SiteHeader from './components/SiteHeader.tsx'

// Hash routes work unchanged when FastAPI serves web/dist: #/ landing, #/dashboard dispatcher console.
// Older evidence links (?run=…, ?replay=…) without a hash still open the dashboard directly.
const onHash = (cb: () => void) => {
  window.addEventListener('hashchange', cb)
  return () => window.removeEventListener('hashchange', cb)
}
const isDashboard = () => {
  const { hash, search } = window.location
  return hash === '#/dashboard' || (hash === '' && /[?&](run|compare|tz|replay)=/.test(search))
}

function Root() {
  const dashboard = useSyncExternalStore(onHash, isDashboard)
  useEffect(() => {
    window.scrollTo(0, 0)
  }, [dashboard])
  return dashboard ? (
    <>
      <SiteHeader href="#/" label="Главная" />
      <App />
    </>
  ) : (
    <Landing />
  )
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Root />
  </StrictMode>,
)

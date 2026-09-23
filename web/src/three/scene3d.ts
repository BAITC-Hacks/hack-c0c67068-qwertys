// Low-poly wind-farm hero scene (three.js), ported from design_handoff_wind_landing/scene3d.js.
// Only the approved variant 3a is kept: `landscape` mode with a slow camera arc (no orbit controls).
// Random calls keep the prototype's order, so the seeded layout matches the design exactly.
import * as THREE from 'three'

type Vec3 = [number, number, number]

export interface SceneState {
  /** wind speed, m/s — drives rotors, streaks and clouds (animation only) */
  ws: number
  /** local hour UTC+5, 0–23 — drives sun, sky and night beacons */
  hour: number
  /** optional per-turbine power 0..1; overrides the ws-based rotor speed */
  p: (number | null | undefined)[]
}

export interface SceneOptions {
  windAngle?: number
  fov?: number
  target?: Vec3
  /** camera arc: radius, height over target, azimuth a0→a1 (rad), duration (s) with ease-in-out */
  sweep?: { r: number; h: number; a0: number; a1: number; dur: number }
  /** prefers-reduced-motion: fixed camera, fewer wind streaks */
  still?: boolean
  /** overlay faded in at the seam of the camera loop */
  fade?: HTMLElement | null
  /** sun azimuth at sunrise and sunset, rad (0 = straight ahead of the camera, + = right) */
  sunAz?: [number, number]
  /** starting local hour (UTC+5), so the first frame is already lit for it */
  hour?: number
  seed?: number
}

export interface WindScene {
  set(o: Partial<SceneState>): void
  dispose(): void
}

const COLORS = new Map<string, THREE.Color>()
/** cached, never mutated: callers copy() or read only */
const C = (h: string) => {
  let c = COLORS.get(h)
  if (!c) COLORS.set(h, (c = new THREE.Color(h)))
  return c
}
const lerp = (a: number, b: number, t: number) => a + (b - a) * t
const clamp = (v: number, a: number, b: number) => Math.max(a, Math.min(b, v))
function rng(seed: number) {
  let x = seed
  return () => {
    x = (x * 16807) % 2147483647
    return (x - 1) / 2147483646
  }
}
function noise(x: number, z: number) {
  return Math.sin(x * 0.12) * 1.3 + Math.cos(z * 0.15 + x * 0.04) * 1.1 + Math.sin((x + z) * 0.07) * 1.9 + Math.sin(x * 0.41 + z * 0.33) * 0.3
}
/** terrain height: steppe hills rising toward the horizon and the sides */
const H = (x: number, z: number) => noise(x, z) * 1.6 + Math.max(0, -z - 45) * 0.32 + Math.max(0, Math.abs(x) - 70) * 0.2

const SKY_VS = `varying vec3 vW; void main(){ vW = normalize(position); gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); }`
const SKY_FS = `varying vec3 vW; uniform vec3 top; uniform vec3 mid; uniform vec3 horizon; uniform vec3 bottom; uniform vec3 sunDir; uniform vec3 sunColor; uniform float sunAmt; uniform float glow; uniform vec3 moonDir; uniform float moonAmt;
void main(){ vec3 d = normalize(vW); float h = d.y; vec3 c = h > 0. ? mix(mix(horizon, mid, smoothstep(.08, .2, h)), top, smoothstep(.13, .36, h)) : mix(horizon, bottom, smoothstep(0., -.25, h));
  float s = max(dot(d, sunDir), 0.); c += sunColor * (smoothstep(.9990, .9995, s) * 1.6 + pow(s, 12.) * .35 + pow(s, 3.) * .08) * sunAmt;
  c += sunColor * glow * pow(s, 8.) * exp(-abs(h) * 6.) * .3; // low-sun halo hugging the horizon
  float m = max(dot(d, moonDir), 0.); c += vec3(.86,.9,1.) * (smoothstep(.99955, .9997, m) * 1.2 + pow(m, 60.) * .12) * moonAmt;
  gl_FragColor = vec4(c, 1.); }`

interface TurbineData {
  rotor: THREE.Group
  beacon: THREE.Mesh
  angle: number
  speed: number
}

function makeTurbine(mat: THREE.Material, bladeGeo: THREE.BufferGeometry) {
  const g = new THREE.Group()
  const add = (geo: THREE.BufferGeometry, x: number, y: number, z: number, parent: THREE.Object3D = g) => {
    const mesh = new THREE.Mesh(geo, mat)
    mesh.position.set(x, y, z)
    mesh.castShadow = mesh.receiveShadow = true
    parent.add(mesh)
    return mesh
  }
  add(new THREE.CylinderGeometry(0.09, 0.22, 7, 8), 0, 3.5, 0)
  add(new THREE.BoxGeometry(0.34, 0.32, 0.9), 0, 7.12, -0.12)
  const rotor = new THREE.Group()
  rotor.position.set(0, 7.12, 0.38)
  g.add(rotor)
  add(new THREE.ConeGeometry(0.17, 0.38, 8), 0, 0, 0.12, rotor).rotation.x = Math.PI / 2
  for (let k = 0; k < 3; k++) {
    const piv = new THREE.Group()
    piv.rotation.z = (k * Math.PI * 2) / 3
    rotor.add(piv)
    add(bladeGeo, 0, 0, 0, piv).rotation.y = 0.22
  }
  const beacon = new THREE.Mesh(new THREE.SphereGeometry(0.07, 6, 4), new THREE.MeshBasicMaterial({ color: 0xff2a1a, fog: false }))
  beacon.position.set(0, 7.33, -0.2)
  g.add(beacon)
  g.userData = { rotor, beacon, angle: Math.random() * 6, speed: 0 } satisfies TurbineData
  return g
}

/** Mounts its own <canvas> into `host` (a fresh WebGL context per mount); throws if WebGL is unavailable. */
export function createScene(host: HTMLElement, opt: SceneOptions = {}): WindScene {
  const R = rng(opt.seed ?? 11)
  const canvas = document.createElement('canvas')
  host.appendChild(canvas)
  let renderer: THREE.WebGLRenderer
  try {
    renderer = new THREE.WebGLRenderer({ canvas, antialias: true })
  } catch (e) {
    canvas.remove()
    throw e
  }
  renderer.setPixelRatio(Math.min(2, window.devicePixelRatio || 1))
  renderer.shadowMap.enabled = true
  renderer.shadowMap.type = THREE.PCFShadowMap // PCFSoft is deprecated in r184 and falls back to this anyway
  renderer.toneMapping = THREE.ACESFilmicToneMapping
  renderer.outputColorSpace = THREE.SRGBColorSpace
  const scene = new THREE.Scene()
  const camera = new THREE.PerspectiveCamera(opt.fov ?? 34, 1, 0.1, 1200)

  // --- terrain
  const mTurb = new THREE.MeshStandardMaterial({ color: 0xf4f5f2, roughness: 0.55, metalness: 0.05, flatShading: true })
  const plane = new THREE.PlaneGeometry(260, 260, 90, 90)
  plane.rotateX(-Math.PI / 2)
  {
    // colour per shared vertex, interpolated across faces: a smooth height gradient, no per-face noise or spots
    const pal = [C('#4f7a33'), C('#6a9a3e'), C('#8fb152'), C('#b7b866')]
    const p = plane.attributes.position
    const col = new Float32Array(p.count * 3)
    const c = new THREE.Color()
    for (let i = 0; i < p.count; i++) {
      const y = H(p.getX(i), p.getZ(i))
      p.setY(i, y)
      const t = clamp((y + 3) / 9, 0, 1) * (pal.length - 1)
      const k = Math.min(Math.floor(t), pal.length - 2)
      c.copy(pal[k]).lerp(pal[k + 1], t - k).toArray(col, i * 3)
    }
    plane.setAttribute('color', new THREE.BufferAttribute(col, 3))
    plane.computeVertexNormals()
    for (let i = 0; i < 90 * 90 * 4; i++) R() // the old per-face colouring drew 2 randoms per face; keep tree/rock layout unchanged
  }
  const ground = new THREE.Mesh(plane, new THREE.MeshStandardMaterial({ vertexColors: true, flatShading: true, roughness: 1 }))
  ground.receiveShadow = true
  scene.add(ground)

  // --- trees & rocks (shared geometry: every tree is the same cone/trunk, scaled)
  const treeMat = new THREE.MeshStandardMaterial({ color: 0x2f5a2c, flatShading: true, roughness: 1 })
  const treeMat2 = new THREE.MeshStandardMaterial({ color: 0x3f6f33, flatShading: true, roughness: 1 })
  const trunkMat = new THREE.MeshStandardMaterial({ color: 0x5a3f2a, flatShading: true, roughness: 1 })
  const rockMat = new THREE.MeshStandardMaterial({ color: 0x8b8a83, flatShading: true, roughness: 1 })
  const trunkGeo = new THREE.CylinderGeometry(0.06, 0.09, 0.5, 5)
  const coneGeo = new THREE.ConeGeometry(0.55, 1.6, 6)
  for (let i = 0; i < 140; i++) {
    const x = (R() - 0.5) * 220
    const z = -R() * 150 + 30
    const cluster = 1 + Math.floor(R() * 3)
    for (let k = 0; k < cluster; k++) {
      const tx = x + (R() - 0.5) * 2.4
      const tz = z + (R() - 0.5) * 2.4
      const s = 0.5 + R() * 0.8
      const t = new THREE.Group()
      const trunk = new THREE.Mesh(trunkGeo, trunkMat)
      trunk.position.y = 0.25
      const cone = new THREE.Mesh(coneGeo, R() > 0.5 ? treeMat : treeMat2)
      cone.position.y = 1.2
      trunk.castShadow = cone.castShadow = true
      t.add(trunk, cone)
      t.position.set(tx, H(tx, tz), tz)
      t.scale.setScalar(s)
      t.rotation.y = R() * 6
      scene.add(t)
    }
    if (R() < 0.35) {
      const r = new THREE.Mesh(new THREE.DodecahedronGeometry(0.3 + R() * 0.4, 0), rockMat)
      r.position.set(x + 2, H(x + 2, z) + 0.1, z)
      r.castShadow = true
      r.rotation.set(R(), R(), R())
      scene.add(r)
    }
  }

  // --- turbines
  const WA = opt.windAngle ?? 0.6
  const ca = Math.cos(WA)
  const sa = Math.sin(WA)
  const blade = new THREE.Shape()
  blade.moveTo(-0.13, 0.05)
  blade.lineTo(0.15, 0.35)
  blade.lineTo(0.06, 3.3)
  blade.lineTo(-0.02, 3.35)
  blade.lineTo(-0.09, 0.5)
  blade.closePath()
  const bladeGeo = new THREE.ExtrudeGeometry(blade, { depth: 0.035, bevelEnabled: false })
  const tpos: [number, number][] = [[-14, 4], [-3, -2], [9, 3], [20, -6], [-28, -12], [-16, -26], [4, -22], [26, -24], [-40, -40], [-6, -48], [18, -52], [44, -40], [34, -8]]
  const turbines = tpos.map(([x, z]) => {
    const t = makeTurbine(mTurb, bladeGeo)
    t.position.set(x, H(x, z) - 0.1, z)
    t.rotation.y = Math.atan2(-ca, sa) + (R() - 0.5) * 0.1
    scene.add(t)
    return t.userData as TurbineData
  })

  // --- shelterbelts and groves: poplar rows (as along steppe fields) and round trees, instanced;
  // own seed, so the prototype's layout above and below stays as designed
  {
    const R2 = rng(29)
    const clear = (x: number, z: number) => tpos.every(([px, pz]) => Math.hypot(x - px, z - pz) > 4)
    type Tree = [x: number, z: number, scale: number, turn: number]
    const poplars: Tree[] = []
    const rounds: Tree[] = []
    for (let i = 0; i < 14; i++) {
      const x0 = (R2() - 0.5) * 200
      const z0 = -R2() * 125 + 20
      const a = R2() * Math.PI
      const n = 6 + Math.floor(R2() * 8)
      for (let k = 0; k < n; k++) {
        const x = x0 + Math.cos(a) * k * 1.25
        const z = z0 + Math.sin(a) * k * 1.25
        if (clear(x, z)) poplars.push([x, z, 0.8 + R2() * 0.45, R2() * 6])
      }
    }
    for (let i = 0; i < 26; i++) {
      const x0 = (R2() - 0.5) * 210
      const z0 = -R2() * 130 + 25
      const n = 3 + Math.floor(R2() * 5)
      for (let k = 0; k < n; k++) {
        const x = x0 + (R2() - 0.5) * 5
        const z = z0 + (R2() - 0.5) * 5
        if (clear(x, z)) rounds.push([x, z, 0.6 + R2() * 0.5, R2() * 6])
      }
    }
    const poplarGeo = new THREE.IcosahedronGeometry(0.42, 0).scale(1, 3.2, 1).translate(0, 1.75, 0)
    const roundGeo = new THREE.IcosahedronGeometry(0.75, 0).scale(1, 0.85, 1).translate(0, 1.1, 0)
    const stemGeo = trunkGeo.clone().translate(0, 0.25, 0)
    const leaves = ['#4f7d33', '#5f8a38', '#6f963c', '#3f6f33'].map(C)
    const o = new THREE.Object3D()
    const plant = (geo: THREE.BufferGeometry, mat: THREE.Material, pts: Tree[], tint: boolean) => {
      const m = new THREE.InstancedMesh(geo, mat, pts.length)
      pts.forEach(([x, z, s, r], i) => {
        o.position.set(x, H(x, z) - 0.05, z)
        o.rotation.y = r
        o.scale.setScalar(s)
        o.updateMatrix()
        m.setMatrixAt(i, o.matrix)
        if (tint) m.setColorAt(i, leaves[Math.floor(R2() * leaves.length)])
      })
      m.castShadow = true
      scene.add(m)
    }
    const leafMat = new THREE.MeshStandardMaterial({ flatShading: true, roughness: 1 })
    plant(poplarGeo, leafMat, poplars, true)
    plant(roundGeo, leafMat, rounds, true)
    plant(stemGeo, trunkMat, [...poplars, ...rounds], false)
  }

  // --- clouds
  const clouds: THREE.Group[] = []
  const cloudMat = new THREE.MeshStandardMaterial({ color: 0xffffff, flatShading: true, roughness: 1, transparent: true, opacity: 0.95 })
  const SPAN = 240
  for (let i = 0; i < 12; i++) {
    const g = new THREE.Group()
    const k = 3 + Math.floor(R() * 3)
    for (let j = 0; j < k; j++) {
      const m = new THREE.Mesh(new THREE.IcosahedronGeometry(1 + R() * 1.4, 0), cloudMat)
      m.position.set(j * 1.5 - k * 0.7, R() * 0.6, (R() - 0.5) * 1.2)
      m.scale.y = 0.65
      m.castShadow = true
      g.add(m)
    }
    g.position.set((R() - 0.5) * SPAN, 20 + R() * 10, -R() * 120 + 20)
    g.scale.setScalar(1.4 + R())
    scene.add(g)
    clouds.push(g)
  }

  // --- wind streaks (instanced thin sticks, additive, fading at the ends of the volume)
  const NS = opt.still ? 250 : 700
  const box = { cx: 0, cz: -40, L: 100, W: 75, y0: 0.8, y1: 22 }
  const sGeo = new THREE.BoxGeometry(1, 0.018, 0.018)
  sGeo.translate(-0.5, 0, 0)
  const sMat = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.85, blending: THREE.AdditiveBlending, depthWrite: false, fog: true })
  const streaks = new THREE.InstancedMesh(sGeo, sMat, NS)
  streaks.frustumCulled = false
  const S = Array.from({ length: NS }, () => ({
    u: lerp(-box.L, box.L, R()),
    w: lerp(-box.W, box.W, R()),
    y: lerp(box.y0, box.y1, Math.pow(R(), 1.4)),
    v: 0.6 + R() * 0.8,
    l: 0.5 + R(),
    ph: R() * 6.28,
  }))
  const dummy = new THREE.Object3D()
  const white = new THREE.Color()
  for (let i = 0; i < NS; i++) streaks.setColorAt(i, white)
  scene.add(streaks)

  // --- sky, stars, lights
  const skyU = {
    top: { value: C('#3f7fd0').clone() },
    mid: { value: C('#97bfe6').clone() },
    horizon: { value: C('#bfe0f5').clone() },
    bottom: { value: C('#5b6b4b').clone() },
    sunDir: { value: new THREE.Vector3(0, 0.3, -1).normalize() },
    sunColor: { value: C('#fff1dc').clone() },
    sunAmt: { value: 1 },
    glow: { value: 0 },
    moonDir: { value: new THREE.Vector3(0.4, 0.5, -0.7).normalize() },
    moonAmt: { value: 0 },
  }
  const sky = new THREE.Mesh(
    new THREE.SphereGeometry(500, 32, 16),
    new THREE.ShaderMaterial({ uniforms: skyU, vertexShader: SKY_VS, fragmentShader: SKY_FS, side: THREE.BackSide, depthWrite: false, fog: false }),
  )
  sky.renderOrder = -1
  scene.add(sky)
  const starG = new THREE.BufferGeometry()
  {
    const a: number[] = []
    for (let i = 0; i < 1100; i++) {
      const u = R() * 6.28
      const v = 0.06 + R() * 0.94
      const c = Math.sqrt(1 - v * v)
      a.push(Math.cos(u) * c * 480, v * 480, Math.sin(u) * c * 480)
    }
    starG.setAttribute('position', new THREE.Float32BufferAttribute(a, 3))
  }
  const starM = new THREE.PointsMaterial({ color: 0xffffff, size: 1.6, sizeAttenuation: false, transparent: true, opacity: 0, fog: false, depthWrite: false })
  const stars = new THREE.Points(starG, starM)
  scene.add(stars)

  const hemi = new THREE.HemisphereLight(0xbfdcff, 0x5a6b3a, 0.8)
  scene.add(hemi)
  const sun = new THREE.DirectionalLight(0xfff1dc, 2.4)
  sun.castShadow = true
  Object.assign(sun.shadow.camera, { left: -70, right: 70, top: 70, bottom: -70, near: 1, far: 400 })
  sun.shadow.mapSize.set(2048, 2048)
  sun.shadow.bias = -0.0004
  sun.shadow.normalBias = 0.03
  scene.add(sun, sun.target)
  const moon = new THREE.DirectionalLight(0x8fa8ff, 0.3)
  scene.add(moon)
  const fog = new THREE.Fog(0xbfe0f5, 50, 230)
  scene.fog = fog

  // --- camera: slow arc (variant 3a), or fixed at the arc centre for reduced motion
  const target = new THREE.Vector3(...(opt.target ?? [0, 5.5, -10]))
  const sweep = opt.sweep ?? { r: 48, h: 2.5, a0: -0.42, a1: 0.42, dur: 36 }
  let fit = 1 // pull the camera back on portrait screens so the farm stays in frame

  // --- light by hour (Shelek, January, UTC+5)
  const h0 = opt.hour ?? 14
  const st: SceneState & { hCur: number; wsCur: number } = { ws: 6, hour: h0, p: [], hCur: h0, wsCur: 6 }
  const RISE = 7.1
  const SET = 16.7
  const SUN_AZ = opt.sunAz ?? [-1.25, 1.25]
  function sunVec(h: number) {
    const t = (h - RISE) / (SET - RISE)
    let el: number
    let az: number
    if (t >= -0.15 && t <= 1.15) {
      el = Math.sin(clamp(t, -0.15, 1.15) * Math.PI) * 26
      az = lerp(SUN_AZ[0], SUN_AZ[1], t)
    } else {
      el = -18
      az = 0
    }
    const e = (el * Math.PI) / 180
    return { el, v: new THREE.Vector3(Math.sin(az) * Math.cos(e), Math.sin(e), -Math.cos(az) * Math.cos(e)).normalize() }
  }
  function applyLight(h: number) {
    const { el, v } = sunVec(h)
    const day = clamp((el + 2) / 12, 0, 1)
    const tw = clamp(1 - Math.abs(el - 8) / 10, 0, 1) // golden hour: strongest with the sun on the far ridge (~7.5° high)
    const mix3 = (n: string, d: string, t: string, out: THREE.Color) => out.copy(C(n)).lerp(C(d), day).lerp(C(t), tw)
    mix3('#040817', '#3c7ccc', '#9a8fb8', skyU.top.value) // dusty lavender
    mix3('#0a1030', '#97bfe6', '#f0bc98', skyU.mid.value) // soft peach
    mix3('#10183a', '#c9e4f4', '#ffd28e', skyU.horizon.value) // soft gold
    mix3('#05070c', '#6f7d5a', '#4a2f3a', skyU.bottom.value)
    skyU.sunDir.value.copy(v)
    skyU.sunColor.value.copy(C('#ff8f4f')).lerp(C('#fff3dd'), clamp(el / 18, 0, 1) * (1 - tw))
    skyU.sunAmt.value = clamp((el + 4) / 6, 0, 1)
    skyU.glow.value = tw
    cloudMat.emissive.copy(C('#f0a890')).multiplyScalar(tw * 0.2) // clouds catch the warm afterglow
    skyU.moonAmt.value = 1 - day
    // lavender haze: distant ridges read as layers against the gold horizon
    fog.color.copy(skyU.horizon.value).lerp(C('#a07aa8'), tw * 0.8)
    starM.opacity = clamp(1 - day - tw * 0.6, 0, 1)
    sun.color.copy(C('#ff9a5a')).lerp(C('#fff1dc'), clamp(el / 16, 0, 1) * (1 - tw * 0.8))
    sun.intensity = 2.8 * clamp((el + 1) / 8, 0, 1)
    sun.position.copy(target).addScaledVector(v, 120)
    sun.target.position.copy(target)
    moon.position.set(40, 80, -60)
    moon.intensity = 0.45 * (1 - day)
    // dusk fill: lavender sky light keeps the sun-averted slopes violet instead of muddy
    hemi.color.copy(C('#26335e')).lerp(C('#c6e0ff'), day).lerp(C('#a987c9'), tw * 0.8)
    hemi.groundColor.copy(C('#0b0f0a')).lerp(C('#5d6b3a'), day).lerp(C('#7a4a35'), tw * 0.5)
    hemi.intensity = 0.35 + day * 0.75 + tw * 0.2
    renderer.toneMappingExposure = 0.9 + day * 0.15 + (1 - day) * 0.25
    return day
  }

  function resize() {
    const r = host.getBoundingClientRect()
    renderer.setSize(r.width, r.height, false)
    camera.aspect = r.width / Math.max(1, r.height)
    camera.updateProjectionMatrix()
    fit = clamp(1.05 / camera.aspect, 1, 1.6)
  }
  const ro = new ResizeObserver(resize)
  ro.observe(host)
  resize()

  // --- loop (paused while the hero is off screen)
  let raf = 0
  let lastT = performance.now()
  let t = 0
  let fadeOn: boolean | null = null
  function frame() {
    const now = performance.now()
    const dt = Math.min(0.05, (now - lastT) / 1000)
    lastT = now
    t += dt
    const dh = ((st.hour - st.hCur + 36) % 24) - 12
    st.hCur = (st.hCur + dh * Math.min(1, dt * 3) + 24) % 24
    st.wsCur = lerp(st.wsCur, st.ws, Math.min(1, dt * 2))
    const day = applyLight(st.hCur)
    const ws = st.wsCur
    turbines.forEach((u, i) => {
      const p = st.p[i]
      const goal = p != null ? 0.25 + p * 3.2 : ws < 3 ? 0.15 : clamp(0.6 + (ws - 3) * 0.28, 0, 3.4)
      u.speed = lerp(u.speed, goal, Math.min(1, dt * 1.5))
      u.angle += u.speed * dt
      u.rotor.rotation.z = -u.angle
      u.beacon.visible = day < 0.5 && Math.sin(t * 3 + i) > 0.2
    })
    const sp = 2 + ws * 1.9
    const len = 0.5 + ws * 0.32
    const vis = clamp((ws - 1) / 5, 0.12, 1)
    for (let i = 0; i < NS; i++) {
      const s = S[i]
      s.u += sp * s.v * dt
      if (s.u > box.L) {
        s.u = -box.L
        s.w = lerp(-box.W, box.W, R())
      }
      const f = Math.sin((Math.PI * (s.u + box.L)) / (2 * box.L))
      const y = s.y + Math.sin(t * 1.3 + s.ph + s.u * 0.08) * 0.35
      const x = box.cx + s.u * ca + s.w * sa
      const z = box.cz - s.u * sa + s.w * ca
      dummy.position.set(x, y + H(x, z) * 0.8, z)
      dummy.rotation.set(0, WA, Math.sin(t + s.ph) * 0.05)
      dummy.scale.set(len * s.l, 1, 1)
      dummy.updateMatrix()
      streaks.setMatrixAt(i, dummy.matrix)
      const b = f * vis * (0.35 + day * 0.35) * (0.5 + 0.5 * Math.sin(s.ph + t * 0.5))
      streaks.setColorAt(i, white.setRGB(b, b, b))
    }
    streaks.instanceMatrix.needsUpdate = true
    streaks.instanceColor!.needsUpdate = true
    for (const c of clouds) {
      const d = (0.3 + ws * 0.12) * dt
      c.position.x += d * ca
      c.position.z -= d * sa * 0.3
      if (c.position.x > SPAN / 2) c.position.x = -SPAN / 2
    }
    const ph = opt.still ? 0.5 : (t % sweep.dur) / sweep.dur
    const e = ph < 0.5 ? 2 * ph * ph : 1 - Math.pow(-2 * ph + 2, 2) / 2
    const a = lerp(sweep.a0, sweep.a1, e)
    camera.position.set(target.x + Math.sin(a) * sweep.r * fit, target.y + sweep.h, target.z + Math.cos(a) * sweep.r * fit)
    camera.lookAt(target)
    sky.position.copy(camera.position)
    stars.position.copy(camera.position)
    renderer.render(scene, camera)
    const dark = ph > 0.975 || ph < 0.02
    if (opt.fade && dark !== fadeOn) opt.fade.style.opacity = dark ? '1' : '0'
    fadeOn = dark
    raf = requestAnimationFrame(frame)
  }
  const start = () => {
    if (raf) return
    lastT = performance.now()
    raf = requestAnimationFrame(frame)
  }
  const stop = () => {
    cancelAnimationFrame(raf)
    raf = 0
  }
  const io = new IntersectionObserver(([en]) => (en.isIntersecting ? start() : stop()))
  io.observe(host)
  start()

  return {
    set(o) {
      Object.assign(st, o)
    },
    dispose() {
      stop()
      io.disconnect()
      ro.disconnect()
      scene.traverse((o) => {
        const m = o as THREE.Mesh
        m.geometry?.dispose()
        const mats = m.material ? ([] as THREE.Material[]).concat(m.material) : []
        mats.forEach((x) => x.dispose())
      })
      renderer.dispose()
      renderer.forceContextLoss()
      canvas.remove()
    },
  }
}

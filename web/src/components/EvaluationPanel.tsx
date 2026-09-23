import { useState } from 'react'

// Renders C2's history evaluation (coordination/research/C2/evaluation-v*.json) as served by
// GET /api/evaluation. Only numbers present in the file are shown; February has no labels.

interface Metric {
  n: number
  mae: number
  rmse: number
  bias: number
}
type Buckets = Partial<Record<'all_48' | 'hours_1_24' | 'hours_25_48' | 'available_only', Metric>>
interface TurbineEval {
  selected_on_validation?: string
  test?: Record<string, Buckets & { coverage?: number }>
  test_coverage?: { labelled_pairs: number; possible_pairs: number; coverage: number }
  candidate_rmse_delta?: number
}
export interface EvaluationV1 {
  unit?: string
  model_version?: string
  protocol?: string
  target_split?: { train_end_exclusive?: string; validation_end_exclusive?: string; test_end_exclusive?: string }
  turbines?: Record<string, TurbineEval>
  february_metrics?: unknown
  evaluation_fit_end_exclusive?: string
  production_fit_end_exclusive?: string
  estimator_relationship?: string
  experiment_label?: string
  january_test_previously_viewed?: boolean
}

const MODEL_LABEL: Record<string, string> = {
  nwp_curve: 'Кривая мощности по NWP',
  catboost: 'CatBoost',
  persistence: 'Persistence (baseline)',
}
/** Russian rendering of C2's known estimator_relationship text; unknown texts are shown verbatim. */
const RELATION_RU: Record<string, string> = {
  'January metrics belong to estimators fitted only on pre-January targets. model_version identifies final production refit, not the January-test estimator. Same family/configuration, different fitted parameters.':
    'Метрики января получены моделями, обученными только на целях до января. model_version обозначает финальное переобучение для прогнозов, а не январский оценщик: то же семейство и конфигурация, другие обученные параметры.',
}
/** selected_on_validation may name a candidate config (e.g. depth4_full) that is reported under `catboost`. */
const selectedKey = (sel?: string) => (sel && /^depth/.test(sel) ? 'catboost' : sel)
const BUCKET_LABEL: Record<string, string> = { hours_1_24: '1–24 ч', hours_25_48: '25–48 ч', all_48: '1–48 ч', available_only: 'все доступные' }
const TURBINE_RU: Record<string, string> = { turbine_1: 'Турбина 1', turbine_2: 'Турбина 2' }
const d10 = (s?: string) => (s ? s.slice(0, 10) : '?')
const f3 = (v?: number) => (v == null ? '—' : v.toFixed(3))

export function EvaluationPanel({
  evaluation: v1,
  evaluationV2,
  currentModel,
}: {
  evaluation: EvaluationV1 | null
  evaluationV2?: EvaluationV1 | null
  currentModel?: string | null
}) {
  const [tab, setTab] = useState<'v1' | 'v2'>('v1')
  const evaluation = tab === 'v2' && evaluationV2 ? evaluationV2 : v1
  const posttest = evaluation === evaluationV2 && !!evaluationV2
  const turbines = evaluation?.turbines ? Object.entries(evaluation.turbines) : []
  const split = evaluation?.target_split
  return (
    <section className="card" aria-labelledby="eval-h">
      <h2 id="eval-h">
        Качество на истории
        <small>фактических данных за февраль нет — метрик за февраль не бывает</small>
      </h2>
      {v1 && evaluationV2 && (
        <div className="eval-tabs" role="tablist" aria-label="Версия отчёта">
          <button type="button" role="tab" aria-selected={tab === 'v1'} onClick={() => setTab('v1')}>
            v1 · независимая оценка
          </button>
          <button type="button" role="tab" aria-selected={tab === 'v2'} onClick={() => setTab('v2')}>
            v2 · post-test эксперимент
          </button>
        </div>
      )}
      {posttest && (
        <p className="eval-badge">
          Январь уже был открыт до этого эксперимента ({evaluation?.experiment_label ?? 'post-test'}). Эти числа — диагностика, не новая
          независимая проверка и не основание выбирать модель задним числом.
        </p>
      )}
      {!turbines.length ? (
        <p className="unknown">Историческая проверка пока не опубликована backend-ом.</p>
      ) : (
        <>
          <p className="eval-meta">
            Тест: {d10(split?.validation_end_exclusive)} — {d10(split?.test_end_exclusive)}, не использовался для выбора. Выбор модели — на валидации
            (обучение до {d10(split?.train_end_exclusive)}); оценщик для теста обучен на данных до{' '}
            {d10(evaluation?.evaluation_fit_end_exclusive ?? split?.validation_end_exclusive)}.
            {evaluation?.production_fit_end_exclusive && <> Рабочая модель обучена заранее на данных до {d10(evaluation.production_fit_end_exclusive)}.</>} При
            прогнозе загружается заранее обученная модель; шаг prepare проверяет её и временную границу обучения. Версия{' '}
            {evaluation?.model_version ?? '?'} · единица {evaluation?.unit ?? '?'} · bias = прогноз − факт
          </p>
          {currentModel && evaluation?.model_version && currentModel !== evaluation.model_version && (
            <p className="eval-note">
              ⚠ Версия модели текущего прогноза ({currentModel}) не совпадает с версией в отчёте ({evaluation.model_version}). Метрики описывают процедуру
              обучения и отбора, а не напрямую оценку этого экземпляра модели.
            </p>
          )}
          <div className="eval-grid">
            {turbines.map(([tid, t]) => (
              <div key={tid} className="table-scroll">
                <table>
                  <caption className="eval-cap">
                    {TURBINE_RU[tid] ?? tid} · выбрано на валидации: <b>{MODEL_LABEL[selectedKey(t.selected_on_validation) ?? ''] ?? t.selected_on_validation ?? '?'}</b>
                    {t.test_coverage && ` · покрытие ${t.test_coverage.labelled_pairs}/${t.test_coverage.possible_pairs}`}
                  </caption>
                  <thead>
                    <tr>
                      <th scope="col">Модель</th>
                      <th scope="col">Упреждение</th>
                      <th scope="col">MAE</th>
                      <th scope="col">RMSE</th>
                      <th scope="col">bias</th>
                      <th scope="col">n</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(t.test ?? {}).flatMap(([model, buckets]) =>
                      (['hours_1_24', 'hours_25_48', 'available_only'] as const)
                        .filter((b) => buckets[b])
                        .map((b) => {
                          const m = buckets[b] as Metric
                          return (
                            <tr key={model + b} className={model === selectedKey(t.selected_on_validation) ? 'selected' : undefined}>
                              <td>{MODEL_LABEL[model] ?? model}</td>
                              <td>{BUCKET_LABEL[b]}</td>
                              <td>{f3(m.mae)}</td>
                              <td>{f3(m.rmse)}</td>
                              <td>{m.bias >= 0 ? '+' : ''}{f3(m.bias)}</td>
                              <td>{m.n}</td>
                            </tr>
                          )
                        }),
                    )}
                  </tbody>
                </table>
              </div>
            ))}
          </div>
          {evaluation?.estimator_relationship && (
            <p className="eval-meta" title={evaluation.estimator_relationship}>
              {RELATION_RU[evaluation.estimator_relationship.trim()] ?? evaluation.estimator_relationship}
            </p>
          )}
          {evaluation?.protocol && (
            <details className="eval-proto">
              <summary>Протокол оценки</summary>
              <p>{evaluation.protocol}</p>
            </details>
          )}
        </>
      )}
    </section>
  )
}

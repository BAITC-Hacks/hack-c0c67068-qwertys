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
}

const MODEL_LABEL: Record<string, string> = {
  nwp_curve: 'Кривая мощности по NWP',
  catboost: 'CatBoost',
  persistence: 'Persistence (baseline)',
}
const BUCKET_LABEL: Record<string, string> = { hours_1_24: '1–24 ч', hours_25_48: '25–48 ч', all_48: '1–48 ч', available_only: 'все доступные' }
const TURBINE_RU: Record<string, string> = { turbine_1: 'Турбина 1', turbine_2: 'Турбина 2' }
const d10 = (s?: string) => (s ? s.slice(0, 10) : '?')
const f3 = (v?: number) => (v == null ? '—' : v.toFixed(3))

export function EvaluationPanel({ evaluation, currentModel }: { evaluation: EvaluationV1 | null; currentModel?: string | null }) {
  const turbines = evaluation?.turbines ? Object.entries(evaluation.turbines) : []
  const split = evaluation?.target_split
  return (
    <section className="card" aria-labelledby="eval-h">
      <h2 id="eval-h">
        Качество на истории
        <small>фактических данных за февраль нет — метрик за февраль не бывает</small>
      </h2>
      {!turbines.length ? (
        <p className="unknown">Историческая проверка пока не опубликована backend-ом.</p>
      ) : (
        <>
          <p className="eval-meta">
            Тест: {d10(split?.validation_end_exclusive)} — {d10(split?.test_end_exclusive)}, не использовался для выбора. Выбор модели — на валидации
            (обучение до {d10(split?.train_end_exclusive)}); для теста выбранная процедура переобучена на данных до{' '}
            {d10(evaluation?.evaluation_fit_end_exclusive ?? split?.validation_end_exclusive)}; модель для прогнозов переобучена на данных до{' '}
            {evaluation?.production_fit_end_exclusive ? d10(evaluation.production_fit_end_exclusive) : 'момента выпуска (шаг prepare в журнале агента)'}. Версия{' '}
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
                    {TURBINE_RU[tid] ?? tid} · выбрано на валидации: <b>{MODEL_LABEL[t.selected_on_validation ?? ''] ?? t.selected_on_validation ?? '?'}</b>
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
                            <tr key={model + b} className={model === t.selected_on_validation ? 'selected' : undefined}>
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
          {evaluation?.estimator_relationship && <p className="eval-meta">{evaluation.estimator_relationship}</p>}
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

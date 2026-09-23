import type { Evaluation } from '../api/types'

export function EvaluationPanel({ evaluation }: { evaluation: Evaluation | null }) {
  return (
    <section className="card" aria-labelledby="eval-h">
      <h2 id="eval-h">
        Качество на истории
        <small>фактических данных за февраль нет — метрик за февраль не бывает</small>
      </h2>
      {!evaluation ? (
        <p className="unknown">Историческая проверка пока не опубликована backend-ом.</p>
      ) : (
        <>
          <p style={{ margin: '0 0 8px', color: 'var(--ink-2)', fontSize: 12.5 }}>
            {evaluation.period_start} — {evaluation.period_end} · {evaluation.protocol}
          </p>
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th scope="col">Модель</th>
                  <th scope="col">Турбина</th>
                  <th scope="col">Упреждение</th>
                  <th scope="col">MAE</th>
                  <th scope="col">RMSE</th>
                  <th scope="col">n</th>
                </tr>
              </thead>
              <tbody>
                {evaluation.rows.map((r, i) => (
                  <tr key={i}>
                    <td>{r.model}</td>
                    <td>{r.turbine_id}</td>
                    <td>{r.lead_bucket}</td>
                    <td>{r.mae.toFixed(3)}</td>
                    <td>{r.rmse.toFixed(3)}</td>
                    <td>{r.n}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </section>
  )
}

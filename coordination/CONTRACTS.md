# Предлагаемые контракты для первого согласования

Статус: PROPOSED. C3 согласует с C1/C2/C4 до14:15 и публикует DECISION. Этот документ не свидетельствует о существовании API или готового кода. Совет может предложить корректировку, но уже согласованный контракт меняется только через интегратора с оценкой сроков.

| Объект | Поля и смысл |
|---|---|
| Observation | turbine_id,timestamp,timezone/unit interpretation,wind_m_s,temperature_c,power_normalized,coverage,quality_flags |
| WeatherForecast | provider,model,run_time,available_at или проверяемое основание оценки,valid_time,variables,units,source_reference |
| ForecastRequest | issue_time,turbine_ids,horizon_hours24/48,input_version |
| ForecastRow | run_id,turbine_id,issue_time,valid_time,lead_hours,y_pred,unit,model_version,weather_reference,fallback_status |
| RunStatus | run_id,state,started_at,updated_at,safe_errors,input_version,model_version |
| AgentEvent | run_id,tool_name,safe_input_summary,result_reference,state_transition,retry_count |
| Evaluation | train/tuning/test dates,protocol,baseline,MAE,RMSE,coverage,per_turbine/per_horizon,runtime |

## Инварианты

- Время и единицы однозначны; timezone SCADA не равен timezone часов хакатона автоматически.
- `available_at <= issue_time < valid_time`; run_time сам по себе не доказывает available_at.
- Нельзя требовать отсутствующие февральские измерения для лагов/обновления обучения.
- Выбор split, заполнение пропусков и настройка не используют будущие метки.
- Полный ключ: turbine_id+issue_time+valid_time. Разные выпуски на один целевой час не удаляются как дубликаты.
- Для февраля672 целевых часа на турбину при согласованных календарных границах;1344 уникальные пары для двух турбин. Полный журнал48ч содержит перекрытия и возможно целевые часы за границей теста.
- Единицы нормализованной мощности нельзя выдавать за энергию или складывать в МВт без определённой нормализации.
- Ошибка архива/LLM не даёт status=success. Сохранённый результат и живой запуск различаются.
- При обновлении версии входа есть новый результат/идентификатор; старый остаётся доступным.

Основной стек пока рекомендация: Python+pandas+CatBoost+FastAPI/Pydantic; React/Vite/Plotly; один агент-оркестратор с инструментами. Это не закрывает творческую дискуссию, но любое изменение после начала работ обязано окупиться до контрольной точки.

"""API_CONTRACT_V1: UTC timestamps, explicit provenance and no assumed power cap."""
from datetime import datetime, timezone
from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, field_validator, model_validator

TurbineId = Literal["turbine_1", "turbine_2"]
RunMode = Literal["live", "cached", "deterministic"]
Stage = Literal["weather", "prepare", "forecast", "validate", "export"]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    @field_validator("*", mode="after")
    @classmethod
    def utc_dates(cls, value):
        return value.astimezone(timezone.utc) if isinstance(value, datetime) else value


class ForecastRequest(Contract):
    issue_time: AwareDatetime
    turbine_ids: list[TurbineId] = Field(default_factory=lambda: ["turbine_1", "turbine_2"], min_length=1, max_length=2)
    horizon_hours: Literal[24, 48] = 48
    input_version: str | None = Field(default=None, max_length=160)

    @field_validator("turbine_ids")
    @classmethod
    def unique_turbines(cls, value):
        if len(set(value)) != len(value):
            raise ValueError("Duplicate turbine IDs")
        return value

    @field_validator("issue_time", mode="before")
    @classmethod
    def explicit_timestamp(cls, value):
        if isinstance(value, (float, int)):
            raise ValueError("Use an ISO 8601 timestamp with timezone")
        return value

    @field_validator("issue_time")
    @classmethod
    def hourly_issue(cls, value):
        if value.minute or value.second or value.microsecond:
            raise ValueError("issue_time must be an exact hour")
        return value


class ApiError(Contract):
    code: str
    message: str
    retryable: bool = False


class ForecastRow(Contract):
    turbine_id: TurbineId
    issue_time: AwareDatetime
    valid_time: AwareDatetime
    lead_hours: int = Field(ge=1, le=48)
    y_pred: float | None

    @model_validator(mode="after")
    def time_order(self):
        if (self.valid_time - self.issue_time).total_seconds() != self.lead_hours * 3600:
            raise ValueError("valid_time must equal issue_time + lead_hours")
        return self


class ForecastMetadata(Contract):
    model_version: str | None = None
    input_version: str | None = None
    weather_provider: str | None = None
    weather_model: str | None = None
    weather_run_time: AwareDatetime | None = None
    weather_available_at: AwareDatetime | None = None
    availability_basis: str | None = None
    scada_timezone: str | None = None
    timezone_status: str | None = None
    provenance_status: str | None = None


class ForecastPayload(Contract):
    """Return type expected from the numerical adapter; no API run_id needed."""
    rows: list[ForecastRow]
    metadata: ForecastMetadata
    mode: RunMode
    warnings: list[str] = Field(default_factory=list)


class ForecastResponse(Contract):
    run_id: str
    unit: Literal["normalized_power"] = "normalized_power"
    rows: list[ForecastRow]
    metadata: ForecastMetadata


class RunStatus(Contract):
    run_id: str
    status: Literal["queued", "running", "completed", "failed"]
    stage: Stage | None = None
    mode: RunMode | None = None
    forecast_available: bool = False
    warnings: list[str] = Field(default_factory=list)
    error: ApiError | None = None
    issue_time: AwareDatetime
    turbine_ids: list[TurbineId]
    horizon_hours: Literal[24, 48]
    started_at: AwareDatetime
    updated_at: AwareDatetime


class EventInput(Contract):
    """Tool adapter calls emit(EventInput(...)); only safe human summaries here."""
    tool: str = Field(min_length=1, max_length=80)
    state: str = Field(min_length=1, max_length=80)
    summary: str = Field(max_length=1000)
    stage: Stage | None = None


class AgentEvent(EventInput):
    seq: int
    timestamp: AwareDatetime


class EventResponse(Contract):
    run_id: str
    events: list[AgentEvent]


def check_payload(request: ForecastRequest, payload: ForecastPayload) -> list[str]:
    """Fail closed on future inputs/wrong identity; missing target hours stay missing."""
    seen = set()
    for row in payload.rows:
        if row.turbine_id not in request.turbine_ids or row.issue_time != request.issue_time or row.lead_hours > request.horizon_hours:
            raise ValueError("Forecast identity or horizon differs from request")
        key = (row.turbine_id, row.valid_time)
        if key in seen:
            raise ValueError("Duplicate forecast target hour")
        seen.add(key)
    if not any(row.y_pred is not None for row in payload.rows):
        raise ValueError("No numerical forecast returned")
    metadata = payload.metadata
    if metadata.weather_available_at and metadata.weather_available_at > request.issue_time:
        raise ValueError("Weather became available after issue_time")
    if metadata.weather_run_time and metadata.weather_run_time > request.issue_time:
        raise ValueError("Weather run initialized after issue_time")
    if metadata.weather_available_at and metadata.weather_run_time and metadata.weather_available_at < metadata.weather_run_time:
        raise ValueError("Weather cannot be available before initialization")
    warnings = list(payload.warnings)
    for turbine in request.turbine_ids:
        count = sum(row.y_pred is not None for row in payload.rows if row.turbine_id == turbine)
        if count != request.horizon_hours:
            warnings.append(f"{turbine}: {count}/{request.horizon_hours} часов с прогнозом")
    if metadata.weather_available_at is None:
        warnings.append("Время доступности погоды не подтверждено")
    if metadata.provenance_status != "confirmed":
        warnings.append("Происхождение или доступность погодного выпуска требуют проверки")
    if metadata.timezone_status != "confirmed":
        warnings.append("Часовой пояс SCADA является предположением")
    return list(dict.fromkeys(warnings))

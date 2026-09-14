from contextvars import ContextVar

current_organization_id: ContextVar[str | None] = ContextVar("current_organization_id", default=None)
current_risk_thresholds: ContextVar[tuple[int, int] | None] = ContextVar("current_risk_thresholds", default=None)

def organization_id() -> str | None:
    return current_organization_id.get()

def risk_thresholds() -> tuple[int, int]:
    return current_risk_thresholds.get() or (30, 60)

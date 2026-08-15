from dataclasses import dataclass
from enum import StrEnum


class QAStatus(StrEnum):
    PASS = "PASS"
    INVESTIGATE = "INVESTIGATE"
    FAILED = "FAILED"


@dataclass(frozen=True, slots=True)
class QACheckResult:
    name: str
    passed: bool
    message: str


@dataclass(frozen=True, slots=True)
class BaselineComparison:
    stress_change_percent: float
    frequency_change_percent: float


@dataclass(frozen=True, slots=True)
class StressLimitResult:
    passed: bool
    stress_pa: float
    limit_pa: float
    margin_percent: float


@dataclass(frozen=True, slots=True)
class FrequencyShiftResult:
    passed: bool
    shift_percent: float
    maximum_absolute_shift_percent: float


@dataclass(frozen=True, slots=True)
class OutlierResult:
    is_outlier: bool
    value: float
    z_score: float
    z_threshold: float

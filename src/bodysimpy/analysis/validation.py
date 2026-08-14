def relative_error_percent(
    *,
    reference: float,
    value: float,
) -> float:
    """Return absolute relative error as a percentage."""

    if reference == 0.0:
        raise ValueError("Reference value must be non-zero for relative-error calculation.")

    return abs(value - reference) / abs(reference) * 100.0

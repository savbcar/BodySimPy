import pytest

from bodysimpy.analysis.validation import relative_error_percent


def test_relative_error_percent() -> None:
    error = relative_error_percent(
        reference=0.01561640,
        value=0.01541943,
    )

    assert error == pytest.approx(
        1.2613,
        rel=1e-4,
    )


def test_relative_error_rejects_zero_reference() -> None:
    with pytest.raises(ValueError):
        relative_error_percent(
            reference=0.0,
            value=1.0,
        )

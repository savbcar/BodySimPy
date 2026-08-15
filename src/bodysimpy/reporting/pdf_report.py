from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    Flowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

from bodysimpy.reporting.summary_data import ReportingSummary


def _value(
    value: float | None,
    suffix: str = "",
) -> str:
    if value is None:
        return "Not available"

    return f"{value:.3f}{suffix}"


def generate_engineering_summary_pdf(
    summary: ReportingSummary,
    output_path: str | Path,
) -> None:
    path = Path(output_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    styles = getSampleStyleSheet()

    story: list[Flowable] = []

    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
    )

    story.append(
        Paragraph(
            "BodySimPy Engineering Summary",
            styles["Title"],
        )
    )

    story.append(
        Spacer(
            1,
            16,
        )
    )

    sections = {
        "Objective": (
            "Automate structural CAE workflows for a simplified automotive "
            "body crossmember surrogate using Python, analytical references, "
            "CalculiX FEA, stochastic studies, fatigue assessment and ML surrogates."
        ),
        "Method": (
            "Validated configuration files generate structural models. "
            "Analytical beam theory, CalculiX static/modal analysis and "
            "Python post-processing are used to quantify response behavior."
        ),
        "Baseline Configuration": (
            "Thin-walled rectangular hollow-section cantilever surrogate with "
            "linear-elastic isotropic material and idealized transverse loading."
        ),
        "Key Results": (
            f"Final mesh displacement error: "
            f"{_value(summary.baseline_deflection_error_percent, ' %')}<br/>"
            f"Final mesh stress error: "
            f"{_value(summary.baseline_stress_error_percent, ' %')}<br/>"
            f"Mode-1 frequency: "
            f"{_value(summary.mode_1_frequency_hz, ' Hz')}<br/>"
            f"Observed stochastic stress exceedance over 350 MPa: "
            f"{_value(summary.stress_exceedance_percent, ' %')}<br/>"
            f"Best ML frequency MAPE: "
            f"{_value(summary.best_ml_frequency_mape_percent, ' %')}"
        ),
        "Sensitivity": (
            "Wall thickness, section geometry, Young's modulus, density and "
            "load are evaluated through automated sweeps and stochastic analysis."
        ),
        "Risk": (
            "The model is a simplified surrogate, not a production body-in-white. "
            "Results depend on idealized boundary conditions, beam assumptions, "
            "generic material data and the sampled design domain."
        ),
        "Engineering Recommendation": (
            "Use BodySimPy as a reproducible CAE automation and validation "
            "portfolio workflow. Extend shell modelling, fatigue realism and "
            "solver-result extraction before claiming production-level accuracy."
        ),
    }

    for heading, text in sections.items():
        story.append(
            Paragraph(
                heading,
                styles["Heading2"],
            )
        )

        story.append(
            Paragraph(
                text,
                styles["BodyText"],
            )
        )

        story.append(
            Spacer(
                1,
                12,
            )
        )

    doc.build(story)

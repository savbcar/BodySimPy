from bodysimpy.reporting.pdf_report import generate_engineering_summary_pdf
from bodysimpy.reporting.pptx_report import generate_management_summary_pptx
from bodysimpy.reporting.summary_data import load_reporting_summary


def main() -> None:
    summary = load_reporting_summary()

    generate_engineering_summary_pdf(
        summary,
        "reports/BodySimPy_Engineering_Summary.pdf",
    )

    generate_management_summary_pptx(
        summary,
        "reports/BodySimPy_Management_Summary.pptx",
    )

    print("Generated reports:")
    print("reports/BodySimPy_Engineering_Summary.pdf")
    print("reports/BodySimPy_Management_Summary.pptx")


if __name__ == "__main__":
    main()

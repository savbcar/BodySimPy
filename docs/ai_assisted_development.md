# AI-Assisted Development

## Purpose

BodySimPy uses AI-assisted development selectively to support software engineering tasks such as test generation, code review, documentation, refactoring suggestions, and workflow analysis.

AI output is treated as a candidate engineering suggestion rather than authoritative code or engineering truth.

The human developer remains responsible for validating physical assumptions, software behaviour, solver integration, tests, and final implementation decisions.

---

## Validation Policy

Every significant AI-assisted change follows this workflow:

1. Define a bounded engineering or software task.
2. Provide relevant repository context and constraints.
3. Record the prompt used for the task.
4. Review the generated suggestions individually.
5. Reject suggestions that introduce unsupported physical or software assumptions.
6. Modify partially correct suggestions when necessary.
7. Implement only validated changes.
8. Run the complete BodySimPy quality gate.
9. Record the final accepted result.

The standard verification commands are:

```bash
ruff format --check .
ruff check .
mypy src
python -m pytest
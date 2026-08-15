# AI-Assisted Development

## Purpose

BodySimPy uses AI-assisted development selectively to support software engineering tasks such as test generation, code review, documentation, refactoring suggestions, and workflow analysis.

AI output is treated as a candidate engineering suggestion rather than authoritative code or engineering truth.

The human developer remains responsible for validating physical assumptions, software behaviour, solver integration, tests, and final implementation decisions.

---

## AID-001 — Configuration Validation Edge Cases

### AI Output

GitHub Copilot proposed 40 candidate configuration-validation tests covering geometry boundaries, material properties, signed loading, modal settings, stochastic configuration, mesh configuration, parameter sweeps, project configuration, strict-model behavior, and non-finite numerical values.

The assistant distinguished between behavior already supported by the existing implementation and several ambiguous cases requiring a new engineering decision.

Notably, the assistant correctly identified that negative `tip_force_n` values are intentionally valid and must not be rejected.

The assistant also identified non-finite floating-point values (`NaN` and infinity) as an unresolved validation-policy question across multiple physical configuration fields.

### Engineering Validation

The candidate list was manually reviewed against BodySimPy's existing structural assumptions and software requirements.

The review deliberately rejected broad implementation of all AI-generated candidates. Redundant tests that merely repeated equivalent direct field constraints were not selected solely because they were suggested by the AI assistant.

Nine existing-contract tests were accepted for their boundary or regression value:

- exact rectangular-hollow-section thickness boundary rejection;
- acceptance immediately inside the valid thickness boundary;
- both exact Poisson-ratio boundary rejections;
- preservation of valid negative signed tip force;
- rejection of an empty thickness sweep;
- preservation of unsorted sweep input;
- rejection of zero worker count;
- rejection of unsupported extra fields in a nested geometry configuration.

Several suggestions were deferred because they would unnecessarily duplicate existing validation or would establish requirements not yet justified by the project.

The non-finite-number suggestions were treated separately because they exposed a genuine engineering-policy question rather than an existing implementation requirement.

A human engineering decision was made that physical numerical configuration values used by structural analysis and simulation workflows must be finite. `NaN`, positive infinity, and negative infinity are therefore considered invalid engineering configuration values.

This finite-number policy will be introduced test-first before any production implementation is changed.

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

### Final Result

The AI-assisted review produced two classes of improvements.

First, nine high-value regression and boundary tests were selected from the larger AI-generated candidate set after human engineering review. These tests protect existing requirements including signed loading, geometric boundary behaviour, parameter-sweep semantics, and strict nested configuration validation.

Second, the AI review surfaced ambiguity around non-finite floating-point values. A human engineering decision established that physical numerical configuration values must be finite.

Test-first validation showed that infinite Young's modulus, infinite signed load, infinite stochastic standard deviation, and infinite thickness-sweep entries were still accepted by the existing configuration layer, while some geometry cases were already rejected by existing constraints.

The production configuration policy was then changed centrally through the shared Pydantic model configuration rather than by adding duplicated field-specific validators.

The final policy preserves finite negative signed loads while rejecting NaN and positive/negative infinity.

### Human Validation Decisions

Accepted:
- preserve signed negative finite loads;
- enforce the exact rectangular-hollow-section geometric boundary;
- preserve unsorted sweep input;
- reject zero worker counts;
- reject unsupported nested fields;
- enforce finite numerical engineering configuration values.

Rejected or deferred:
- redundant tests that simply duplicated equivalent existing field constraints;
- arbitrary maximum worker limits;
- automatic sweep sorting;
- silent input clamping;
- unsupported material or physical assumptions;
- unrelated project-name policy changes.

### Verification

The accepted implementation was verified using:

```text
ruff format --check .
ruff check .
mypy src
python -m pytest
```
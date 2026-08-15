# BodySimPy GitHub Copilot Instructions

## Project identity

BodySimPy is a Python-driven structural CAE workflow automation project built around a simplified automotive body structural surrogate.

The project is intended to demonstrate engineering software architecture, structural mechanics, finite-element workflow automation, validation, uncertainty analysis, fatigue methods, parameter studies, reporting, and machine-learning surrogate modelling.

Do not describe BodySimPy as a BMW project, proprietary body-in-white model, production vehicle model, or industrial validation study.

## Engineering modelling rules

- Use SI units internally unless a reporting layer explicitly converts units for presentation.
- Do not invent material properties, fatigue curves, manufacturing tolerances, load cases, geometry, experimental measurements, or solver results.
- Do not hardcode numerical FEA outputs that should come from CalculiX.
- Preserve the distinction between analytical reference solutions and finite-element results.
- Preserve the distinction between the simplified structural surrogate and a production automotive structure.
- Clearly state assumptions whenever a proposed implementation introduces a new physical assumption.

## Structural configuration rules

- Geometric dimensions must be physically positive.
- A rectangular hollow section is valid only when the wall thickness leaves a positive internal cavity.
- The physical constraint is:

  `2 * thickness < min(width, height)`

- Do not silently clamp physically invalid geometry.
- Invalid geometry should be rejected explicitly.

## Loading rules

- `tip_force_n` is a signed quantity.
- A negative force is valid and represents the opposite loading direction.
- Do not add positivity validation to `tip_force_n` unless the project requirements explicitly change.

## Material rules

- Young's modulus and density must remain physically positive.
- Poisson's ratio must remain inside the limits already defined by the configuration model.
- Do not invent material-specific durability or fatigue data.

## FEA rules

- CalculiX solver outputs must be parsed from generated solver files.
- Do not replace real solver integration tests with mocked results when the test is specifically intended to validate CalculiX integration.
- Keep temporary/raw CalculiX outputs outside version control.
- Maintain isolated work directories when independent simulations execute concurrently.

## Software architecture

- Reusable production code belongs in `src/bodysimpy/`.
- Verification belongs in `tests/`.
- Exploratory notebooks belong in `notebooks/`.
- Scripts may orchestrate studies but should reuse package functionality rather than duplicate engineering equations.
- Keep solver-independent domain objects separate from solver-specific implementations.
- Prefer small, focused functions and dataclasses over monolithic workflows.

## Testing workflow

Prefer test-driven development for new behaviour:

1. Define expected behaviour with a focused test.
2. Confirm the new test fails for the expected reason.
3. Implement the minimum correct behaviour.
4. Run the focused test.
5. Run the complete project quality gate.

Do not change physically correct implementation behaviour merely to satisfy an AI-generated test.

If an AI-generated test assumes behaviour that is not part of the BodySimPy requirements, flag that assumption instead of silently implementing it.

## Quality gate

Before considering a change complete, the project should pass:

```bash
ruff format --check .
ruff check .
mypy src
python -m pytest
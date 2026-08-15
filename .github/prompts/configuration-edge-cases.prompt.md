# BodySimPy Configuration Edge-Case Review

## Goal

Identify useful additional edge-case unit tests for BodySimPy configuration validation.

Do not modify any source or test files yet.

Your first response must only propose candidate tests for human engineering review.

## Relevant project files

Review:

- `src/bodysimpy/config/models.py`
- `tests/unit/test_config_models.py`
- `tests/unit/test_sweep_config.py`

## Engineering constraints

Preserve the existing BodySimPy requirements.

In particular:

- geometric dimensions must be physically positive;
- rectangular hollow-section geometry requires:

  `2 * thickness < min(width, height)`

- `tip_force_n` is signed and negative force values are valid;
- do not invent a requirement that loads must be positive;
- configuration models intentionally reject unsupported extra fields;
- positive worker counts are required where parallel execution is configured;
- do not invent arbitrary maximum worker limits;
- do not silently clamp invalid engineering values;
- do not invent requirements for sorting parameter-sweep values unless existing code requires sorted values;
- preserve existing public behaviour unless a genuine defect is identified.

## Task

Inspect the existing models and tests.

Identify gaps in boundary-value and invalid-input coverage.

Consider categories such as:

- exact physical boundary conditions;
- empty collections;
- zero values;
- negative values where physically invalid;
- signed values where negative values are intentionally valid;
- unsupported extra configuration fields;
- duplicate values;
- non-finite floating-point values;
- invalid worker counts;
- material-property boundaries.

Do not assume every category necessarily requires a new test.

## Required response format

For every proposed candidate, provide:

### Candidate N — descriptive test name

**Target model/function:**  
Name of the model or function.

**Input condition:**  
Exact edge condition being tested.

**Expected behaviour:**  
Pass or reject, including expected exception type when appropriate.

**Reason:**  
Why the test is useful.

**Requirement support:**  
State whether the expected behaviour is directly supported by existing BodySimPy code/requirements or requires a new engineering decision.

## Important

Do not edit files.

Do not provide implementation changes yet.

Do not invent physical requirements.

If you identify an ambiguous requirement, explicitly mark it as ambiguous and ask for human engineering review.
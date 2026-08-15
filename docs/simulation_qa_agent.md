# Simulation QA Agent

## Purpose

The BodySimPy Simulation QA Agent provides a deterministic
tool-orchestration layer for screening completed structural simulations.

The agent does not generate engineering truth independently.

Instead, it selects and coordinates validated engineering tools according
to the metadata available for a simulation.

## Workflow

A completed simulation may provide:

- solver return code;
- expected output-file status;
- solver log;
- peak stress;
- mode-1 natural frequency;
- baseline results;
- configured engineering screening thresholds;
- historical reference results.

The agent selects applicable tools and combines their outputs into a
human-readable QA recommendation.

## Available Tools

### `check_solver_completion()`

Checks:

- solver return code;
- expected output availability.

### `inspect_simulation_log()`

Screens solver logs for known failure markers.

This is a heuristic log-screening step and does not replace complete
solver-specific convergence diagnostics.

### `compare_to_baseline()`

Calculates percentage changes in structural responses relative to a
validated baseline.

### `check_stress_limit()`

Compares calculated peak stress with a user-supplied screening threshold.

The threshold is an explicit workflow input and is not inferred by the
agent.

### `check_frequency_shift()`

Compares mode-1 frequency change with a configured percentage threshold.

### `detect_outlier()`

Uses a simple z-score relative to supplied historical values.

This is an outlier-screening heuristic rather than proof that a
simulation is physically invalid.

### `summarize_results()`

Converts validated tool outputs into a deterministic human-readable
summary.

## Status Levels

### PASS

No configured QA screening condition was triggered.

### INVESTIGATE

The solver completed, but one or more engineering screening checks were
triggered.

Examples include:

- stress threshold exceedance;
- excessive frequency shift;
- statistical outlier indication.

### FAILED

Solver completion or log inspection indicates that the numerical result
should not be interpreted before solver issues are investigated.

## Engineering Responsibility

The QA agent is an orchestration and screening tool.

It does not replace:

- physical modelling judgement;
- mesh-convergence studies;
- solver verification;
- experimental validation;
- material qualification;
- production durability assessment;
- engineering sign-off.

A flagged result indicates that additional engineering review is
recommended.
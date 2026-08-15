# BodySimPy

Python-driven structural CAE workflow automation for simplified automotive body structures.

## Overview

BodySimPy is an engineering software project exploring the automation of structural simulation workflows using Python.

The project combines:

- parameterized structural models
- automated FEA solver execution
- static structural analysis
- modal analysis
- simulation result extraction
- stochastic parameter studies
- fatigue assessment
- PyTorch surrogate modelling
- automated testing and continuous integration
- engineering result reporting

## Current Status

The current implementation contains:

- validated geometric section calculations
- material-domain models
- analytical cantilever reference calculations
- static deflection estimation
- bending-stress estimation
- first natural-frequency estimation
- automated unit tests
- Ruff formatting and linting
- strict static type checking with mypy
- GitHub Actions CI configuration
- command-line interface

## Planned Workflow

Configuration → Model generation → FEA solver → Result parsing → Validation → Parameter studies → ML surrogate → Engineering report

## Engineering Philosophy

Numerical simulation results are validated against independent analytical reference solutions wherever practical.

## Current Technology

Python · NumPy · SciPy · pandas · pytest · Ruff · mypy · Typer · Git · GitHub Actions · Linux

## Planned Integration

CalculiX · PyTorch

## Current Crossmember Surrogate

The current baseline model represents a simplified automotive body structural crossmember as a uniform thin-walled rectangular hollow section.

It is intended to validate the BodySimPy simulation workflow and solver automation architecture rather than reproduce a production vehicle body structure.

### Current assumptions

- uniform prismatic cross-section
- linear-elastic isotropic material
- idealized cantilever boundary condition
- transverse point loading
- beam-element representation
- small-deformation structural response

### Not currently represented

- stamped sheet-metal geometry
- local beads or reinforcements
- joints and spot welds
- complex vehicle boundary conditions
- production load cases
- proprietary vehicle geometry

## Planned Geometry Evolution

The structural representation will evolve incrementally from the validated beam surrogate toward a parameterized thin-walled shell model.

Planned parameters include:

- wall thickness
- section depth
- flange width
- local reinforcement
- mesh density
- joint and spot-weld idealization

## Stochastic Engineering

BodySimPy includes Monte Carlo uncertainty propagation for selected manufacturing, material and loading parameters.

The baseline stochastic study evaluates 500 independently sampled configurations with uncertainty in:

- wall thickness
- Young's modulus
- applied load

Each sampled configuration is evaluated using automated CalculiX static and modal analyses.

Reported quantities include:

- response mean and standard deviation
- 5th and 95th percentiles
- stress-threshold exceedance fraction
- mode-1 frequency variation
- correlation analysis
- standardized linear sensitivity coefficients

The stochastic model is intended as an engineering uncertainty study for the simplified structural surrogate and does not represent production vehicle reliability.


## Fatigue Assessment

BodySimPy includes an initial stress-life fatigue assessment module based on a power-law S-N model and linear Palmgren-Miner cumulative damage.

The module evaluates constant-amplitude loading blocks and reports:

- predicted cycles to failure for each stress amplitude
- individual Miner damage contributions
- cumulative damage fraction
- estimated repeated-spectrum life
- critical loading block

The current fatigue model is intended for workflow development and engineering-method demonstration. Example S-N parameters are generic and are not representative of proprietary vehicle material or joint durability data.

### Current limitations

The initial implementation does not yet include:

- rainflow counting
- mean-stress corrections
- weld-class fatigue curves
- notch effects
- multiaxial fatigue
- low-cycle fatigue
- crack-growth modelling

## PyTorch Structural Surrogate

BodySimPy includes a feed-forward neural-network surrogate trained on a six-dimensional CalculiX design dataset.

### Inputs

- wall thickness
- section height
- section width
- Young's modulus
- material density
- applied tip force

### Predicted responses

- maximum axial stress
- tip displacement
- mode-1 natural frequency

The training dataset is generated using Latin Hypercube sampling across a bounded engineering design space and evaluated using automated static and modal CalculiX analyses.

The dataset is separated into training, validation and held-out test subsets. Input and target normalization statistics are fitted exclusively on the training subset.

Training includes validation monitoring, early stopping and best-model checkpointing.

The surrogate is intended for interpolation within the sampled design space and does not replace finite-element validation outside that domain.

## Simulation QA Agent

BodySimPy includes a deterministic simulation-quality-assurance agent
that orchestrates validated analysis tools after a structural simulation
completes.

Depending on available metadata, the agent can:

- verify solver completion;
- inspect simulation logs;
- compare structural responses with a baseline;
- check supplied stress thresholds;
- detect excessive modal-frequency shifts;
- screen results for statistical outliers;
- produce a human-readable engineering summary.

The agent does not independently generate engineering truth. Its role is
to select and coordinate deterministic tools whose outputs remain
testable and reviewable.

See [`docs/simulation_qa_agent.md`](docs/simulation_qa_agent.md) for the
workflow and limitations.
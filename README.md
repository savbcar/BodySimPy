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
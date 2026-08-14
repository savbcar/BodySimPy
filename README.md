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
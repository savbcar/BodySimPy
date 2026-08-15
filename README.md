# BodySimPy

## Python-Driven Structural CAE Workflow Automation for Automotive Body Structures

[![CI](https://github.com/savbcar/BodySimPy/actions/workflows/ci.yml/badge.svg)](https://github.com/savbcar/BodySimPy/actions/workflows/ci.yml)
[![Tests](https://img.shields.io/github/actions/workflow/status/savbcar/BodySimPy/ci.yml?branch=main&label=tests)](https://github.com/savbcar/BodySimPy/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue)
![License](https://img.shields.io/badge/License-MIT-green)

**BodySimPy** is a Python-based engineering software project for automating structural CAE studies around a simplified automotive body crossmember surrogate.

The project combines analytical mechanics, CalculiX finite-element analysis, structural dynamics, uncertainty propagation, fatigue assessment, parameter-study automation, PyTorch surrogate modelling, automated reporting, test-driven development, AI-assisted software development, and simulation QA.

The objective is not to reproduce a proprietary vehicle body model. The objective is to demonstrate how Python can be used to build a **reproducible, validated and extensible structural engineering workflow** around an open-source finite-element solver.

---

## Engineering Workflow

```mermaid
flowchart LR
    A[YAML Configuration] --> B[Validated Domain Model]

    B --> C[Analytical Solver]
    B --> D[CalculiX FEA]

    D --> E[Static Analysis]
    D --> F[Modal Analysis]

    C --> G[FEA Validation]
    E --> G

    E --> H[Parameter Sweeps]
    E --> I[Stochastic Analysis]
    E --> J[Fatigue Assessment]

    E --> K[FEA Dataset]
    F --> K

    K --> L[PyTorch Surrogate]

    G --> M[Engineering Results]
    H --> M
    I --> M
    J --> M
    L --> M

    M --> N[Simulation QA Agent]
    M --> O[Automated Reporting]



## Software Architecture

BodySimPy/
│
├── configs/
│   └── simulation and study configurations
│
├── data/
│   └── generated engineering / surrogate datasets
│
├── docs/
│   ├── figures/
│   ├── validation/
│   ├── ai_assisted_development.md
│   └── simulation_qa_agent.md
│
├── reports/
│   └── automated engineering summaries
│
├── scripts/
│   └── reproducible study and reporting entry points
│
├── src/bodysimpy/
│   ├── agents/
│   ├── analysis/
│   ├── config/
│   ├── domain/
│   ├── ml/
│   ├── modeling/
│   ├── reporting/
│   ├── solvers/
│   │   └── parsers/
│   └── workflows/
│
└── tests/
    ├── integration/
    └── unit/


Development Environment

Primary development workflow:

Linux through WSL / Ubuntu;
Python virtual environment;
Visual Studio Code;
Git;
GitHub;
CalculiX;
NumPy;
SciPy;
pandas;
Matplotlib;
Pydantic;
Typer;
pytest;
Ruff;
mypy;
PyTorch;
GitHub Copilot.

What I Learned

BodySimPy reinforced several engineering-development principles.

Automate repetitive engineering work

Python provides significantly more value when it controls the complete simulation workflow rather than merely post-processing isolated files.

Validate numerical models

Finite-element output should not be accepted only because a solver completed successfully. Analytical references, mesh studies, trend checks and explicit assumptions are essential.

Separate physics from software infrastructure

Domain models, solver adapters, parsers, analyses and reporting become easier to test when responsibilities are separated.

Quantify uncertainty rather than hiding it

A deterministic baseline gives one answer. Stochastic studies reveal how response distributions change when engineering inputs vary.

ML usefulness depends on economics as well as accuracy

A surrogate is valuable only when its prediction quality, training-data cost, evaluation volume and domain of validity make the trade-off worthwhile.

AI output still requires engineering judgement

AI coding tools can accelerate exploration and testing, but physical assumptions, numerical methods and final implementation decisions remain human engineering responsibilities.

Communication is part of engineering

A technically correct Python workflow is incomplete if its results cannot be communicated clearly to engineers, reviewers and decision-makers.

Limitations

BodySimPy is a portfolio and engineering-method development project. Its results must be interpreted within the assumptions of the implemented model.

Current limitations include:

the structural geometry is a simplified crossmember surrogate rather than a production body-in-white model;
beam idealization does not represent detailed shell geometry, spot welds, adhesives, joints, local stamped features or contact;
materials are currently represented using simplified linear-elastic isotropic behaviour;
boundary conditions and loads are idealized;
finite-element validation is primarily against analytical mechanics rather than physical vehicle-test data;
numerical agreement with the analytical surrogate does not constitute validation of a real automotive structure;
stochastic input distributions are study assumptions rather than measured manufacturing distributions;
sampled threshold-exceedance fractions are not real-world failure probabilities;
simple correlation and regression sensitivity metrics are screening tools rather than full global sensitivity analysis;
the initial fatigue model uses simplified S-N and Palmgren-Miner damage assumptions;
fatigue calculations do not yet model weld classes, notch effects, rainflow counting, mean-stress correction, multiaxial fatigue, low-cycle fatigue or crack growth;
the PyTorch surrogate reproduces the underlying CalculiX model and cannot improve the physical fidelity of its training labels;
ML accuracy has only been demonstrated inside the sampled parameter domain;
surrogate predictions outside that domain should not be treated as validated extrapolation;
runtime comparisons depend on hardware, solver settings and benchmarking methodology;
statistical outlier detection in the QA workflow is a screening heuristic;
Simulation QA statuses support engineering review and do not replace engineering sign-off;
AI-assisted development tools may propose incorrect code or engineering assumptions and therefore require human validation.

These limitations are intentionally documented because acknowledging model boundaries is part of responsible engineering analysis.

Future Development

Potential extensions include:

shell-element automotive structural models;
spot-weld and adhesive-joint representation;
additional static and dynamic load cases;
geometry import and richer meshing workflows;
experimental or high-fidelity reference validation;
nonlinear material behaviour;
buckling analysis;
transient structural dynamics;
rainflow cycle counting;
mean-stress corrections;
welded-joint fatigue classes;
global sensitivity analysis;
correlated manufacturing uncertainty;
optimization loops;
uncertainty-aware ML surrogates;
automatic model-domain checking before surrogate inference;
richer simulation QA tooling;
expanded CLI orchestration;
interactive engineering dashboards.

Quick Start

Clone the repository:

git clone https://github.com/savbcar/BodySimPy.git
cd BodySimPy

Create and activate a virtual environment:

python3.11 -m venv .venv
source .venv/bin/activate

Upgrade pip:

python -m pip install --upgrade pip

Install BodySimPy and development dependencies:

python -m pip install -e ".[dev]"

Install CalculiX on Ubuntu / WSL:

sudo apt update
sudo apt install calculix-ccx

Run the quality gate:

ruff format --check .
ruff check .
mypy src
python -m pytest

Explore the CLI:

bodysim --help
Project Status

BodySimPy is under active development as a structural CAE and engineering-software portfolio project.

The focus is on:

reproducibility, validation, automation, explicit assumptions and engineering interpretation.

License

MIT License.
# Python Package Roadmap: `quantum-gametheory`

This document details the strategy, project structure, and implementation steps to transform this project into an open-source, PyPI-installable Python package.

---

## 1. Objectives & Package Vision

`quantum-gametheory` aims to be an accessible bridge between classical game theory modeling and quantum decision theory. It enables developers and researchers to:
1. Parse classical text scenarios into formal game schemas using LLMs.
2. Simulate quantum entanglement strategies (GHZ state, EWL protocol, custom quantum circuits) via Qiskit.
3. Generate automated Markdown insights and payoff equilibria comparison (Classical vs. Quantum).
4. Run locally as a Python library, a CLI tool, or a web application (FastAPI + Gradio).

---

## 2. Directory Structure

```text
quantum-gametheory/
├── pyproject.toml               # Build configuration (Hatch / Setuptools)
├── README.md                    # Overview, installation, quickstart
├── LICENSE                      # Open-source license (e.g. MIT)
├── PYTHON_PACKAGE.md            # Packaging guide & architecture overview
├── requirements.txt             # Standard dependencies list
├── src/
│   └── quantum_gametheory/      # Main package directory
│       ├── __init__.py          # Top-level imports
│       ├── schemas.py           # Pydantic data models
│       ├── ai/
│       │   ├── __init__.py
│       │   ├── openrouter.py    # OpenRouter / LLM client wrappers
│       │   └── prompts.py       # Prompt templates
│       ├── quantum/
│       │   ├── __init__.py
│       │   ├── ghz.py           # GHZ state entanglement simulation
│       │   └── base.py          # Abstract base class for quantum algorithms
│       ├── core.py              # Main execution logic / SDK entrypoints
│       ├── cli.py               # Command Line Interface (Typer / argparse)
│       └── server/
│           ├── __init__.py
│           ├── app.py           # FastAPI application definition
│           └── ui.py            # Gradio Interface builder
└── tests/
    ├── test_schemas.py
    ├── test_quantum.py
    └── test_ai.py
```

---

## 3. Build & Packaging Configuration (`pyproject.toml`)

To make the package buildable via `pip install .` or publishable to PyPI:

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "quantum-gametheory"
version = "0.1.0"
description = "A unified framework combining classical game theory parsing with Qiskit quantum entanglement simulations."
readme = "README.md"
authors = [
    { name = "Quantum Game Theory Contributors" }
]
license = { text = "MIT" }
requires-python = ">=3.9"
dependencies = [
    "fastapi>=0.100.0",
    "uvicorn>=0.22.0",
    "gradio>=4.0.0",
    "qiskit>=1.0.0",
    "qiskit-aer>=0.13.0",
    "requests>=2.28.0",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
cli = ["typer>=0.9.0"]
dev = [
    "pytest>=7.0.0",
    "black",
    "ruff"
]

[project.scripts]
quantum-game-server = "quantum_gametheory.server.app:launch_server"
quantum-game-cli = "quantum_gametheory.cli:main"
```

---

## 4. Reusable SDK API Design

Users will be able to use the library in Python code cleanly:

```python
from quantum_gametheory import QuantumGameAnalyzer, GameRequest

# Initialize analyzer
analyzer = QuantumGameAnalyzer(api_key="sk-or-v1-...")

# Run analysis
result = analyzer.analyze("Two criminals are arrested by the police...")

if isinstance(result, str):
    print("Result:", result) # "this is not game theory problem."
else:
    print(result.markdown_response)
    print(result.processed_json)
```

---

## 5. Modular Quantum Engine Extension

To enable expanding beyond the GHZ state simulation:
- Define a base interface `QuantumProtocol` with `run_simulation(schema: GameTheorySchema) -> dict`.
- Implement alternative quantum protocols:
  - **GHZ State Protocol** ($N$-qubit GHZ state with strategy rotations).
  - **Eisert-Wilkens-Lewenstein (EWL) Protocol** for 2-player games (e.g. Prisoner's Dilemma).
  - **Penny Flip Game** quantum algorithm.

---

## 6. Deployment & Publishing Steps

1. **Local Development Install**:
   ```bash
   pip install -e .
   ```
2. **Build Distribution Packages**:
   ```bash
   pip install build twine
   python -m build
   ```
3. **Publish to PyPI**:
   ```bash
   python -m twine upload dist/*
   ```

---

## 7. Next Actions Roadmap

- [x] Refactor FastAPI + Gradio server into modular components (`app/`).
- [ ] Add unit tests using `pytest` for `quantum.py` logic.
- [ ] Implement `pyproject.toml` and CLI entrypoint.
- [ ] Add support for configurable LLM providers & custom quantum rotation angles.

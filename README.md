# 🎲 Quantum Game Theory Analyzer

A unified **FastAPI** and **Gradio** web application and simulation framework that models classical game theory scenarios using **Qiskit** quantum circuits (GHZ state entanglement) and OpenRouter LLMs.

---

## 📌 Features

- **LLM Game Scenario Parsing**: Analyzes unstructured text scenarios and extracts structured game theory metadata (`GameTheorySchema` for up to 5 players) via OpenRouter.
- **Quantum Entanglement Simulation**: Simulates decision space strategy rotations over an $N$-qubit GHZ state circuit using Qiskit and `AerSimulator`.
- **Automated Insights**: Generates structured Markdown reports (classical vs. quantum strategy analysis, payoff matrix summary, and equilibrium shifts).
- **FastAPI Backend + Gradio Frontend**: Exposes a clean REST API `/analyze_game` while hosting a Gradio web interface mounted at the root (`/`).

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- OpenRouter API Key

### Installation

1. Clone the repository and navigate to the root directory:
   ```bash
   cd quantum-gametheory
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

---

## 🏃 Running the Application

Launch the unified FastAPI + Gradio server:

```bash
python -m app.main
```

Using the start script:

```bash
./start.sh
```

Or using `uvicorn` directly:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- **Gradio Web Interface**: Open [http://localhost:8000/](http://localhost:8000/) in your browser.
- **FastAPI Interactive Docs**: Open [http://localhost:8000/docs](http://localhost:8000/docs).

---

## 📡 API Usage

### Endpoint: `POST /analyze_game`

#### Request Body
```json
{
  "api_key": "sk-or-v1-...",
  "text": "Two prisoners are arrested for a crime..."
}
```

#### Response (Valid Game Theory Problem)
```json
{
  "markdown_response": "# Quantum Game Theory Analysis\n...",
  "processed_json": {
    "classical_schema": {
      "is_game_theory": true,
      "players": [...],
      "payoff_matrix": {...},
      "narrative_context": "..."
    },
    "quantum_results": {
      "quantum_counts": {"00": 512, "11": 512},
      "dominant_strategy_binary": "00",
      "total_shots": 1024,
      "entanglement_type": "2-qubit GHZ state"
    }
  }
}
```

#### Response (Non-Game Theory Problem)
```json
"this is not game theory problem."
```

---

## 📁 Project Architecture

```text
quantum-gametheory/
├── app/
│   ├── __init__.py
│   ├── schemas.py       # Pydantic models (Player, GameTheorySchema, GameRequest, GameResponse)
│   ├── ai.py            # OpenRouter parsing and Markdown insight generation
│   ├── quantum.py       # Qiskit GHZ state entanglement simulation
│   ├── core.py          # Application workflow logic
│   └── main.py          # FastAPI application & Gradio UI mount
├── requirements.txt     # Python dependencies
├── PYTHON_PACKAGE.md    # Packaging roadmap & Python SDK specifications
└── README.md            # Project overview & documentation
```

---

## 📦 Python Packaging Roadmap

For details on converting this workspace into a pip-installable library (`quantum-gametheory`), refer to [PYTHON_PACKAGE.md](file:///Users/ernest.pascual/Downloads/Development/quantum-gametheory/PYTHON_PACKAGE.md).

---

## 📄 License

MIT

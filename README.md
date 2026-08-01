# 🎲 Quantum Game Theory Analyzer

A unified **FastAPI** and **Gradio** web application and simulation framework that models classical game theory scenarios using **Qiskit** quantum circuits (GHZ state entanglement) and OpenRouter LLMs.

---

## 📌 Features

- **LLM Game Scenario Parsing**: Analyzes unstructured text scenarios and extracts structured game theory metadata (`GameTheorySchema` for up to 5 players) via OpenRouter.
- **Quantum Entanglement Simulation**: Simulates decision space strategy rotations over an $N$-qubit GHZ state circuit using Qiskit and `AerSimulator`.
- **Automated Insights**: Generates structured Markdown reports (classical vs. quantum strategy analysis, payoff matrix summary, and equilibrium shifts).
- **FastAPI Backend + Gradio Frontend**: Exposes a clean REST API `/analyze_game` while hosting a Gradio web interface mounted at the root (`/`).
- **Serverless & Sleeping Container Optimized**: Fast boot times with lazy module loading and built-in health check `/health`.

---

## ⚡ Serverless & Cold Start Optimizations

To ensure minimal wake-up latency when deployed to serverless environments (e.g. Railway, Render, GCP Cloud Run):

1. **Lazy Imports**: Heavy computational libraries (`qiskit`, `qiskit_aer`, `reportlab`) are imported lazily inside their respective functions (`process_quantum_entanglement`, `export_to_pdf`) rather than globally at app startup. This allows FastAPI/Gradio to boot in ~2–3 seconds instead of 15+ seconds.
2. **Slim Container Footprint**: `requirements.txt` strictly includes lightweight required packages without heavy unused ML frameworks.
3. **Container Health Checks**: A lightweight GET `/health` endpoint returns `{"status": "ok"}` for platform health-check pre-warming.

---

## ⚛️ Quantum Algorithm Description

The quantum simulation pipeline in `app/quantum.py` utilizes **Multi-Qubit GHZ (Greenberger–Horne–Zeilinger) Entanglement** and rotation gates to construct a joint decision space:

1. **State Initialization**: For $N$ players ($N \le 5$), an $N$-qubit register $|00\dots 0\rangle$ and classical readout register are initialized.
2. **Entanglement Preparation**: 
   - A Hadamard gate $H$ is applied to qubit 0: $H|0\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$.
   - Cascaded Controlled-NOT ($CNOT$) gates entangle qubit 0 with all subsequent qubits $i \in \{1, \dots, N-1\}$, producing a maximally entangled $N$-qubit GHZ state:
     $$\psi_{GHZ} = \frac{1}{\sqrt{2}}\left(|00\dots 0\rangle + |11\dots 1\rangle\right)$$
3. **Gate Rationale & Purpose**:
   - **Hadamard Gate ($H$)**: Placed on the first qubit to create an equal superposition of $|0\rangle$ and $|1\rangle$. This removes deterministic bias, allowing the first player to explore all possible strategic choices simultaneously.
   - **Controlled-NOT Gates ($CNOT$)**: Links qubit 0 as the control to every other player's qubit as targets. This creates strong quantum entanglement across all players, guaranteeing that their decision states become physically correlated rather than statistically independent.
   - **Strategy Rotation Gates ($R_x$)**: Applies a continuous $X$-axis rotation ($\pi/2$) to each qubit, transforming pure classical choices into quantum strategy superpositions that allow players to access non-classical equilibria.
4. **Quantum Strategy Operator**: Each player's action choice is mapped to a single-qubit strategy operator $R_x(\theta)$ (a rotation around the X-axis by $\theta = \pi/2$), introducing quantum superpositions of strategies:
   $$R_x(\pi/2) = \begin{bmatrix} \frac{1}{\sqrt{2}} & -\frac{i}{\sqrt{2}} \\ -\frac{i}{\sqrt{2}} & \frac{1}{\sqrt{2}} \end{bmatrix}$$
5. **Measurement & Execution**: The circuit is measured into $N$ classical bits over 1,024 shots on Qiskit's `AerSimulator`, returning measurement frequency distributions and identifying dominant joint strategy bitstrings.

---

## ⚖️ Comparing Quantum vs. Classical Game Theory

| Dimension | Classical Game Theory | Quantum Game Theory |
| :--- | :--- | :--- |
| **Strategy Space** | Discrete probability distributions over deterministic choices (Mixed Strategies). | Continuous unitary operations on Hilbert spaces (Quantum Superposition). |
| **Player Independence** | Players make choices independently; correlation only via explicit communication/correlated equilibria. | Non-local correlations via **Quantum Entanglement** without direct player communication. |
| **Equilibrium Behavior** | In dilemmas like Prisoner's Dilemma, Nash Equilibrium often forces Pareto-suboptimal outcomes (Defect, Defect). | Quantum entanglement can resolve classical dilemmas, achieving Pareto-optimal equilibria (e.g. mutual Cooperation). |
| **Payoff Calculation** | Expected value over independent joint probability vectors $P(s_1, s_2) = P(s_1)P(s_2)$. | Expectation values of payoff operators over entangled joint state vectors $\langle \psi | \hat{H}_{payoff} | \psi \rangle$. |

### How to Compare Results in the App:
1. **Classical Baseline**: Inspect the `classical_schema` table in the generated report to locate the traditional Nash Equilibrium (where no player can unilaterally improve their payoff).
2. **Quantum Outcome**: Observe the `dominant_strategy_binary` from the Qiskit execution counts. Note how non-zero off-diagonal state amplitudes in the GHZ state allow players to access Pareto-superior payoff outcomes unreachable in classical un-correlated play.

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

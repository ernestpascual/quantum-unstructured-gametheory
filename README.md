# 🎲 Quantum Game Theory Analyzer

A unified **FastAPI** and **Gradio** web application and simulation framework that models classical game theory scenarios using **Qiskit** quantum circuits (GHZ state entanglement) and OpenRouter LLMs.

---

## 📌 Features

- **LLM Game Scenario Parsing**: Analyzes unstructured text scenarios and extracts structured game theory metadata (`GameTheorySchema` for up to 5 players) via OpenRouter, Google AI Studio, or OpenAI.
- **Dual Quantum Simulation Modes**:
  - **Equilibrium Mode (`"equilibrium"`)**: Simulates an $N$-qubit **GHZ state** circuit for joint Nash/Pareto equilibria.
  - **Winning Mode (`"winning"`)**: Generates an $N$-qubit **W-state** circuit using parameterized $R_y$ and Controlled-$R_y$ ($CRY$) rotations to produce a **Strategic Winning Matrix Table** that safely prevents blackout collision penalties.
- **Automated Insights**: Generates structured Markdown reports (classical vs. quantum strategy analysis, payoff matrix summary, and equilibrium/winning shifts).
- **FastAPI Backend + Gradio Frontend**: Exposes a clean REST API `/analyze_game` while hosting a Gradio web interface mounted at the root (`/`).
- **Serverless & Sleeping Container Optimized**: Fast boot times with lazy module loading and built-in health check `/health`.

---

## ⚡ Serverless & Cold Start Optimizations

To ensure minimal wake-up latency when deployed to serverless environments (e.g. Railway, Render, GCP Cloud Run):

1. **Lazy Imports**: Heavy computational libraries (`qiskit`, `qiskit_aer`, `reportlab`) are imported lazily inside their respective functions (`process_quantum_entanglement`, `export_to_pdf`) rather than globally at app startup. This allows FastAPI/Gradio to boot in ~2–3 seconds instead of 15+ seconds.
2. **Slim Container Footprint**: `requirements.txt` strictly includes lightweight required packages without heavy unused ML frameworks.
3. **Container Health Checks**: A lightweight GET `/health` endpoint returns `{"status": "ok"}` for platform health-check pre-warming.

---

## 🚂 Deploying to Railway

This repository is pre-configured for instant deployment on Railway using either **Nixpacks** (`railway.toml`) or **Docker** (`Dockerfile`).

### Option 1: One-Click / GitHub Integration (Recommended)
1. Push this repository to GitHub.
2. Go to [Railway.app](https://railway.app) and create a **New Project** -> **Deploy from GitHub repo**.
3. Select your repository.
4. Railway will automatically detect `railway.toml` or `Dockerfile` and configure:
   - **Start Command**: `sh start.sh`
   - **Healthcheck Path**: `/health`
   - **Port**: Auto-assigned by Railway via `$PORT`.

### Option 2: Railway CLI Deployment
```bash
npm i -g @railway/cli
railway login
railway init
railway up
```

---

## ⚛️ Quantum Algorithm Description

The quantum simulation pipeline in `app/quantum.py` supports two distinct quantum entanglement protocols based on the requested `simulation_mode`:

### 1. Equilibrium Mode (`simulation_mode: "equilibrium"`) — GHZ State
1. **State Initialization**: For $N$ players ($N \le 5$), an $N$-qubit register $|00\dots 0\rangle$ and classical readout register are initialized.
2. **Entanglement Preparation**: 
   - A Hadamard gate $H$ is applied to qubit 0: $H|0\rangle = \frac{1}{\sqrt{2}}(|0\rangle + |1\rangle)$.
   - Cascaded Controlled-NOT ($CNOT$) gates entangle qubit 0 with all subsequent qubits $i \in \{1, \dots, N-1\}$, producing a maximally entangled $N$-qubit GHZ state:
     $$\psi_{GHZ} = \frac{1}{\sqrt{2}}\left(|00\dots 0\rangle + |11\dots 1\rangle\right)$$

### 2. Winning Mode (`simulation_mode: "winning"`) — W State
1. **W-State Construction**: Generates a balanced $N$-qubit W-state using parameterized $R_y$ and Controlled-$R_y$ ($CRY$) rotations:
   $$|W_N\rangle = \frac{1}{\sqrt{N}}\left(|100\dots 0\rangle + |010\dots 0\rangle + \dots + |000\dots 1\rangle\right)$$
   - **Qubit 0 Initial Rotation**: $\theta_0 = 2 \arccos\left(\sqrt{\frac{N-1}{N}}\right)$
   - **Cascaded Controlled Rotations**: $\theta_i = 2 \arccos\left(\sqrt{\frac{rem-1}{rem}}\right)$ with CNOT entanglement across adjacent qubits.
2. **Strategic Winning Matrix Output**: The LLM analyzes the single-excitation superposition to output a Strategic Winning Matrix Table detailing targeted binary winning states (exactly one `'1'`), exact local strategy rotation angles ($\theta$), winner vs. non-winner payoffs, and blackout avoidance mechanisms.

### 3. Gate Rationale & Purpose
- **Hadamard Gate ($H$)**: Placed on the first qubit to create an equal superposition of $|0\rangle$ and $|1\rangle$, removing deterministic bias.
- **Controlled-NOT Gates ($CNOT$)**: Links qubits to establish non-local entanglement across all players.
- **Parameterized Rotations ($R_y$ / $CRY$)**: Precisely splits amplitude weight among remaining unassigned qubits to construct balanced W-states.
- **Strategy Rotation Gates ($R_x$)**: Applies $X$-axis rotation ($\pi/2$) to each qubit, mapping classical choices into quantum superpositions.

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
2. **Quantum Outcome**: Observe the `dominant_strategy_binary` from the Qiskit execution counts. Note how non-zero off-diagonal state amplitudes in the GHZ or W state allow players to access Pareto-superior payoff outcomes unreachable in classical un-correlated play.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- API Key for OpenRouter, Google AI Studio, or OpenAI

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

#### Request Body Parameters
- `text` *(string, required)*: The game theory scenario description.
- `api_key` *(string, required)*: API key for the chosen AI provider.
- `provider` *(string, optional)*: `"OpenRouter"` (default), `"Google AI Studio"`, or `"OpenAI"`.
- `model` *(string, optional)*: Model override name (e.g., `gpt-4o`, `gemini-1.5-pro`).
- `simulation_mode` *(string, optional)*: `"equilibrium"` (default, GHZ state) or `"winning"` (W state).

```json
{
  "text": "Two prisoners are arrested for a crime...",
  "api_key": "sk-or-v1-...",
  "provider": "OpenRouter",
  "model": "",
  "simulation_mode": "equilibrium"
}
```

### 💻 How to Call from External Frontends

#### 1. JavaScript / Next.js / React (`fetch`)
```javascript
const analyzeGame = async () => {
  const response = await fetch("https://your-app.up.railway.app/analyze_game", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      text: "Two criminals are arrested by the police...",
      api_key: "sk-or-v1-...",
      provider: "OpenRouter", // "OpenRouter" | "Google AI Studio" | "OpenAI"
      simulation_mode: "winning" // "equilibrium" | "winning"
    })
  });

  const result = await response.json();
  console.log(result.markdown_response);
  console.log(result.processed_json);
};
```

#### 2. cURL
```bash
curl -X POST "https://your-app.up.railway.app/analyze_game" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Two suspects are arrested for a robbery...",
    "api_key": "sk-or-v1-...",
    "provider": "OpenRouter",
    "simulation_mode": "winning"
  }'
```

#### 3. Python (`requests`)
```python
import requests

response = requests.post(
    "https://your-app.up.railway.app/analyze_game",
    json={
        "text": "Two criminals are arrested by police...",
        "api_key": "sk-or-v1-...",
        "provider": "OpenRouter",
        "simulation_mode": "equilibrium"
    }
)
data = response.json()
print(data["markdown_response"])
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
      "simulation_mode": "equilibrium",
      "n_players": 2,
      "qubits_per_player": [1, 1],
      "total_qubits": 2,
      "quantum_counts": {"00": 512, "11": 512},
      "dominant_joint_action": "Alice: Cooperate, Bob: Cooperate",
      "joint_action_probabilities": {"Alice: Cooperate, Bob: Cooperate": 0.5},
      "total_shots": 1024,
      "entanglement_type": "2-Player (2-Qubit) EWL Quantum Game Protocol"
    }
  }
}
```

#### Response (Non-Game Theory Problem)
```json
"this is not game theory problem. Tip: Make sure to clearly define the players, their decisions/actions, and the payoff impact of those decisions."
```

---

### ⚡ 2. Direct Quantum Simulation Endpoint (`POST /run_game_quantum_only`)

Execute Qiskit quantum circuit simulations directly on `AerSimulator` without invoking LLMs or needing an API key. Pass a raw `GameTheorySchema` (players, actions, payoffs) and receive raw quantum probability distributions.

> 📁 **Schema Reference Files**: Request & response JSON templates are available in [schema/request_schema.json](file:///Users/ernest.pascual/Downloads/Development/quantum-gametheory/schema/request_schema.json) and [schema/response_schema.json](file:///Users/ernest.pascual/Downloads/Development/quantum-gametheory/schema/response_schema.json).

#### Request Payload (`POST /run_game_quantum_only`)
```json
{
  "is_game_theory": true,
  "players": [
    {
      "name": "Alice",
      "actions": ["Cooperate", "Defect", "Negotiate"]
    },
    {
      "name": "Bob",
      "actions": ["Cooperate", "Defect", "Negotiate"]
    }
  ],
  "payoff_matrix": {
    "Cooperate, Cooperate": [3.0, 3.0],
    "Cooperate, Defect": [0.0, 5.0],
    "Cooperate, Negotiate": [2.0, 2.0],
    "Defect, Cooperate": [5.0, 0.0],
    "Defect, Defect": [1.0, 1.0],
    "Defect, Negotiate": [4.0, 0.5],
    "Negotiate, Cooperate": [2.0, 2.0],
    "Negotiate, Defect": [0.5, 4.0],
    "Negotiate, Negotiate": [2.5, 2.5]
  },
  "narrative_context": "Two negotiating parties",
  "simulation_mode": "equilibrium"
}
```

#### cURL Example
```bash
curl -X POST "https://your-app.up.railway.app/run_game_quantum_only" \
  -H "Content-Type: application/json" \
  -d '{
    "is_game_theory": true,
    "players": [
      {"name": "Alice", "actions": ["Cooperate", "Defect"]},
      {"name": "Bob", "actions": ["Cooperate", "Defect"]}
    ],
    "payoff_matrix": {
      "Cooperate, Cooperate": [3.0, 3.0],
      "Cooperate, Defect": [0.0, 5.0],
      "Defect, Cooperate": [5.0, 0.0],
      "Defect, Defect": [1.0, 1.0]
    },
    "narrative_context": "Prisoner Dilemma",
    "simulation_mode": "winning"
  }'
```

#### JavaScript (`fetch`)
```javascript
const res = await fetch("https://your-app.up.railway.app/run_game_quantum_only", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    is_game_theory: true,
    players: [
      { name: "Alice", actions: ["Cooperate", "Defect"] },
      { name: "Bob", actions: ["Cooperate", "Defect"] }
    ],
    payoff_matrix: { "Cooperate, Cooperate": [3.0, 3.0] },
    narrative_context: "Direct test",
    simulation_mode: "equilibrium"
  })
});
const quantumResults = await res.json();
console.log(quantumResults.dominant_joint_action);
```

#### Response Output
```json
{
  "simulation_mode": "equilibrium",
  "n_players": 2,
  "qubits_per_player": [2, 2],
  "total_qubits": 4,
  "quantum_counts": {
    "0000": 268,
    "0001": 254,
    "0100": 249,
    "0101": 253
  },
  "dominant_joint_action": "Alice: Cooperate, Bob: Cooperate",
  "joint_action_probabilities": {
    "Alice: Cooperate, Bob: Cooperate": 0.2617,
    "Alice: Defect, Bob: Cooperate": 0.248,
    "Alice: Cooperate, Bob: Defect": 0.2432,
    "Alice: Defect, Bob: Defect": 0.2471
  },
  "total_shots": 1024,
  "entanglement_type": "2-Player (4-Qubit) EWL Quantum Game Protocol"
}
```

---

## 📁 Project Architecture

```text
quantum-gametheory/
├── app/
│   ├── __init__.py
│   ├── schemas.py       # Pydantic models (Player, GameTheorySchema, GameRequest, GameResponse)
│   ├── ai.py            # Multi-provider LLM parsing (OpenRouter, Gemini, OpenAI) and insight prompt dispatch
│   ├── quantum.py       # Qiskit simulation routines (GHZ state & W-state circuits with lazy imports)
│   ├── core.py          # Core workflow orchestration logic
│   └── main.py          # FastAPI server, CORS middleware, and Gradio UI mount
├── requirements.txt     # Python dependencies
├── railway.toml         # Railway Nixpacks deployment configuration
├── Dockerfile           # Production container build specification
├── start.sh             # Executable startup script with dynamic port binding
├── PYTHON_PACKAGE.md    # Packaging roadmap & Python SDK specifications
└── README.md            # Project overview & documentation
```

---

## 📦 Python Packaging Roadmap

For details on converting this workspace into a pip-installable library (`quantum-gametheory`), refer to [PYTHON_PACKAGE.md](file:///Users/ernest.pascual/Downloads/Development/quantum-gametheory/PYTHON_PACKAGE.md).

---

## 📄 License

MIT

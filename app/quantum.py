from app.schemas import GameTheorySchema

_SIMULATOR = None

def get_simulator():
    global _SIMULATOR
    if _SIMULATOR is None:
        from qiskit_aer import AerSimulator
        _SIMULATOR = AerSimulator()
    return _SIMULATOR

def process_quantum_entanglement(schema: GameTheorySchema) -> dict:
    n_players = len(schema.players)
    if n_players == 0:
        return {}

    from qiskit import QuantumCircuit, transpile

    simulator = get_simulator()

    # Initialize a quantum circuit with n qubits and n classical bits
    qc = QuantumCircuit(n_players, n_players)

    # 1. Create Maximally Entangled State (GHZ State)
    qc.h(0)
    for i in range(1, n_players):
        qc.cx(0, i)
        
    # 2. Apply strategy rotations 
    for i in range(n_players):
        qc.rx(1.57, i) # Pi/2 rotation

    # 3. Measurement
    qc.measure(range(n_players), range(n_players))

    # 4. Transpile and execute on Aer Simulator
    compiled_circuit = transpile(qc, simulator)
    result = simulator.run(compiled_circuit, shots=1024).result()
    counts = result.get_counts()

    # Find the most frequent quantum state
    best_state_binary = max(counts, key=counts.get)
    
    return {
        "quantum_counts": counts,
        "dominant_strategy_binary": best_state_binary,
        "total_shots": 1024,
        "entanglement_type": f"{n_players}-qubit GHZ state"
    }

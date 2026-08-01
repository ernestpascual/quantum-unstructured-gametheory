from app.schemas import GameTheorySchema

_SIMULATOR = None

def get_simulator():
    global _SIMULATOR
    if _SIMULATOR is None:
        from qiskit_aer import AerSimulator
        _SIMULATOR = AerSimulator()
    return _SIMULATOR

def create_w_circuit(num_players: int):
    """
    Generates a balanced W-state circuit for N qubits using parameterized rotations (Ry and CRY).
    W-state for N qubits: |W_N> = (1/sqrt(N)) * (|100...0> + |010...0> + ... + |000...1>)
    """
    import math
    from qiskit import QuantumCircuit
    
    qc = QuantumCircuit(num_players, num_players)
    if num_players == 0:
        return qc
    if num_players == 1:
        qc.x(0)
        return qc

    # Step 1: Initialize qubit 0 with Ry rotation angle theta = 2 * arccos(sqrt((N-1)/N))
    theta_0 = 2 * math.acos(math.sqrt((num_players - 1) / num_players))
    qc.ry(theta_0, 0)
    qc.x(0)

    # Step 2: Cascaded Controlled-Ry rotations for remaining qubits
    for i in range(1, num_players - 1):
        rem_qubits = num_players - i
        theta_i = 2 * math.acos(math.sqrt((rem_qubits - 1) / rem_qubits))
        qc.cry(theta_i, i - 1, i)
        qc.cx(i, i - 1)

    # Final CNOT to set the last qubit state
    qc.cx(num_players - 2, num_players - 1)
    
    return qc

def process_quantum_entanglement(schema: GameTheorySchema, simulation_mode: str = "equilibrium") -> dict:
    n_players = len(schema.players)
    if n_players == 0:
        return {}

    from qiskit import QuantumCircuit, transpile
    simulator = get_simulator()

    mode = (simulation_mode or "equilibrium").lower().strip()

    if mode == "winning":
        # Generate W state circuit where exactly one player wins ('1') safely without blackout
        qc = create_w_circuit(n_players)
        
        # Apply strategy rotations for competitive positioning
        for i in range(n_players):
            qc.rx(1.57, i) # Pi/2 rotation
            
        qc.measure(range(n_players), range(n_players))
        entanglement_label = f"{n_players}-qubit W state (Winning Mode)"
    else:
        # Standard GHZ state circuit for equilibrium correlation
        qc = QuantumCircuit(n_players, n_players)
        qc.h(0)
        for i in range(1, n_players):
            qc.cx(0, i)
            
        for i in range(n_players):
            qc.rx(1.57, i) # Pi/2 rotation

        qc.measure(range(n_players), range(n_players))
        entanglement_label = f"{n_players}-qubit GHZ state (Equilibrium Mode)"

    # Transpile and execute on Aer Simulator
    compiled_circuit = transpile(qc, simulator)
    result = simulator.run(compiled_circuit, shots=1024).result()
    counts = result.get_counts()

    # Find the dominant quantum state
    best_state_binary = max(counts, key=counts.get)
    
    return {
        "simulation_mode": mode,
        "quantum_counts": counts,
        "dominant_strategy_binary": best_state_binary,
        "total_shots": 1024,
        "entanglement_type": entanglement_label
    }

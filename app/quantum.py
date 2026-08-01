import math
from typing import List
from app.schemas import GameTheorySchema

_SIMULATOR = None

def get_simulator():
    global _SIMULATOR
    if _SIMULATOR is None:
        from qiskit_aer import AerSimulator
        _SIMULATOR = AerSimulator()
    return _SIMULATOR

def get_qubits_per_player(num_actions: int) -> int:
    """
    Allocates qubits per player based on action count:
    - 2 actions: 1 qubit (2 states: |0>, |1>)
    - 3-4 actions: 2 qubits (4 states: |00>, |01>, |10>, |11>)
    - 5 actions: 3 qubits (8 states: |000>..|100>)
    """
    if num_actions <= 2:
        return 1
    elif num_actions <= 4:
        return 2
    else:
        return 3

def create_ewl_entangling_gate(num_qubits: int, gamma: float = math.pi / 2):
    """
    Constructs the EWL J entangling operator matrix for N qubits.
    J = exp(i * gamma/2 * (X^N)).
    For gamma = pi/2, J = 1/sqrt(2) * (I^N + i * X^N).
    """
    from qiskit.circuit.library import UnitaryGate
    import numpy as np

    dim = 2 ** num_qubits
    # Pauli X operator tensor product across all qubits
    X = np.array([[0, 1], [1, 0]], dtype=complex)
    X_tensor = X
    for _ in range(1, num_qubits):
        X_tensor = np.kron(X_tensor, X)
    
    # J = cos(gamma/2) * I + i * sin(gamma/2) * X_tensor
    identity = np.eye(dim, dtype=complex)
    J_matrix = math.cos(gamma / 2.0) * identity + 1j * math.sin(gamma / 2.0) * X_tensor
    
    J_gate = UnitaryGate(J_matrix, label="J")
    J_dag_gate = UnitaryGate(J_matrix.conj().T, label="J†")
    return J_gate, J_dag_gate

def build_ewl_circuit(n_players: int, qubits_per_player: List[int]) -> tuple:
    """
    Builds an EWL quantum circuit:
    1. Apply J entangling operator across initial |0...0> qubits.
    2. Apply player strategy rotation gates U_i(theta, phi, lambda) per player.
    3. Apply J^dagger disentanglement operator.
    4. Measure all qubits.
    """
    from qiskit import QuantumCircuit
    
    total_qubits = sum(qubits_per_player)
    qc = QuantumCircuit(total_qubits, total_qubits)
    
    J_gate, J_dag_gate = create_ewl_entangling_gate(total_qubits, gamma=math.pi / 2)
    
    # 1. Apply J entangling operator
    qc.append(J_gate, range(total_qubits))
    
    # 2. Apply localized player strategy operators U_i
    qubit_offset = 0
    for p_idx, q_count in enumerate(qubits_per_player):
        for q in range(q_count):
            target_qubit = qubit_offset + q
            # EWL strategy gate U(theta, phi, lambda) with theta=pi/2, phi=0, lambda=pi/2
            qc.u(math.pi / 2, 0.0, math.pi / 2, target_qubit)
        qubit_offset += q_count

    # 3. Apply J^dagger disentanglement operator
    qc.append(J_dag_gate, range(total_qubits))
    
    # 4. Measurement
    qc.measure(range(total_qubits), range(total_qubits))
    
    return qc, total_qubits

def build_multi_qubit_w_circuit(n_players: int, qubits_per_player: List[int]) -> tuple:
    """
    Constructs a multi-qubit W-state circuit distributed across player strategy spaces:
    |W_N> = 1/sqrt(N) * (|100..0> + |010..0> + ... + |000..1>)
    """
    from qiskit import QuantumCircuit
    
    total_qubits = sum(qubits_per_player)
    qc = QuantumCircuit(total_qubits, total_qubits)
    
    # Map primary qubit index for each player
    player_primary_qubits = []
    offset = 0
    for q_count in qubits_per_player:
        player_primary_qubits.append(offset)
        offset += q_count
        
    # Construct W-state over player primary qubits using Ry and CRY gates
    if n_players >= 2:
        theta_0 = 2 * math.acos(math.sqrt((n_players - 1) / n_players))
        qc.ry(theta_0, player_primary_qubits[0])
        qc.x(player_primary_qubits[0])

        for i in range(1, n_players - 1):
            rem_players = n_players - i
            theta_i = 2 * math.acos(math.sqrt((rem_players - 1) / rem_players))
            qc.cry(theta_i, player_primary_qubits[i - 1], player_primary_qubits[i])
            qc.cx(player_primary_qubits[i], player_primary_qubits[i - 1])

        qc.cx(player_primary_qubits[n_players - 2], player_primary_qubits[n_players - 1])
        
    # Apply strategy rotations for competitive positioning across all qubits
    for q in range(total_qubits):
        qc.rx(math.pi / 2, q)
        
    qc.measure(range(total_qubits), range(total_qubits))
    return qc, total_qubits

def decode_quantum_counts_to_player_actions(counts: dict, schema: GameTheorySchema, qubits_per_player: List[int]) -> dict:
    """
    Decodes measurement bitstrings into player action tuples with explicit player labels.
    Example: "Player 1 (Alice): Cooperate, Player 2 (Bob): Defect"
    """
    action_counts = {}
    total_shots = sum(counts.values())
    
    for bitstring, count in counts.items():
        # Qiskit bitstring is right-to-left (qubit 0 is last char)
        rev_bits = bitstring[::-1]
        
        player_actions = []
        offset = 0
        
        for p_idx, q_count in enumerate(qubits_per_player):
            p_bits = rev_bits[offset : offset + q_count]
            action_idx = int(p_bits, 2)
            player = schema.players[p_idx]
            
            if action_idx < len(player.actions):
                chosen_action = player.actions[action_idx]
            else:
                chosen_action = player.actions[action_idx % len(player.actions)]
                
            player_actions.append(f"{player.name}: {chosen_action}")
            offset += q_count
            
        joint_action_key = ", ".join(player_actions)
        action_counts[joint_action_key] = action_counts.get(joint_action_key, 0) + count
        
    dominant_joint_action = max(action_counts, key=action_counts.get)
    action_probabilities = {k: round(v / total_shots, 4) for k, v in action_counts.items()}
    
    return {
        "joint_action_counts": action_counts,
        "joint_action_probabilities": action_probabilities,
        "dominant_joint_action": dominant_joint_action
    }

def process_quantum_entanglement(schema: GameTheorySchema, simulation_mode: str = "equilibrium") -> dict:
    n_players = len(schema.players)
    if n_players < 2:
        return {}

    from qiskit import transpile
    simulator = get_simulator()

    mode = (simulation_mode or "equilibrium").lower().strip()
    qubits_per_player = [get_qubits_per_player(len(p.actions)) for p in schema.players]

    if mode == "winning":
        qc, total_qubits = build_multi_qubit_w_circuit(n_players, qubits_per_player)
        entanglement_label = f"{n_players}-Player ({sum(qubits_per_player)}-Qubit) Multi-Action W-State Protocol"
    else:
        qc, total_qubits = build_ewl_circuit(n_players, qubits_per_player)
        entanglement_label = f"{n_players}-Player ({sum(qubits_per_player)}-Qubit) EWL Quantum Game Protocol"

    # Transpile and execute on Aer Simulator
    compiled_circuit = transpile(qc, simulator)
    result = simulator.run(compiled_circuit, shots=1024).result()
    counts = result.get_counts()

    # Decode bitstrings into dynamic n-ary player actions
    action_decoded = decode_quantum_counts_to_player_actions(counts, schema, qubits_per_player)

    return {
        "simulation_mode": mode,
        "n_players": n_players,
        "qubits_per_player": qubits_per_player,
        "total_qubits": total_qubits,
        "quantum_counts": counts,
        "dominant_joint_action": action_decoded["dominant_joint_action"],
        "joint_action_probabilities": action_decoded["joint_action_probabilities"],
        "total_shots": 1024,
        "entanglement_type": entanglement_label
    }

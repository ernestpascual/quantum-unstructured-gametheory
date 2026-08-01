import time
import logging
from typing import Union
from app.schemas import GameRequest, GameResponse, GameTheorySchema
from app.ai import parse_game_scenario, generate_quantum_insights
from app.quantum import process_quantum_entanglement

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("quantum_game_theory")

def run_game_analysis(request: GameRequest) -> Union[GameResponse, str]:
    if not request.api_key:
        raise ValueError("API Key is required.")

    start_time = time.time()
    logger.info(f"▶️ Starting Quantum Game Theory Analysis (Provider: {request.provider}, Mode: {request.simulation_mode})")

    # Step 1: Parsing using AI
    step1_start = time.time()
    logger.info("⏳ Step 1/3: Parsing scenario text into structured JSON schema via AI...")
    schema = parse_game_scenario(
        api_key=request.api_key,
        text=request.text,
        provider=request.provider,
        model=request.model or None
    )
    logger.info(f"✅ Step 1/3 Complete: Parsed in {time.time() - step1_start:.2f}s (is_game_theory={schema.is_game_theory}, players={len(schema.players)})")

    # Step 1.5: Validation check
    if not schema.is_game_theory:
        logger.warning("⚠️ Text was evaluated as non-game-theory. Terminating workflow.")
        return "this is not game theory problem. Tip: Make sure to clearly define the players, their decisions/actions, and the payoff impact of those decisions."

    if len(schema.players) > 5:
        raise ValueError("Maximum of 5 players allowed.")

    # Step 2: Quantum Simulation
    step2_start = time.time()
    logger.info(f"⏳ Step 2/3: Executing Qiskit Quantum Simulation on AerSimulator ({request.simulation_mode.upper()} mode)...")
    quantum_results = process_quantum_entanglement(
        schema=schema,
        simulation_mode=request.simulation_mode
    )
    logger.info(f"✅ Step 2/3 Complete: Quantum simulation executed in {time.time() - step2_start:.2f}s ({quantum_results.get('entanglement_type', '')})")

    # Step 3: Output Processing
    step3_start = time.time()
    logger.info("⏳ Step 3/3: Generating final Markdown report & executive insights via AI...")
    markdown_output = generate_quantum_insights(
        api_key=request.api_key,
        schema=schema,
        quantum_results=quantum_results,
        provider=request.provider,
        model=request.model or None,
        simulation_mode=request.simulation_mode
    )
    logger.info(f"✅ Step 3/3 Complete: Output report processed in {time.time() - step3_start:.2f}s")
    logger.info(f"🎉 Analysis Complete in {time.time() - start_time:.2f}s total.")

    return GameResponse(
        markdown_response=markdown_output,
        processed_json={
            "classical_schema": schema.model_dump(),
            "quantum_results": quantum_results
        }
    )

def run_game_quantum_only(schema: GameTheorySchema, simulation_mode: str = None) -> dict:
    if len(schema.players) < 2:
        raise ValueError("Minimum of 2 players required for quantum simulation.")
    if len(schema.players) > 5:
        raise ValueError("Maximum of 5 players allowed.")

    mode = simulation_mode or getattr(schema, "simulation_mode", "equilibrium")
    logger.info(f"⚡ Running Direct Quantum Simulation Only (Players: {len(schema.players)}, Mode: {mode})")
    
    start_time = time.time()
    quantum_results = process_quantum_entanglement(
        schema=schema,
        simulation_mode=mode
    )
    logger.info(f"✅ Direct Quantum Simulation Completed in {time.time() - start_time:.2f}s")
    return quantum_results

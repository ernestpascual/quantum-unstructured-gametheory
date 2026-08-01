from typing import Union
from app.schemas import GameRequest, GameResponse
from app.ai import parse_game_scenario, generate_quantum_insights
from app.quantum import process_quantum_entanglement

def run_game_analysis(request: GameRequest) -> Union[GameResponse, str]:
    if not request.api_key:
        raise ValueError("API Key is required.")

    # Step 1: Parse Text via selected AI provider
    schema = parse_game_scenario(
        api_key=request.api_key,
        text=request.text,
        provider=request.provider,
        model=request.model or None
    )

    # Step 2: Validation check
    if not schema.is_game_theory:
        return "this is not game theory problem. Tip: Make sure to clearly define the players, their decisions/actions, and the payoff impact of those decisions."

    if len(schema.players) > 5:
        raise ValueError("Maximum of 5 players allowed.")

    # Step 3: Quantum Processing based on simulation_mode ("equilibrium" GHZ state vs "winning" W state)
    quantum_results = process_quantum_entanglement(
        schema=schema,
        simulation_mode=request.simulation_mode
    )

    # Step 4: Generate Markdown Insights
    markdown_output = generate_quantum_insights(
        api_key=request.api_key,
        schema=schema,
        quantum_results=quantum_results,
        provider=request.provider,
        model=request.model or None,
        simulation_mode=request.simulation_mode
    )

    return GameResponse(
        markdown_response=markdown_output,
        processed_json={
            "classical_schema": schema.model_dump(),
            "quantum_results": quantum_results
        }
    )

from pydantic import BaseModel, Field
from typing import Dict, List, Union, Literal

class Player(BaseModel):
    name: str
    actions: List[str] = Field(..., min_length=2, max_length=5, description="List of 2 to 5 distinct actions for this player.")

class GameTheorySchema(BaseModel):
    is_game_theory: bool = Field(description="True if the text describes a valid game theory scenario. False otherwise.")
    players: List[Player] = Field(..., min_length=2, max_length=5, description="List of 2 to 5 players.")
    payoff_matrix: Dict[str, List[float]] = Field(
        ..., 
        description="Mapping of joint actions (comma-separated, matching player order) to a list of payoffs. Example for 3 players: 'ActionA,ActionB,ActionA': [1.0, 5.0, 0.0]"
    )
    narrative_context: str = Field(description="A brief summary of the conflict and incentives.")

class GameRequest(BaseModel):
    text: str
    api_key: str
    provider: str = Field(default="OpenRouter", description="AI Provider: OpenRouter, Google AI Studio, or OpenAI")
    model: str = Field(default="", description="Optional custom model name")
    simulation_mode: Literal["equilibrium", "winning"] = Field(default="equilibrium", description="Quantum Simulation Mode: 'equilibrium' (GHZ state) or 'winning' (W state)")

class GameResponse(BaseModel):
    markdown_response: str
    processed_json: dict

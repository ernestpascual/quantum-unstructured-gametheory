from pydantic import BaseModel, Field
from typing import Dict, List, Union

class Player(BaseModel):
    name: str
    actions: List[str]

class GameTheorySchema(BaseModel):
    is_game_theory: bool = Field(description="True if the text describes a valid game theory scenario. False otherwise.")
    players: List[Player] = Field(..., max_length=5, description="List of players, up to 5.")
    payoff_matrix: Dict[str, List[float]] = Field(
        ..., 
        description="Mapping of joint actions (comma-separated, matching player order) to a list of payoffs. Example: 'Cooperate,Defect': [0.0, 5.0]"
    )
    narrative_context: str = Field(description="A brief summary of the conflict and incentives.")

class GameRequest(BaseModel):
    text: str
    api_key: str

class GameResponse(BaseModel):
    markdown_response: str
    processed_json: dict

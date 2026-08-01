import json
import requests
from fastapi import HTTPException
from app.schemas import GameTheorySchema

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
LLM_MODEL = "openai/gpt-4o"

def call_openrouter(api_key: str, messages: list, response_format: dict = None) -> str:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": LLM_MODEL,
        "messages": messages
    }
    if response_format:
        payload["response_format"] = response_format
        
    response = requests.post(OPENROUTER_URL, headers=headers, json=payload)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()["choices"][0]["message"]["content"]

def parse_game_scenario(api_key: str, text: str) -> GameTheorySchema:
    system_prompt = """
    You are an expert game theory parser. Analyze the user's text and extract it into the provided JSON schema. 
    If the text does not describe a scenario involving actors, strategies, and payoffs, set 'is_game_theory' to false.
    """
    
    llm_response = call_openrouter(
        api_key=api_key,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Parse this scenario:\n\n{text}"}
        ],
        response_format={"type": "json_object"}
    )
    
    try:
        parsed_data = json.loads(llm_response)
        return GameTheorySchema(**parsed_data)
    except Exception:
        raise ValueError("Failed to parse LLM response into schema.")

def generate_quantum_insights(api_key: str, schema: GameTheorySchema, quantum_results: dict) -> str:
    insights_prompt = f"""
    You are an expert in quantum game theory. I have provided the classical game theory schema and the Qiskit quantum entanglement results.
    
    Schema: {schema.model_dump_json(indent=2)}
    Quantum Results: {json.dumps(quantum_results, indent=2)}
    
    Task:
    Provide a Markdown response containing:
    1. A clear table summarizing the players, their actions, and the classical payoff matrix.
    2. An analysis of the quantum results mapping the binary state back to their actions.
    3. Insights on how quantum entanglement changes the equilibrium.
    
    Do not output JSON, only return the raw Markdown text.
    """
    
    return call_openrouter(
        api_key=api_key,
        messages=[
            {"role": "system", "content": "You are a quantum game theory analyst."},
            {"role": "user", "content": insights_prompt}
        ]
    )

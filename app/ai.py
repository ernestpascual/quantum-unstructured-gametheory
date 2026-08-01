import json
import requests
from app.schemas import GameTheorySchema

DEFAULT_MODELS = {
    "OpenRouter": "openai/gpt-4o",
    "Google AI Studio": "gemini-1.5-pro",
    "OpenAI": "gpt-4o"
}

def call_openrouter(api_key: str, messages: list, model: str = None, response_format: dict = None) -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model or DEFAULT_MODELS["OpenRouter"],
        "messages": messages
    }
    if response_format:
        payload["response_format"] = response_format
        
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
    except requests.exceptions.RequestException as e:
        raise ValueError(f"OpenRouter connection error: {str(e)}")

    if response.status_code != 200:
        try:
            err_msg = response.json().get("error", {}).get("message", response.text)
        except Exception:
            err_msg = response.text
        raise ValueError(f"OpenRouter API error (HTTP {response.status_code}): {err_msg}")

    try:
        res_data = response.json()
        return res_data["choices"][0]["message"]["content"]
    except Exception as e:
        raise ValueError(f"Invalid OpenRouter response format: {str(e)}")

def call_openai(api_key: str, messages: list, model: str = None, response_format: dict = None) -> str:
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model or DEFAULT_MODELS["OpenAI"],
        "messages": messages
    }
    if response_format:
        payload["response_format"] = response_format
        
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
    except requests.exceptions.RequestException as e:
        raise ValueError(f"OpenAI connection error: {str(e)}")

    if response.status_code != 200:
        try:
            err_msg = response.json().get("error", {}).get("message", response.text)
        except Exception:
            err_msg = response.text
        raise ValueError(f"OpenAI API error (HTTP {response.status_code}): {err_msg}")

    try:
        res_data = response.json()
        return res_data["choices"][0]["message"]["content"]
    except Exception as e:
        raise ValueError(f"Invalid OpenAI response format: {str(e)}")

def call_google_ai_studio(api_key: str, messages: list, model: str = None, response_format: dict = None) -> str:
    model_name = model or DEFAULT_MODELS["Google AI Studio"]
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    # Convert OpenAI style messages to Gemini contents structure
    contents = []
    system_instruction = None
    
    for msg in messages:
        role = msg["role"]
        content = msg["content"]
        if role == "system":
            system_instruction = {"parts": [{"text": content}]}
        else:
            gemini_role = "user" if role == "user" else "model"
            contents.append({
                "role": gemini_role,
                "parts": [{"text": content}]
            })
            
    payload = {"contents": contents}
    if system_instruction:
        payload["systemInstruction"] = system_instruction
        
    if response_format and response_format.get("type") == "json_object":
        payload["generationConfig"] = {"responseMimeType": "application/json"}
        
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Google AI Studio connection error: {str(e)}")

    if response.status_code != 200:
        try:
            err_msg = response.json().get("error", {}).get("message", response.text)
        except Exception:
            err_msg = response.text
        raise ValueError(f"Google AI Studio API error (HTTP {response.status_code}): {err_msg}")

    try:
        res_data = response.json()
        return res_data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        raise ValueError(f"Invalid Google AI Studio response format: {str(e)}")

def call_ai(provider: str, api_key: str, messages: list, model: str = None, response_format: dict = None) -> str:
    prov_clean = (provider or "OpenRouter").strip()
    if prov_clean.lower() in ["openrouter", "open router"]:
        return call_openrouter(api_key, messages, model, response_format)
    elif prov_clean.lower() in ["google ai studio", "google", "gemini"]:
        return call_google_ai_studio(api_key, messages, model, response_format)
    elif prov_clean.lower() in ["openai", "gpt"]:
        return call_openai(api_key, messages, model, response_format)
    else:
        raise ValueError(f"Unsupported provider '{provider}'. Choose from: OpenRouter, Google AI Studio, OpenAI")

def parse_game_scenario(api_key: str, text: str, provider: str = "OpenRouter", model: str = None) -> GameTheorySchema:
    json_schema_str = json.dumps(GameTheorySchema.model_json_schema(), indent=2)
    system_prompt = f"""
    You are an expert game theory parser. Analyze the user's text and extract it into the following JSON schema:

    {json_schema_str}

    If the text does not describe a scenario involving actors, strategies, and payoffs, set 'is_game_theory' to false, set 'players' to [], set 'payoff_matrix' to {{}}, and 'narrative_context' to 'Not game theory'.
    Return ONLY valid JSON matching this schema.
    """
    
    llm_response = call_ai(
        provider=provider,
        api_key=api_key,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Parse this scenario:\n\n{text}"}
        ],
        model=model,
        response_format={"type": "json_object"}
    )
    
    clean_response = llm_response.strip()
    if clean_response.startswith("```"):
        lines = clean_response.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        clean_response = "\n".join(lines).strip()
    
    try:
        parsed_data = json.loads(clean_response)
        return GameTheorySchema(**parsed_data)
    except Exception as err:
        raise ValueError(
            f"Failed to parse LLM response into game theory schema. "
            f"Tip: Please ensure your text clearly defines the players, their decisions/actions, and the payoff impact of those decisions. "
            f"(Details: {err})"
        )

def generate_quantum_insights(api_key: str, schema: GameTheorySchema, quantum_results: dict, provider: str = "OpenRouter", model: str = None) -> str:
    insights_prompt = f"""
    You are an expert in quantum game theory who excels at explaining complex quantum concepts in simple, plain English. 
    I have provided the classical game theory schema and the Qiskit quantum entanglement results.
    
    Schema: {schema.model_dump_json(indent=2)}
    Quantum Results: {json.dumps(quantum_results, indent=2)}
    
    Task:
    Provide a Markdown response structured strictly as follows:
    
    1. **Overview**: A concise 2-sentence description summarizing the core problem, key actors, and high-level strategic dilemma.
    2. **Classical Game Matrix**: A clear table summarizing the players, their actions, and the classical payoff matrix.
    3. **Quantum Strategy Analysis**: An analysis mapping the binary measurement state back to specific player actions.
    4. **Equilibrium & Insights**: 
       Explain this section in simple, intuitive terms by breaking it down into 3 clear subsections:
       - **Why this Quantum State Result Occurred**: Explain in plain language why the GHZ state entanglement and rotation operations produced this specific result.
       - **What Happens During the Quantum State**: Explain what physically/conceptually happens when players' choices are entangled in superposition (how quantum entanglement removes independent betrayal/conflict).
       - **Why it is the Best Outcome**: Compare the quantum payoff against the classical Nash equilibrium to show why this outcome is optimal for all players (achieving Pareto optimality).
    
    Do not output JSON, only return the raw Markdown text.
    """
    
    return call_ai(
        provider=provider,
        api_key=api_key,
        messages=[
            {"role": "system", "content": "You are a quantum game theory analyst."},
            {"role": "user", "content": insights_prompt}
        ],
        model=model
    )

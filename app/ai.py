import json
import requests
from app.schemas import GameTheorySchema

DEFAULT_MODELS = {
    "OpenRouter": "google/gemini-3.6-flash",
    "Google AI Studio": "gemini-3.6-flash",
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
    You are an expert game theory parser specializing in multi-actor, multi-choice strategic games.
    Analyze the user's text and extract it into the following JSON schema:

    {json_schema_str}

    CRITICAL PARSING RULES:
    1. **Dynamic Player Capacity**: Extract between 2 and 5 players (`players` array size must be 2 to 5).
    2. **Multi-Action Options**: Each player can have anywhere from 2 to 5 distinct action choices (e.g. ['Cooperate', 'Defect', 'Compromise']). Do NOT restrict to binary choices if 3, 4, or 5 choices are described.
    3. **Complete Payoff Matrix**: Construct the `payoff_matrix` dictionary containing entries for EVERY joint action combination across all players.
       - Keys must be formatted as comma-separated player action names matching player order (e.g., 'Action1, Action2' for 2 players, or 'ActionA, ActionB, ActionC' for 3 players).
       - Values must be a JSON array of floats representing the payoffs for each player in that exact order (e.g., [1.0, 5.0] or [2.0, 0.0, -1.0]).
    4. **Non-Game Fallback**: If the text does not describe a scenario involving actors, strategies, and payoffs, set 'is_game_theory' to false, 'players' to [], 'payoff_matrix' to {{}}, and 'narrative_context' to 'Not game theory'.

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
            f"Tip: Please ensure your text clearly defines the players, their decisions/actions (2 to 5 actions per player), and the payoff impact of those decisions. "
            f"(Details: {err})"
        )

def generate_quantum_insights(api_key: str, schema: GameTheorySchema, quantum_results: dict, provider: str = "OpenRouter", model: str = None, simulation_mode: str = "equilibrium") -> str:
    mode = (simulation_mode or "equilibrium").lower().strip()

    if mode == "winning":
        insights_prompt = f"""
    You are a practical quantum game theory consultant who excels at giving clear, actionable business and strategic advice.
    I have provided the classical game theory schema and the Qiskit multi-qubit W-state quantum entanglement simulation results (Winning Mode).
    
    Schema: {schema.model_dump_json(indent=2)}
    Quantum Results: {json.dumps(quantum_results, indent=2)}
    
    CRITICAL FORMATTING RULES FOR LATEX & MARKDOWN:
    - Put every long mathematical equation or state vector on its own separate line wrapped in display math delimiters: \\[ equation \\]
    - Do NOT split simple numbers or basic arithmetic across multiple lines (write 15.0 + 4(3.0) = 27.0 inline naturally without broken math tags).
    - Insert double newlines between paragraphs and bullet points to ensure clean rendering.
    
    Task:
    Provide a Markdown response structured strictly as follows:
    
    1. **Overview & Initial Game Setup**:
       - **Problem Summary**: A concise 2-sentence description summarizing the core strategic conflict.
       - **Players & Decisions**: Explicitly list all participating players (2 to 5) and ALL available action/decision choices for each player (up to 5 actions per player).
       - **Complete Classical Payoff Matrix**: Render a clear, comprehensive markdown table showing ALL joint action combinations and the resulting payoff vector for each player.
    
    2. **Practical Player Action Guide**: A clear bulleted list detailing for EACH player by name:
       - **Recommended Action**: State the exact action name they should play to win from their multi-choice action set.
       - **Strategic Goal & Payoff**: Explain in plain terms what condition leads to their victory and the exact payoff reward.
    
    3. **Strategic Winning Matrix Table**: A clean markdown table presenting:
       - **Player Name**: Name of the player.
       - **Action to Play**: The specific classical action the player executes to achieve victory.
       - **Target Binary / Action State**: The binary state and corresponding action key representing their solo win.
       - **Local Strategy Parameter**: The angle $\\theta$ (e.g. $\\theta = \\pi/2$).
       - **Winner vs. Non-Winner Payoff**: The payoff for winning vs. non-winning players.
    
    4. **Preventing Mutual Collision & Blackouts**: A practical explanation of how the multi-qubit W-state superposition guarantees that exactly one player succeeds while preventing dangerous blackout/collision penalties. Show the state equation as a standalone block:
       \\[ |W_N\\rangle = \\frac{{1}}{{\\sqrt{{N}}}} \\left( |100\\dots\\rangle + |010\\dots\\rangle + \\dots \\right) \\]
    
    5. **Actionable Executive Insights & Results Analysis**:
       - **Why This Strategy Works**: Practical breakdown of how quantum correlation coordinates multi-action choices without collusion.
       - **Actionable Execution Plan**: High-level advice for players on how to implement this strategy in real-world negotiations or competitive scenarios.
    
    Do not output JSON, only return raw Markdown text.
    """
    else:
        insights_prompt = f"""
    You are an expert in quantum game theory who excels at explaining complex quantum concepts in simple, plain English. 
    I have provided the classical game theory schema and the Qiskit Eisert-Wilkens-Lewenstein (EWL) quantum game protocol simulation results (Equilibrium Mode).
    
    Schema: {schema.model_dump_json(indent=2)}
    Quantum Results: {json.dumps(quantum_results, indent=2)}
    
    Task:
    Provide a Markdown response structured strictly as follows:
    
    1. **Overview & Initial Game Setup**:
       - **Problem Summary**: A concise 2-sentence description summarizing the core strategic conflict.
       - **Players & Decisions**: Explicitly list all participating players (2 to 5) and ALL available action/decision choices for each player (up to 5 actions per player).
       - **Complete Classical Payoff Matrix**: Render a clear, comprehensive markdown table showing ALL joint action combinations and the resulting payoff vector for each player.
    
    2. **EWL Quantum Strategy & Probability Analysis**: An analysis mapping the resulting EWL probability distribution back to specific multi-player action choices.
    
    3. **Quantum Nash Equilibrium & Insights**: 
       Explain this section in simple, intuitive terms by breaking it down into 3 clear subsections:
       - **Quantum Nash Equilibrium**: Identify the true Quantum Nash Equilibrium resulting from the EWL protocol ($J \\to U_1 \\otimes \\dots \\otimes U_n \\to J^\\dagger$).
       - **How Quantum Interference Prevents Defection Traps**: Explain in plain language how destructive quantum interference cancels out classical betrayal/defection states.
       - **Why it is the Best Outcome**: Compare the EWL quantum payoff against the classical Nash equilibrium to show why this outcome is optimal for all players (achieving Pareto optimality).
    
    Do not output JSON, only return raw Markdown text with valid LaTeX for math symbols (e.g. $J = exp(i * gamma/2 * X^N)$).
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

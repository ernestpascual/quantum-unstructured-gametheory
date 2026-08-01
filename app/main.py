from typing import Union
from fastapi import FastAPI, HTTPException
import gradio as gr

from app.schemas import GameRequest, GameResponse
from app.core import run_game_analysis

app = FastAPI(title="Quantum Game Theory API")

# --- API Endpoints ---

@app.post("/analyze_game", response_model=Union[GameResponse, str])
async def api_analyze_game(request: GameRequest):
    try:
        return run_game_analysis(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- Gradio UI ---

def gradio_interface(api_key, text):
    try:
        request = GameRequest(api_key=api_key, text=text)
        result = run_game_analysis(request)
        
        if isinstance(result, str):
            return result, {}
            
        return result.markdown_response, result.processed_json
    except Exception as e:
        return f"**Error:** {str(e)}", {}

with gr.Blocks(title="Quantum Game Theory Analyzer") as demo:
    gr.Markdown("# 🎲 Quantum Game Theory Analyzer")
    gr.Markdown("Enter an OpenRouter API key and describe a game theory scenario. The system will parse it, run a quantum simulation using Qiskit, and return an entangled strategy analysis.")
    
    with gr.Row():
        with gr.Column(scale=1):
            api_key_input = gr.Textbox(label="OpenRouter API Key", type="password", placeholder="sk-or-v1-...")
            problem_input = gr.Textbox(label="Game Theory Scenario", lines=6, placeholder="Example: Two criminals are arrested...")
            submit_btn = gr.Button("Analyze Quantum Strategy", variant="primary")
            
        with gr.Column(scale=1):
            markdown_output = gr.Markdown(label="Analysis Insights")
            json_output = gr.JSON(label="Processed Context (Classical + Quantum)")

    submit_btn.click(
        fn=gradio_interface,
        inputs=[api_key_input, problem_input],
        outputs=[markdown_output, json_output]
    )

# Mount Gradio on FastAPI at root /
app = gr.mount_gradio_app(app, demo, path="/")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

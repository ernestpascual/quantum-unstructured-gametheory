from typing import Union
from fastapi import FastAPI, HTTPException
import gradio as gr

from app.schemas import GameRequest, GameResponse
from app.core import run_game_analysis

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Quantum Game Theory API")

# Enable CORS for external frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Endpoints ---

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/analyze_game", response_model=Union[GameResponse, str])
async def api_analyze_game(request: GameRequest):
    try:
        return run_game_analysis(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- Gradio UI & Export Helpers ---

def export_to_markdown(markdown_text: str):
    import tempfile
    if not markdown_text or not markdown_text.strip() or markdown_text.startswith("**Error"):
        return gr.DownloadButton(value=None)
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".md", mode="w", encoding="utf-8")
    temp_file.write(markdown_text)
    temp_file.close()
    return gr.DownloadButton(value=temp_file.name, visible=True)

def export_to_pdf(markdown_text: str):
    import tempfile
    import re
    
    if not markdown_text or not markdown_text.strip() or markdown_text.startswith("**Error"):
        return gr.DownloadButton(value=None)
        
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        pdf_path = temp_file.name
        temp_file.close()
        
        doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=16, leading=20, spaceAfter=10)
        h2_style = ParagraphStyle('DocH2', parent=styles['Heading2'], fontSize=13, leading=16, spaceBefore=10, spaceAfter=6)
        body_style = ParagraphStyle('DocBody', parent=styles['Normal'], fontSize=10, leading=14, spaceAfter=6)
        
        story = [Paragraph("Quantum Game Theory Analysis Report", title_style), Spacer(1, 10)]
        
        for line in markdown_text.splitlines():
            line_clean = line.strip()
            if not line_clean:
                continue
            if line_clean.startswith("#"):
                heading_text = line_clean.lstrip("#").strip()
                story.append(Paragraph(heading_text, h2_style))
            else:
                text_escaped = line_clean.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                text_escaped = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text_escaped)
                text_escaped = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text_escaped)
                story.append(Paragraph(text_escaped, body_style))
                
        doc.build(story)
        return gr.DownloadButton(value=pdf_path, visible=True)
    except Exception as e:
        print(f"PDF generation error: {e}")
        return gr.DownloadButton(value=None)

EXAMPLE_SCENARIO = """Two suspects are arrested by the police. The police have insufficient evidence for a conviction, and, having separated both prisoners, visit each of them to offer the same deal:
- If one confesses (Defects) and the other remains silent (Cooperates), the betrayer goes free and the silent accomplice receives a 10-year sentence.
- If both remain silent (Cooperate), both prisoners serve 1 year in prison.
- If both confess (Defect), both receive a 5-year sentence.

Payoff matrix rewards: Cooperate,Cooperate = [1, 1], Cooperate,Defect = [0, 10], Defect,Cooperate = [10, 0], Defect,Defect = [5, 5]."""

def gradio_interface(provider, api_key, model, simulation_mode, text):
    try:
        request = GameRequest(
            provider=provider,
            api_key=api_key,
            model=model.strip(),
            simulation_mode=simulation_mode,
            text=text
        )
        result = run_game_analysis(request)
        
        if isinstance(result, str):
            return result, {}
            
        return result.markdown_response, result.processed_json
    except Exception as e:
        return f"**Error:** {str(e)}", {}

def load_example():
    return EXAMPLE_SCENARIO

custom_css = """
/* Static Full Viewport Layout with Independent Scrollable Columns */
body, html {
    height: 100vh;
    margin: 0;
    padding: 0;
    overflow: hidden !important;
}

#root, .gradio-container {
    height: 100vh !important;
    max-height: 100vh !important;
    display: flex;
    flex-direction: column;
}

.main-container {
    flex: 1;
    height: calc(100vh - 120px) !important;
    overflow: hidden !important;
}

.scrollable-column {
    height: 100% !important;
    max-height: 100% !important;
    overflow-y: auto !important;
    padding-right: 12px;
}
"""

with gr.Blocks(title="Quantum Game Theory Analyzer", css=custom_css) as demo:
    gr.Markdown("# 👨🏻‍🔬 Quantum Game Theory Analyzer")
    
    with gr.Accordion("📖 Instructions & Simple Example (Click to expand)", open=False):
        gr.Markdown("""
        ### How to use this tool:
        1. **Select an AI Provider**: Choose between **OpenRouter**, **Google AI Studio**, or **OpenAI**.
        2. **Enter API Key**: Paste your corresponding API key into the password field.
        3. **Select Quantum Simulation Mode**:
           - **Equilibrium (GHZ State)**: Analyzes quantum entanglement correlations for joint Nash/Pareto equilibria.
           - **Winning (W State)**: Generates a Strategic Winning Matrix Table showing targeted binary winning states, rotation angles ($\theta$), payoffs, and blackout avoidance.
        4. **Describe a Scenario**: Input a text description of a conflict or strategic interaction involving players, actions, and payoffs.
        5. **Run Simulation**: Click **Analyze Strategy**.
        6. **Export Results**: Download the generated report as a **Markdown (`.md`)** file or a compiled **PDF document (`.pdf`)**.
        """)
    
    with gr.Row(elem_classes=["main-container"]):
        with gr.Column(scale=1, elem_classes=["scrollable-column"]):
            gr.Markdown("### ⚙️ Scenario Configuration")
            provider_input = gr.Dropdown(
                choices=["OpenRouter", "Google AI Studio", "OpenAI"],
                value="OpenRouter",
                label="AI Provider"
            )
            api_key_input = gr.Textbox(label="API Key", type="password", placeholder="Enter provider API Key...")
            model_input = gr.Textbox(label="Model Name (Optional)", placeholder="Leave blank for default (e.g. gpt-4o, gemini-1.5-pro)")
            mode_input = gr.Dropdown(
                choices=["equilibrium", "winning"],
                value="equilibrium",
                label="Quantum Simulation Mode",
                info="'equilibrium' = GHZ State Correlation | 'winning' = W State Strategic Winning Matrix"
            )
            problem_input = gr.Textbox(label="Game Theory Scenario", lines=6, placeholder="Example: Two criminals are arrested...")
            
            with gr.Row():
                example_btn = gr.Button("💡 Load Example", variant="secondary")
                submit_btn = gr.Button("🚀 Analyze Strategy", variant="primary")
            
            gr.Markdown("### 📥 Export Report")
            with gr.Row():
                export_md_btn = gr.DownloadButton("📄 Download Markdown (.md)")
                export_pdf_btn = gr.DownloadButton("📕 Download PDF (.pdf)")
            
        with gr.Column(scale=1, elem_classes=["scrollable-column"]):
            gr.Markdown("### 📊 Quantum & Classical Analysis")
            markdown_output = gr.Markdown(label="Analysis Insights", latex_delimiters=[{"left": "$", "right": "$", "display": False}, {"left": "$$", "right": "$$", "display": True}])
            json_output = gr.JSON(label="Processed Context (Classical + Quantum)")

    example_btn.click(
        fn=load_example,
        outputs=[problem_input]
    )

    submit_btn.click(
        fn=gradio_interface,
        inputs=[provider_input, api_key_input, model_input, mode_input, problem_input],
        outputs=[markdown_output, json_output]
    )

    export_md_btn.click(
        fn=export_to_markdown,
        inputs=[markdown_output],
        outputs=[export_md_btn]
    )

    export_pdf_btn.click(
        fn=export_to_pdf,
        inputs=[markdown_output],
        outputs=[export_pdf_btn]
    )

# Mount Gradio on FastAPI at root /
app = gr.mount_gradio_app(app, demo, path="/")

def find_available_port(host: str = "0.0.0.0", start_port: int = 8000, max_attempts: int = 100) -> int:
    import socket
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((host, port))
                return port
            except OSError:
                continue
    raise RuntimeError(f"Could not find an open port starting from {start_port}")

if __name__ == "__main__":
    import os
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    requested_port = int(os.getenv("PORT", 8000))
    port = find_available_port(host=host, start_port=requested_port)

    print(f"🚀 Starting Quantum Game Theory App on http://{host}:{port}")
    print(f"  - Gradio UI: http://{host}:{port}/")
    print(f"  - API Docs:  http://{host}:{port}/docs")
    
    uvicorn.run("app.main:app", host=host, port=port, reload=True)

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import os
import tempfile
import pandas as pd
import requests

from detector import load_test_runs, calculate_test_statistics, detect_flaky_tests
from agent import run_agent

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TEST_RUNS_CSV = os.path.join(os.path.dirname(__file__), 'data', 'test_runs.csv')

@app.get("/api/flaky-tests")
def get_flaky_tests():
    if not os.path.exists(TEST_RUNS_CSV):
        return []
    
    try:
        df = load_test_runs(TEST_RUNS_CSV)
        stats = calculate_test_statistics(df)
        
        results = []
        for stat in stats:
            test_name = stat['test_name']
            
            score = 0
            if stat['total_runs'] > 0:
                score = stat['fail_count'] / stat['total_runs']
                
            results.append({
                "test_name": test_name,
                "score": int(score * 100),
                "pass_rate": stat.get('pass_count', 0) / stat.get('total_runs', 1),
                "runs": stat.get('total_runs', 0),
                "avg_ms": int(stat.get('avg_duration', 0) * 1000),
                "last_failed": "2026-06-03", 
                "category": test_name.split('_')[1].capitalize() if len(test_name.split('_')) > 1 else "General"
            })
        return results
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        content = await file.read()
        
        # Write to a temporary file
        import tempfile
        ext = os.path.splitext(file.filename)[1]
        if not ext:
            ext = ".csv"
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
            
        # Parse and normalize using the universal parser
        from parsers.universal_parser import load_file
        df, mapping, warnings = load_file(tmp_path)
        
        # Save standard schema to the expected project CSV location
        os.makedirs(os.path.dirname(TEST_RUNS_CSV), exist_ok=True)
        df.to_csv(TEST_RUNS_CSV, index=False)
        
        # Clean up
        os.remove(tmp_path)
        
        return {
            "filename": file.filename, 
            "status": "success",
            "mapping": mapping,
            "warnings": warnings
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/run-agent")
def api_run_agent():
    # In a real app this would be a background task
    try:
        report = run_agent()
        return {"status": "started", "report": report}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/chat")
async def chat(request: dict):
    # Proxy to ollama
    try:
        ollama_payload = dict(request)
        if "model" not in ollama_payload:
            from config import OLLAMA_MODEL
            ollama_payload["model"] = OLLAMA_MODEL
            
        # Ensure we don't stream for simplicity in the UI
        ollama_payload["stream"] = False

        response = requests.post("http://127.0.0.1:11434/api/chat", json=ollama_payload, timeout=3)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        # Fallback to Groq
        from config import GROQ_API_KEY, GROQ_MODEL
        if not GROQ_API_KEY:
            return {"error": f"Ollama failed ({e}) and GROQ_API_KEY is not set."}
            
        try:
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            # Convert Ollama payload to OpenAI format
            payload = {
                "model": GROQ_MODEL,
                "messages": request.get("messages", [])
            }
            res = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers)
            res.raise_for_status()
            
            groq_data = res.json()
            # Convert OpenAI response format back to Ollama format
            return {
                "message": {
                    "role": "assistant",
                    "content": groq_data["choices"][0]["message"]["content"]
                }
            }
        except Exception as groq_e:
            return {"error": f"Fallback to Groq failed: {groq_e}"}

@app.get("/api/reports")
def get_reports():
    return {}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

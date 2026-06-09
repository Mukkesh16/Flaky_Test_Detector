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
        os.makedirs(os.path.dirname(TEST_RUNS_CSV), exist_ok=True)
        with open(TEST_RUNS_CSV, "wb") as f:
            f.write(content)
        return {"filename": file.filename, "status": "success"}
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
        response = requests.post("http://127.0.0.1:11434/api/chat", json=request)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/reports")
def get_reports():
    return {}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

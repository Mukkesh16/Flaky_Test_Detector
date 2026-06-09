# Flaky Test Detector & Explainer

A tool that automatically finds flaky tests in your test suite, analyses why they fail, and suggests fixes using a local large language model (Ollama + Llama 3).

---

## Team Information

**Team Name:** Team Syndicates

**Team Members:**
- Mukkesh
- Mohamed Irsath
- Vigneshkumar
- Ragul

---

## Project Title

**Flaky Test Detector & Explainer**

---

## Live Demo

🔗 Live Demo: *To be added*

---

## Business Problem

Flaky tests—tests that pass or fail intermittently without code changes—are a common pain point for modern software teams. They:
- Waste developer time debugging false failures
- Slow down CI/CD pipelines
- Undermine confidence in automated testing

Our goal is to automatically surface flaky tests and provide understandable explanations for their behavior.

---

## Solution Overview

The system performs the following steps:
1. Analyzes historical test execution data
2. Detects flaky tests and calculates a flakiness score
3. Collects failure logs for the identified tests
4. Generates AI‑driven root‑cause explanations
5. Suggests possible fixes
6. Produces a concise investigation report
7. Shows results in an interactive dashboard

---

## Features

### Flaky Test Detection
- Finds tests with mixed pass/fail outcomes
- Computes a flakiness score and categorises severity

### AI‑Powered Root‑Cause Analysis
- Leverages Ollama + Llama 3 locally
- Analyses failure traces and outputs:
  - Root cause description
  - Confidence score
  - Recommended fixes

### Autonomous Agent Workflow
- Loads test data
- Detects flaky tests
- Collects logs
- Generates explanations
- Saves results and creates reports

### Interactive Dashboard
- Upload CSV of test results
- Browse flaky tests and AI explanations
- Trigger investigations on demand
- Download generated reports
- Chat with the data for ad‑hoc queries

---

## System Architecture

```
CSV / JSON Input
    │
    ▼
Detector Engine
    │
    ▼
Flaky Test Identification
    │
    ▼
Agent Workflow
    │
    ▼
Ollama (Llama 3)
    │
    ▼
Root‑Cause Analysis
    │
    ▼
SQLite Database
    │
    ▼
Streamlit Dashboard
    │
    ▼
Reports & Insights
```

---

## Setup & Installation

### Prerequisites
- Python 3.9+
- Ollama installed locally with the `llama3` model (`ollama run llama3`)

### Installation Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/Mukkesh16/Flaky_Test_Detector.git
   cd Flaky_Test_Detector
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate   # on Windows
   ```
3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application
Start the dashboard with:
```bash
streamlit run Flaky_Test_Detector/app.py
```
(If you prefer the full Windows path, use `.\venv\Scripts\python.exe -m streamlit run Flaky_Test_Detector\app.py`.)

---

## Tech Stack
- **Frontend:** Streamlit
- **Backend:** Python 3
- **Data Processing:** Pandas
- **Database:** SQLite + SQLAlchemy
- **AI/LLM:** Ollama (Llama 3)

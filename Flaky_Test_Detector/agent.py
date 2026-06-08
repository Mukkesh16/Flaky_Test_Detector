"""
agent.py - Autonomous AI Agent for Flaky Test Investigation

Orchestrates the full workflow:
  1. Load test execution history
  2. Detect flaky tests
  3. Load failure logs
  4. Generate AI explanations for each flaky test
  5. Create a structured investigation report
  6. Store results in SQLite database
  7. Export report to JSON
"""

import os
import sys
import json
import logging
import io

# Force UTF-8 output on Windows to support unicode characters
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from datetime import datetime, timezone
from typing import List, Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Resolve the project directory (where this file lives)
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Step 1: Load Test Data
# ---------------------------------------------------------------------------

def load_test_data(csv_path: str):
    """
    Loads test execution history from a CSV file using the detector module.

    Args:
        csv_path (str): Absolute path to the test_runs.csv file.

    Returns:
        pd.DataFrame: The loaded test run data.

    Raises:
        FileNotFoundError: If the CSV file does not exist.
        ValueError: If the CSV is empty or missing required columns.
    """
    from detector import load_test_runs

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Test data file not found: {csv_path}")

    df = load_test_runs(csv_path)

    if df.empty:
        raise ValueError("Test data CSV is empty.")

    logger.info(f"Loaded {len(df)} test run records from {os.path.basename(csv_path)}")
    return df


# ---------------------------------------------------------------------------
# Step 2: Detect Flaky Tests
# ---------------------------------------------------------------------------

def detect_flaky(df) -> List[Dict[str, Any]]:
    """
    Runs the flaky detection engine on the loaded test data.

    Args:
        df (pd.DataFrame): Test run data.

    Returns:
        List[Dict[str, Any]]: List of detected flaky tests with scores.
    """
    from detector import detect_flaky_tests

    flaky_tests = detect_flaky_tests(df)
    logger.info(f"Detected {len(flaky_tests)} flaky test(s)")
    return flaky_tests


# ---------------------------------------------------------------------------
# Step 3: Load Failure Logs
# ---------------------------------------------------------------------------

def load_failure_logs(json_path: str) -> Dict[str, List[Dict[str, str]]]:
    """
    Loads failure log entries from a JSON file.

    Args:
        json_path (str): Absolute path to failure_logs.json.

    Returns:
        Dict[str, List[Dict[str, str]]]: Mapping of test_name -> list of log entries.

    Raises:
        FileNotFoundError: If the JSON file does not exist.
        json.JSONDecodeError: If the JSON is malformed.
    """
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Failure logs file not found: {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    logger.info(f"Loaded failure logs for {len(data)} test(s)")
    return data


# ---------------------------------------------------------------------------
# Step 4: Generate AI Explanations
# ---------------------------------------------------------------------------

def generate_explanations(
    flaky_tests: List[Dict[str, Any]],
    failure_logs: Dict[str, List[Dict[str, str]]]
) -> List[Dict[str, Any]]:
    """
    Generates AI root cause explanations for each flaky test.

    For each flaky test, extracts the relevant failure log entries and calls
    the explainer module to generate a structured explanation.

    Args:
        flaky_tests (List[Dict]): List of detected flaky tests.
        failure_logs (Dict): Failure log data keyed by test name.

    Returns:
        List[Dict[str, Any]]: Flaky test dicts enriched with AI explanation fields.
    """
    from explainer import generate_explanation

    enriched_results = []

    for test in flaky_tests:
        test_name = test["test_name"]
        score = test["flakiness_score"]

        # Extract log messages for this test
        log_entries = failure_logs.get(test_name, [])
        log_messages = [entry.get("error", "") for entry in log_entries if entry.get("error")]

        if not log_messages:
            log_messages = ["No failure logs available"]

        logger.info(f"  → Explaining: {test_name} (score={score}, logs={len(log_messages)})")

        explanation = generate_explanation(test_name, score, log_messages)

        # Merge the explanation into the test result
        enriched = {
            "test_name": test_name,
            "flakiness_score": score,
            "severity": test.get("severity", "UNKNOWN"),
            "total_runs": test.get("total_runs", 0),
            "pass_count": test.get("pass_count", 0),
            "fail_count": test.get("fail_count", 0),
        }

        if "error" in explanation:
            enriched["root_cause"] = f"[Error] {explanation['error']}"
            enriched["confidence"] = "N/A"
            enriched["recommended_fix"] = "Unable to generate explanation."
        else:
            enriched["root_cause"] = explanation.get("root_cause", "")
            enriched["confidence"] = explanation.get("confidence", "")
            enriched["recommended_fix"] = explanation.get("recommended_fix", "")

        enriched_results.append(enriched)

    return enriched_results


# ---------------------------------------------------------------------------
# Step 5: Create Report
# ---------------------------------------------------------------------------

def create_report(enriched_tests: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Creates a structured investigation report.

    Args:
        enriched_tests (List[Dict]): Flaky tests with AI explanations.

    Returns:
        Dict[str, Any]: The full report object.
    """
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_flaky_tests": len(enriched_tests),
        "tests": enriched_tests,
    }
    logger.info(f"Report created with {len(enriched_tests)} test(s)")
    return report


# ---------------------------------------------------------------------------
# Step 6: Save to Database
# ---------------------------------------------------------------------------

def save_to_database(flaky_tests: List[Dict[str, Any]]) -> None:
    """
    Stores flaky test detection results in the SQLite database.

    Args:
        flaky_tests (List[Dict]): List of detected flaky tests (raw, pre-explanation).
    """
    from database import initialize_database, save_detection_results

    try:
        initialize_database()
        save_detection_results(flaky_tests)
        logger.info("Results saved to SQLite database")
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise


# ---------------------------------------------------------------------------
# Step 7: Export Report to JSON
# ---------------------------------------------------------------------------

def export_report(report: Dict[str, Any], output_path: str) -> None:
    """
    Exports the investigation report to a JSON file.

    Args:
        report (Dict): The structured report dictionary.
        output_path (str): Absolute path for the output JSON file.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    logger.info(f"Report exported to {output_path}")


# ---------------------------------------------------------------------------
# Agent Orchestrator
# ---------------------------------------------------------------------------

def run_agent() -> Dict[str, Any]:
    """
    Orchestrates the full flaky test investigation workflow.

    Executes all 7 steps in sequence: load data, detect flaky tests,
    load failure logs, generate AI explanations, build report,
    save to database, and export as JSON.

    Returns:
        Dict[str, Any]: The generated investigation report.
    """
    csv_path = os.path.join(PROJECT_DIR, "data", "test_runs.csv")
    logs_path = os.path.join(PROJECT_DIR, "data", "failure_logs.json")
    report_path = os.path.join(PROJECT_DIR, "reports", "flaky_test_report.json")

    print("\n" + "=" * 50)
    print("  FLAKY TEST INVESTIGATION AGENT")
    print("=" * 50 + "\n")

    # ---- Step 1 ----
    print("[STEP 1/7] Loading test data...")
    try:
        df = load_test_data(csv_path)
    except (FileNotFoundError, ValueError) as e:
        logger.error(f"Step 1 failed: {e}")
        return {"error": str(e)}

    # ---- Step 2 ----
    print("[STEP 2/7] Detecting flaky tests...")
    flaky_tests = detect_flaky(df)

    if not flaky_tests:
        print("\n[OK] No flaky tests detected. Pipeline complete.")
        return {"generated_at": datetime.now(timezone.utc).isoformat(), "tests": []}

    for ft in flaky_tests:
        print(f"  [!] {ft['test_name']}  score={ft['flakiness_score']}  severity={ft['severity']}")

    # ---- Step 3 ----
    print("\n[STEP 3/7] Loading failure logs...")
    try:
        failure_logs = load_failure_logs(logs_path)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Step 3 failed: {e}")
        return {"error": str(e)}

    # ---- Step 4 ----
    print("\n[STEP 4/7] Generating AI explanations...")
    enriched_results = generate_explanations(flaky_tests, failure_logs)

    # ---- Step 5 ----
    print("\n[STEP 5/7] Creating report...")
    report = create_report(enriched_results)

    # ---- Step 6 ----
    print("[STEP 6/7] Saving to database...")
    try:
        save_to_database(flaky_tests)
    except Exception as e:
        logger.error(f"Database save failed (non-fatal): {e}")

    # ---- Step 7 ----
    print("[STEP 7/7] Exporting report...")
    export_report(report, report_path)

    # ---- Summary ----
    print("\n" + "=" * 50)
    print("  INVESTIGATION COMPLETE")
    print("=" * 50 + "\n")

    for test in enriched_results:
        print(f"Test: {test['test_name']}")
        print(f"  Flakiness Score : {test['flakiness_score']}")
        print(f"  Severity        : {test['severity']}")
        print(f"  Root Cause      : {test['root_cause'][:100]}...")
        print(f"  Confidence      : {test['confidence']}")
        print(f"  Recommended Fix : {test['recommended_fix'][:100]}...")
        print()

    print(f"[>>] Full report saved to: {report_path}")
    print("=" * 50 + "\n")

    return report


# ---------------------------------------------------------------------------
# Standalone Execution
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    run_agent()

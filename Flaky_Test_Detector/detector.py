import pandas as pd
import os
import logging
from typing import List, Dict, Any
from database import initialize_database, save_detection_results

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_test_runs(file_path: str) -> pd.DataFrame:
    """
    Loads test execution history from a CSV file.
    
    Args:
        file_path (str): Path to the CSV file.
        
    Returns:
        pd.DataFrame: DataFrame containing test run data.
        
    Raises:
        FileNotFoundError: If the file does not exist.
        pd.errors.EmptyDataError: If the file is empty.
        ValueError: If required columns are missing.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Test run file not found: {file_path}")
        
    try:
        df = pd.read_csv(file_path)
    except pd.errors.EmptyDataError:
        raise pd.errors.EmptyDataError(f"The file {file_path} is empty.")
        
    # Standardize column names based on common patterns
    col_mapping = {
        'duration_seconds': 'duration',
        'time': 'duration',
        'run_time': 'duration',
        'run_date': 'timestamp',
        'date': 'timestamp',
        'result': 'status',
        'outcome': 'status',
        'name': 'test_name',
        'error_type': 'status' # Log files usually list errors
    }
    df.rename(columns={k: v for k, v in col_mapping.items() if k in df.columns}, inplace=True)
    
    # Fill in missing required columns with safe defaults
    if 'test_name' not in df.columns:
        df['test_name'] = df.iloc[:, 0] if not df.empty and len(df.columns) > 0 else 'Unknown_Test'
        
    if 'status' not in df.columns:
        df['status'] = 'failed' # Default to failed if it's just an error log
        
    if 'duration' not in df.columns:
        df['duration'] = 0.0
        
    if 'timestamp' not in df.columns:
        df['timestamp'] = pd.Timestamp.now()
        
    # Normalize statuses to 'passed' and 'failed' so the statistics logic works
    df['status'] = df['status'].astype(str).str.lower()
    df['status'] = df['status'].apply(lambda x: 'passed' if 'pass' in x or 'success' in x or x == 'ok' else 'failed')
        
    return df


def calculate_test_statistics(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Calculates statistics for each test in the dataset.
    
    Args:
        df (pd.DataFrame): The test runs DataFrame.
        
    Returns:
        List[Dict[str, Any]]: A list of dictionaries with test statistics.
    """
    stats = []
    
    # Group by test_name
    grouped = df.groupby('test_name')
    
    for test_name, group in grouped:
        total_runs = len(group)
        pass_count = len(group[group['status'].str.lower() == 'passed'])
        fail_count = len(group[group['status'].str.lower() == 'failed'])
        avg_duration = round(group['duration'].mean(), 2)
        
        stats.append({
            "test_name": test_name,
            "total_runs": total_runs,
            "pass_count": pass_count,
            "fail_count": fail_count,
            "avg_duration": avg_duration
        })
        
    return stats


def detect_flaky_tests(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Identifies flaky tests from test statistics.
    
    A test is flaky if it has > 0 passes and > 0 failures.
    Calculates flakiness_score and assigns severity.
    
    Args:
        df (pd.DataFrame): The test runs DataFrame.
        
    Returns:
        List[Dict[str, Any]]: Flaky tests sorted by flakiness_score descending.
    """
    stats = calculate_test_statistics(df)
    flaky_tests = []
    
    for stat in stats:
        if stat['pass_count'] > 0 and stat['fail_count'] > 0:
            score = round(stat['fail_count'] / stat['total_runs'], 2)
            
            # Risk Classification
            if score <= 0.20:
                severity = "LOW"
            elif score <= 0.50:
                severity = "MEDIUM"
            else:
                severity = "HIGH"
                
            flaky_tests.append({
                "test_name": stat['test_name'],
                "flaky": True,
                "flakiness_score": score,
                "severity": severity,
                "total_runs": stat['total_runs'],
                "pass_count": stat['pass_count'],
                "fail_count": stat['fail_count']
            })
            
    # Sort descending by flakiness_score
    flaky_tests.sort(key=lambda x: x['flakiness_score'], reverse=True)
    return flaky_tests


def analyze_test_trends(df: pd.DataFrame) -> Dict[str, Dict[str, str]]:
    """
    Analyzes trend patterns for tests.
    
    Args:
        df (pd.DataFrame): The test runs DataFrame.
        
    Returns:
        Dict[str, Dict[str, str]]: A dictionary mapping test_name to its trend.
    """
    # Sort by timestamp to ensure chronological order
    df_sorted = df.sort_values(by=['test_name', 'timestamp'])
    grouped = df_sorted.groupby('test_name')
    
    trends = {}
    
    for test_name, group in grouped:
        statuses = group['status'].str.lower().tolist()
        
        if len(statuses) < 2:
            trends[test_name] = {"trend": "Insufficient Data"}
            continue
            
        fail_count = statuses.count('failed')
        if fail_count == 0:
            trends[test_name] = {"trend": "Mostly Passing"}
        else:
            # Simple heuristic: if the recent half has more failures than the older half
            mid_point = len(statuses) // 2
            older_half = statuses[:mid_point]
            recent_half = statuses[mid_point:]
            
            recent_fails = recent_half.count('failed')
            older_fails = older_half.count('failed')
            
            if recent_fails > older_fails:
                trends[test_name] = {"trend": "Increasing Failure Rate"}
            else:
                trends[test_name] = {"trend": "Stable Failures"}
                
    return trends


if __name__ == "__main__":
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'test_runs.csv')
    
    try:
        df = load_test_runs(csv_path)
        flaky_results = detect_flaky_tests(df)
        
        # Print CLI Report
        print("\n==================================")
        print("FLAKY TEST REPORT")
        print("==================================\n")
        
        if not flaky_results:
            print("No flaky tests detected.")
        else:
            for result in flaky_results:
                print(f"{result['test_name']}")
                print(f"Score: {result['flakiness_score']:.2f}")
                print(f"Severity: {result['severity']}")
                print()
                
        print("==================================\n")
        
        # Save to DB
        initialize_database()
        save_detection_results(flaky_results)
        
    except Exception as e:
        logger.error(f"Error during execution: {e}")

import os
import sys
import pandas as pd
import pytest

# Ensure the parent directory is in the import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from detector import (
    load_test_runs,
    calculate_test_statistics,
    detect_flaky_tests,
    analyze_test_trends
)

@pytest.fixture
def sample_csv_data(tmp_path):
    """Fixture providing a temporary valid CSV file for loading."""
    df = pd.DataFrame({
        "test_name": ["login_test", "login_test", "search_test"],
        "status": ["passed", "failed", "passed"],
        "duration": [1.0, 1.5, 0.8],
        "timestamp": ["2026-06-08T10:00:00", "2026-06-08T10:05:00", "2026-06-08T10:10:00"]
    })
    filepath = tmp_path / "test_data.csv"
    df.to_csv(filepath, index=False)
    return str(filepath)

@pytest.fixture
def sample_dataframe():
    """Fixture providing an in-memory DataFrame for logic testing."""
    return pd.DataFrame({
        "test_name": ["login_test"] * 10 + ["search_test"] * 5 + ["stable_test"] * 5,
        "status": ["passed"]*7 + ["failed"]*3 + ["failed"]*2 + ["passed"]*3 + ["passed"]*5,
        "duration": [1.0]*10 + [2.0]*5 + [0.5]*5,
        "timestamp": [f"2026-06-08T10:{i:02d}:00" for i in range(20)]
    })

# --- Tests for load_test_runs ---

def test_load_test_runs_success(sample_csv_data):
    df = load_test_runs(sample_csv_data)
    assert not df.empty
    assert list(df.columns) == ["test_name", "status", "duration", "timestamp"]
    assert len(df) == 3

def test_load_test_runs_missing_file():
    with pytest.raises(FileNotFoundError):
        load_test_runs("nonexistent_file.csv")

def test_load_test_runs_empty_file(tmp_path):
    filepath = tmp_path / "empty.csv"
    filepath.touch()
    with pytest.raises(pd.errors.EmptyDataError):
        load_test_runs(str(filepath))

def test_load_test_runs_invalid_columns(tmp_path):
    # The new robust parser handles invalid columns by filling in defaults
    df = pd.DataFrame({"wrong_col": ["t1", "t2"], "status": ["passed", "failed"]})
    filepath = tmp_path / "invalid.csv"
    df.to_csv(filepath, index=False)
    
    loaded_df = load_test_runs(str(filepath))
    
    # It should automatically infer or default the missing columns
    assert 'test_name' in loaded_df.columns
    assert 'duration' in loaded_df.columns
    assert 'timestamp' in loaded_df.columns
    
    # test_name should default to the first column if no name column exists
    assert loaded_df['test_name'].iloc[0] == "t1"
    # duration should default to 0.0
    assert loaded_df['duration'].iloc[0] == 0.0

# --- Tests for calculate_test_statistics ---

def test_calculate_test_statistics(sample_dataframe):
    stats = calculate_test_statistics(sample_dataframe)
    
    # Check login_test
    login_stat = next(s for s in stats if s['test_name'] == 'login_test')
    assert login_stat['total_runs'] == 10
    assert login_stat['pass_count'] == 7
    assert login_stat['fail_count'] == 3
    assert login_stat['avg_duration'] == 1.0

# --- Tests for detect_flaky_tests ---

def test_detect_flaky_tests(sample_dataframe):
    flaky = detect_flaky_tests(sample_dataframe)
    
    # Should only return login_test and search_test, because stable_test has 0 fails
    assert len(flaky) == 2
    
    names = [f['test_name'] for f in flaky]
    assert "stable_test" not in names
    
    # Search test: 5 runs, 2 fails, 3 passes -> score = 0.40
    # Login test: 10 runs, 3 fails, 7 passes -> score = 0.30
    # Flaky tests should be sorted descending by score
    assert flaky[0]['test_name'] == 'search_test'
    assert flaky[0]['flakiness_score'] == 0.40
    assert flaky[0]['severity'] == 'MEDIUM'
    
    assert flaky[1]['test_name'] == 'login_test'
    assert flaky[1]['flakiness_score'] == 0.30
    assert flaky[1]['severity'] == 'MEDIUM'

def test_severity_classification():
    # Construct specific DataFrame to hit all severities
    df = pd.DataFrame({
        "test_name": ["low_risk"]*10 + ["med_risk"]*10 + ["high_risk"]*10,
        "status": ["failed"]*2 + ["passed"]*8 +    # 0.20 score (LOW)
                  ["failed"]*5 + ["passed"]*5 +    # 0.50 score (MEDIUM)
                  ["failed"]*6 + ["passed"]*4,     # 0.60 score (HIGH)
        "duration": [1.0]*30,
        "timestamp": [f"2026-06-08T10:{i:02d}:00" for i in range(30)]
    })
    
    flaky = detect_flaky_tests(df)
    
    high = next(f for f in flaky if f['test_name'] == 'high_risk')
    med = next(f for f in flaky if f['test_name'] == 'med_risk')
    low = next(f for f in flaky if f['test_name'] == 'low_risk')
    
    assert high['severity'] == "HIGH"
    assert med['severity'] == "MEDIUM"
    assert low['severity'] == "LOW"

# --- Tests for analyze_test_trends ---

def test_analyze_test_trends():
    df = pd.DataFrame({
        "test_name": ["stable_fail"]*4 + ["increasing_fail"]*4 + ["mostly_pass"]*4,
        "status": ["failed", "passed", "failed", "passed"] +  # 1 fail older, 1 fail newer -> Stable
                  ["passed", "passed", "failed", "failed"] +  # 0 fail older, 2 fail newer -> Increasing
                  ["passed", "passed", "passed", "passed"],   # Mostly passing
        "duration": [1.0]*12,
        "timestamp": [f"2026-06-08T10:{i:02d}:00" for i in range(12)]
    })
    
    trends = analyze_test_trends(df)
    
    assert trends['stable_fail']['trend'] == "Stable Failures"
    assert trends['increasing_fail']['trend'] == "Increasing Failure Rate"
    assert trends['mostly_pass']['trend'] == "Mostly Passing"

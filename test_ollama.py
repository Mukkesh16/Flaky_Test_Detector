from explainer import generate_explanation

def run_test():
    test_name = "login_test"
    score = 0.33
    logs = [
        "Timeout waiting for element",
        "Connection reset"
    ]
    
    print("Sending prompt to local Ollama model 'llama3' via explainer module...\n")
    result = generate_explanation(test_name, score, logs)
    
    if "error" in result:
        print(f"Failed to generate explanation:\n{result['error']}")
    else:
        print(f"Root Cause: {result['root_cause']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Recommended Fix: {result['recommended_fix']}")

if __name__ == "__main__":
    run_test()

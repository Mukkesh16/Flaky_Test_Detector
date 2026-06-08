import os
import logging
import re
import ollama

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_explanation(test_name: str, score: float, logs: list[str]) -> dict:
    """
    Generate an AI explanation for a flaky test failure using the local Ollama model.
    
    Args:
        test_name (str): The name of the test.
        score (float): The flakiness score.
        logs (list[str]): The failure logs as a list of strings.
        
    Returns:
        dict: A dictionary containing the parsed root cause, confidence, 
              and recommended fix, or an error message.
    """
    logger.info(f"Generating explanation for {test_name}")
    
    prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "rootcause.txt")
    
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_template = f.read()
    except FileNotFoundError:
        error_msg = f"Prompt template {prompt_path} not found."
        logger.error(error_msg)
        return {"error": error_msg}
        
    formatted_logs = "\n".join(logs)
    prompt = prompt_template.format(test_name=test_name, score=score, logs=formatted_logs)
    
    try:
        response = ollama.chat(model='llama3', messages=[
            {
                'role': 'user',
                'content': prompt,
            },
        ])
        logger.info("Ollama response received")
        content = response['message']['content']
        
        # Parse the structured response
        root_cause_match = re.search(r"Root Cause:\s*(.*?)(?=Confidence:|Recommended Fix:|$)", content, re.DOTALL | re.IGNORECASE)
        confidence_match = re.search(r"Confidence:\s*(.*?)(?=Root Cause:|Recommended Fix:|$)", content, re.DOTALL | re.IGNORECASE)
        fix_match = re.search(r"Recommended Fix:\s*(.*?)(?=Root Cause:|Confidence:|$)", content, re.DOTALL | re.IGNORECASE)
        
        if not (root_cause_match and confidence_match and fix_match):
            logger.error("Invalid response format received from Ollama.")
            return {"error": "Invalid response format received from model."}
            
        return {
            "test_name": test_name,
            "root_cause": root_cause_match.group(1).strip(),
            "confidence": confidence_match.group(1).strip(),
            "recommended_fix": fix_match.group(1).strip()
        }
        
    except ollama.ResponseError as e:
        logger.error(f"Ollama API Error: {e}")
        return {"error": f"Ollama API Error: {e}"}
    except Exception as e:
        # Handling connection timeout, missing model, etc.
        error_msg = str(e).lower()
        if 'connect' in error_msg or 'timeout' in error_msg:
            logger.error("Connection failed")
            return {"error": "Connection failed or timeout. Is Ollama running?"}
        else:
            logger.error(f"Unexpected error: {e}")
            return {"error": f"An unexpected error occurred: {e}"}

if __name__ == "__main__":
    # Standalone test mode
    test_name_sample = "login_test"
    score_sample = 0.33
    logs_sample = [
        "Timeout waiting for element",
        "Connection reset"
    ]
    
    result = generate_explanation(test_name_sample, score_sample, logs_sample)
    
    print("\n=================================")
    print("AI ROOT CAUSE ANALYSIS")
    print("=================================\n")
    print(f"Test:\n{test_name_sample}\n")
    
    if "error" in result:
        print(f"Error:\n{result['error']}")
    else:
        print(f"Root Cause:\n{result.get('root_cause', '')}\n")
        print(f"Confidence:\n{result.get('confidence', '')}\n")
        print(f"Recommended Fix:\n{result.get('recommended_fix', '')}")
    
    print("\n=================================")

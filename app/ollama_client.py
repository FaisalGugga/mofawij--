# app/ollama_client.py
import requests
import json
import time

def query_ollama(prompt, model="qwen:32b", max_retries=3):
    """Send a chat request to local Ollama instance with retries"""
    retries = 0
    last_error = None
    
    while retries < max_retries:
        try:
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={"model": model, "prompt": prompt},
                timeout=30  # Shorter timeout
            )
            
            # Check if the request was successful
            response.raise_for_status()
            
            # Parse the response
            result = response.json()
            return result.get('response', '')
            
        except requests.exceptions.ConnectionError as e:
            last_error = e
            retries += 1
            if retries < max_retries:
                time.sleep(1)  # Wait before retrying
            else:
                return f"Error: Cannot connect to Ollama server after {max_retries} attempts. Make sure it's running."
        except requests.exceptions.Timeout:
            return "Error: Ollama server request timed out. The model might be processing a complex query."
        except requests.exceptions.RequestException as e:
            return f"Error communicating with Ollama: {str(e)}"
        except json.JSONDecodeError:
            return "Error: Received invalid response from Ollama server"

    return f"Error: Failed to connect to Ollama server after {max_retries} attempts."

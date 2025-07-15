import requests

def ollama_agent_message(agent_name, history):
        # Compose a prompt for the agent
        prompt = f"You are {agent_name}, a player in a social deduction game. Here is the recent discussion:\n"
        for msg in history[-5:]:
            prompt += f"{msg['speaker']}: {msg['text']}\n"
        prompt += f"What do you say next? Keep it short and in-character."
        data = {
            "model": "qwen7b",
            "prompt": prompt,
            "stream": False
        }
        try:
            response = requests.post("http://localhost:11434/api/generate", json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result.get('response', '').strip()
        except Exception as e:
            return "(remains silent)"
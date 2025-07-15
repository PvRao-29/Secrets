import requests
import json
from engine import Role
import random

AGENT_RULES_CONTEXT = '''
GAME RULES & ROLE KNOWLEDGE:
- 7 players: 4 Good (Whistleblower, Detective, Cop, President), 3 Conspirators (Don, Assassin, Infiltrator).
- 5 missions: Rounds 1-3 & 5 require 1 fail to fail; Round 4 requires 2 fails.
- Leader rotates, proposes a team of size depending on round.
- All vote Approve/Reject; 5 consecutive rejections ⇒ Conspirators win.
- Failed mission triggers emergency vote to reveal President.
- Good wins upon 3 successful missions; Conspirators win upon 3 failures.
- If Good completes 3 successful missions then Assassin may guess Whistleblower. If correct, Conspirators win.

ROLE OBJECTIVES:
- Good (Whistleblower, Detective, Cop, President): Succeed in 3 missions or avoid assassination.
- Conspirators (Don, Assassin, Infiltrator): Fail 3 missions or assassinate the Whistleblower after 3 Good wins.

ROLE KNOWLEDGE:
- Whistleblower: Knows who the Don and Assassin are.
- Detective: Knows two candidates, one is the Whistleblower, one is the Don (but not which is which).
- Infiltrator: Knows who the Don and Assassin are.
- Don: Knows who the Assassin is.
- Assassin: Knows who the Don is.
- Cop, President: No special knowledge.

IMPORTANT:
- Never reveal or speculate about your own or anyone else's role, even indirectly.
- Never claim a player name is invalid or not in the game.
- Never reference the rules, the AI, or the system. Stay in character as a player.
- Always participate in discussion, especially on early missions. Avoid excessive caution or refusal.
- Agree or disagree with others, build consensus, and reference the discussion naturally.
- Use your memory, votes, and mission history to inform your statements and suggestions.
- If you have nothing to add, say something neutral or supportive (e.g., "Let's give this team a try.", "I agree with the leader.", "Sounds good to me.").
'''

def _sanitize_agent_output(text, player_names):
    # Remove any role reveals or meta statements
    roles = ["cop", "detective", "president", "don", "assassin", "infiltrator", "whistleblower"]
    for role in roles:
        text = text.replace(f"({role})", "").replace(f"{role.capitalize()}: ", "")
    # Remove any claims about invalid names
    for name in player_names:
        text = text.replace(f"{name} is not a valid character name", "")
        text = text.replace(f"{name} is not a valid role", "")
    # Remove meta/system/AI references
    meta_phrases = ["as an ai", "as a language model", "i am an ai", "i am a language model", "system", "rules", "not a valid"]
    for phrase in meta_phrases:
        text = text.replace(phrase, "")
    # Remove any accidental double colons or extra whitespace
    text = text.replace("::", ":").strip()
    return text

def ollama_agent_message(player, history, missions, votes):
    player_names = [p['speaker'] for p in history[-10:]]
    prompt = AGENT_RULES_CONTEXT + "\n"
    prompt += (
        f"You are {player.name}, playing as a secret role. "
        "You are in a social deduction game.\n"
        "Recent discussion:\n"
    )
    for msg in history[-5:]:
        prompt += f"{msg['speaker']}: {msg['text']}\n"
    prompt += "\nWhat do you say next? Keep it short, in-character, and never reveal or speculate about any roles. If you agree with someone, say so. If you disagree, say so. If you have nothing to add, say something neutral or supportive."
    data = {
        "model": "qwen7b",
        "prompt": prompt,
        "stream": False
    }
    r = requests.post("http://localhost:11434/api/generate", json=data, timeout=30)
    try:
        response = r.json().get("response", "").strip()
    except Exception:
        lines = r.text.strip().splitlines()
        response = ""
        for line in lines:
            try:
                obj = json.loads(line)
                if "response" in obj:
                    response = obj["response"].strip()
                    break
            except Exception:
                continue
    if not response:
        response = "(remains silent)"
    response = _sanitize_agent_output(response, player_names)
    # If after sanitizing, response is empty, give a neutral fallback
    if not response.strip():
        response = "Let's give this team a try." if random.random() < 0.5 else "I agree with the leader."
    return response
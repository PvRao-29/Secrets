import requests
import json
from engine import Role
import random
from helpers import _format_beliefs, _format_history


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

def ollama_agent_message(player, history, missions, votes, round_number, current_team):
    player_names = [p['speaker'] for p in history[-10:]]
    history_slice = history[-8:]
    prompt = AGENT_RULES_CONTEXT + "\n"
    prompt += (
        f"You are {player.name}. Round {round_number} is underway in a 7-player social deduction game.\n"
        f"Proposed mission team: {', '.join(p.name for p in current_team)}\n"
        f"Your private beliefs: {_format_beliefs(player.memory['beliefs'])}\n"
        f"Your mission history: {missions}\n"
        f"Your voting history: {votes}\n"
        "Recent discussion:\n" + _format_history(history_slice) + "\n\n"
        "Respond in-character as a concise sentence or two. Do not reveal roles."
    )
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

def ollama_agent_vote(player, team, history, missions, votes, round_number):
    player_names = [p['speaker'] for p in history[-10:]]
    history_slice = history[-8:]
    prompt = AGENT_RULES_CONTEXT + "\n"
    prompt += (
        f"You are {player.name}. Round {round_number}. A vote to approve the team is happening.\n"
        f"Proposed team: {', '.join(p.name for p in team)}\n"
        f"Your private beliefs: {_format_beliefs(player.memory['beliefs'])}\n"
        f"Your mission history: {missions}\n"
        f"Your voting history: {votes}\n"
        "Recent discussion:\n" + _format_history(history_slice) + "\n\n"
        "Should you vote Approve? Reply ONLY with a single character 'Y' or 'N'."
    )
    data = {
        "model": "qwen7b",
        "prompt": prompt,
        "stream": False
    }
    r = requests.post("http://localhost:11434/api/generate", json=data, timeout=30)
    try:
        response = r.json().get("response", "").strip().upper()
    except Exception:
        lines = r.text.strip().splitlines()
        response = ""
        for line in lines:
            try:
                obj = json.loads(line)
                if "response" in obj:
                    response = obj["response"].strip().upper()
                    break
            except Exception:
                continue
    if not response or response[0] not in ['Y', 'N']:
        response = random.choice(['Y', 'N'])
    return response[0]

def ollama_agent_mission_action(player, team, history, missions, votes, round_number):
    player_names = [p['speaker'] for p in history[-10:]]
    history_slice = history[-8:]
    prompt = AGENT_RULES_CONTEXT + "\n"
    prompt += (
        f"You are {player.name}. Round {round_number}. The mission is underway.\n"
        f"Mission team: {', '.join(p.name for p in team)}\n"
        f"Your private beliefs: {_format_beliefs(player.memory['beliefs'])}\n"
        f"Your mission history: {missions}\n"
        f"Your voting history: {votes}\n"
        "Recent discussion:\n" + _format_history(history_slice) + "\n\n"
        "Should you help the mission succeed or sabotage it? Reply ONLY with 'P' (Pass) or 'F' (Fail)."
    )
    data = {
        "model": "qwen7b",
        "prompt": prompt,
        "stream": False
    }
    r = requests.post("http://localhost:11434/api/generate", json=data, timeout=30)
    try:
        response = r.json().get("response", "").strip().upper()
    except Exception:
        lines = r.text.strip().splitlines()
        response = ""
        for line in lines:
            try:
                obj = json.loads(line)
                if "response" in obj:
                    response = obj["response"].strip().upper()
                    break
            except Exception:
                continue
    if not response or response[0] not in ['P', 'F']:
        # Default: good always pass, evil random
        if player.role in [Role.DON, Role.ASSASSIN, Role.INFILTRATOR]:
            response = random.choice(['P', 'F'])
        else:
            response = 'P'
    return response[0]
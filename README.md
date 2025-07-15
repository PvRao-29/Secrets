# SECRETS: Fate Awaits

A cinematic, AI-powered social deduction game for your terminal.

---

## 🎭 What is SECRETS?

SECRETS is a 7-player social deduction game inspired by classics like Avalon and Secret Hitler, but with a modern, hacker-movie twist. Play as a lone human against a cast of AI-powered agents, each with their own hidden roles, motives, and personalities. Can you outwit the conspirators and survive the shadows?

- **Cinematic terminal experience** with animated intros, neon colors, and dramatic pacing.
- **AI agents** powered by [Ollama](https://ollama.com/) and the Qwen 2.5 Coder 7B model, generating real-time table talk and strategy.
- **Imperfect information**: Roles, alliances, and betrayals—no two games are the same.
- **Discussion phase**: Argue, accuse, and strategize in a lively, LLM-driven chat before every mission.

---

## 🕹️ How to Play

1. **Start the game**: Launch from your terminal. Enjoy the cinematic intro and main menu.
2. **Read the rules**: Press `R` at the main menu for a quick overview.
3. **Begin a game**: Press `S` to start. You’ll be assigned a secret role.
4. **Discussion phase**: Chat with AI agents (powered by Qwen) before each mission. Type `/skip` to fast-forward during development.
5. **Propose and vote**: Take turns proposing teams and voting on missions. Watch for betrayals!
6. **Victory or defeat**: Win as the Good team by completing missions, or as the Conspirators by sabotaging them.

---

## 🚀 Setup & Requirements

1. **Python 3.8+**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Install [Ollama](https://ollama.com/download) and pull the Qwen model:**
   ```bash
   ollama pull qwen:2.5-coder-7b
   ollama serve
   ```
4. **Run the game:**
   ```bash
   python engine.py
   ```

---

## ✨ Features

- Animated ASCII art intro and transitions
- Stylish, readable terminal UI
- Real-time, LLM-powered agent discussion
- Dynamic, replayable deduction gameplay
- Dev tools: `/skip` command for fast testing

---

## 🧑‍💻 Credits

- **Game Design & Code:** [Your Name]
- **AI Integration:** [Ollama](https://ollama.com/), Qwen 2.5 Coder 7B
- **ASCII Art:** [pyfiglet](https://github.com/pwaller/pyfiglet)

---

## 📜 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

> "Trust no one. The truth is out there." 
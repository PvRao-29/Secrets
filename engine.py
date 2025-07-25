from enum import Enum, auto
import random, time, math
import curses
import itertools
from helpers import *
from aesthetics import *
from agents import *
import pyfiglet
import requests
import datetime

class Role(Enum):
    WHISTLEBLOWER = auto()
    DETECTIVE = auto()
    COP = auto()
    PRESIDENT = auto()
    DON = auto()
    ASSASSIN = auto()
    INFILTRATOR = auto()
    
class Player:
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.alive = True
        self.known_roles = {}
        self.memory = {
            "history": [],
            "missions": [],
            "votes": [],
            # beliefs: {player_name: trust_score}, positive = trust, negative = suspicion
            "beliefs": {}
        }
    
    def receive_initial_info(self, all_players):
        if self.role == Role.WHISTLEBLOWER:
            # Whistleblower knows Don and Assassin
            don = next(p for p in all_players if p.role == Role.DON)
            assassin = next(p for p in all_players if p.role == Role.ASSASSIN)
            self.known_roles[Role.DON] = [don]
            self.known_roles[Role.ASSASSIN] = [assassin]
        elif self.role == Role.DETECTIVE:
            # Detective knows two candidates: Whistleblower & Don (ambiguous)
            wb = next(p for p in all_players if p.role == Role.WHISTLEBLOWER)
            don = next(p for p in all_players if p.role == Role.DON)
            self.known_roles['detective_candidates'] = [wb, don]
        elif self.role == Role.INFILTRATOR:
            # Infiltrator knows Don and Assassin
            don = next(p for p in all_players if p.role == Role.DON)
            assassin = next(p for p in all_players if p.role == Role.ASSASSIN)
            self.known_roles[Role.DON] = [don]
            self.known_roles[Role.ASSASSIN] = [assassin]
        elif self.role == Role.DON:
            # Don knows Assassin
            assassin = next(p for p in all_players if p.role == Role.ASSASSIN)
            self.known_roles[Role.ASSASSIN] = [assassin]
        elif self.role == Role.ASSASSIN:
            # Assassin knows Don
            don = next(p for p in all_players if p.role == Role.DON)
            self.known_roles[Role.DON] = [don]
        # Cop, President have no initial info

    def initialize_beliefs(self, all_players):
        # Start neutral (0) for all other players
        for p in all_players:
            if p.name != self.name:
                self.memory["beliefs"][p.name] = 0

    def update_belief(self, player_name, delta):
        # Adjust trust/suspicion for a player
        if player_name == self.name:
            return
        if player_name not in self.memory["beliefs"]:
            self.memory["beliefs"][player_name] = 0
        self.memory["beliefs"][player_name] += delta

    def get_trusted(self):
        # Return list of players this agent trusts (trust_score > 0)
        return [name for name, score in self.memory["beliefs"].items() if score > 0]

    def get_suspected(self):
        # Return list of players this agent suspects (trust_score < 0)
        return [name for name, score in self.memory["beliefs"].items() if score < 0]

class GameState:
    def __init__(self, player_names):
        self.players = []
        self.leader_index = random.randint(0, 6)
        self.round = 1
        self.successes = 0
        self.failures = 0
        self.failed_votes = 0
        self.mission_history = []
        self.assign_roles(player_names)
        human_name = player_names[0]
        self.human = next(p for p in self.players if p.name == human_name)
        self.distribute_initial_info()
        # Initialize beliefs for all players
        for p in self.players:
            p.initialize_beliefs(self.players)

    def assign_roles(self, names):
        roles = [
            Role.WHISTLEBLOWER, Role.DETECTIVE, Role.COP, Role.PRESIDENT,
            Role.DON, Role.ASSASSIN, Role.INFILTRATOR
        ]
        random.shuffle(roles)
        for name, role in zip(names, roles):
            self.players.append(Player(name, role))

    def distribute_initial_info(self):
        for player in self.players:
            player.receive_initial_info(self.players)
            
    def get_team_size(self):
        sizes = [3, 4, 4, 5, 5]
        return sizes[self.round - 1]

    def rotate_leader(self):
        self.leader_index += 1
        if self.leader_index >= len(self.players):
            self.leader_index = 0

    def propose_team(self):
        team_size = self.get_team_size()
        leader = self.players[self.leader_index]

        team = []
        if leader is self.human:
            styled_print(f"{leader.name} is the leader.", style='system', delay=0.05)
            styled_print(f"Propose a team of {team_size} members.", style='system', delay=0.05)
        while len(team) < team_size:
            choice = input(f"Select player {len(team)+1}: ").strip().capitalize()
            candidate = next((p for p in self.players if p.name == choice), None)
            if candidate and candidate not in team:
                team.append(candidate)
            else:
                    styled_print("Invalid or duplicate selection.", style='warning', delay=0.02)
        else:
            styled_print(f"{leader.name} is the leader.", style='system', delay=random.uniform(2, 4.2))
            team = random.sample(self.players, team_size)
            styled_print(f"{leader.name} proposes: {', '.join([p.name for p in team])}", style='player', delay=0.05)
        return team
            
    def vote_on_team(self, team):
        styled_print("\nVoting phase: Approve or Reject the proposed team.\n", style='system', delay=0.05)
        votes = {}
        voting_order = self.players[:]
        random.shuffle(voting_order)
        for p in voting_order:
            if p is self.human:
                new_line()
                vote = input("Do you approve the team? (Y/N): ").strip().upper()
                new_line()
            else:
                time.sleep(random.uniform(0.8, 2.2))  # Simulate real player thinking
                vote = agent_vote(p, team, p.memory, p.memory['history'][-15:], self.round)
            votes[p.name] = vote
            styled_print(f"{p.name} voted {'Approve' if vote == 'Y' else 'Reject' }.", style='player' if p is not self.human else 'system', delay=0.03)
            # Update memory for this vote
            p.memory['votes'].append({'round': self.round, 'team': [x.name for x in team], 'vote': vote})

        approvals = sum(1 for v in votes.values() if v == 'Y')
        if approvals > len(self.players) // 2:
            new_line()
            styled_print("Team approved.", style='system', delay=0.08)
            new_line()
            return True
        else:
            new_line()
            styled_print("Team rejected.", style='warning', delay=0.08)
            new_line()
            self.failed_votes += 1
            return False
        
    def execute_mission(self, team):
        fails_needed = 2 if self.round == 4 else 1
        styled_print(f"\nMission {self.round} begins. {fails_needed} fail vote(s) required to fail.\n", style='dramatic', delay=0.07)
        fail_votes = 0

        action_order = team[:]
        random.shuffle(action_order)
        for p in action_order:
            if p is self.human:
                if self.human.role in {Role.DON, Role.ASSASSIN, Role.INFILTRATOR}:
                    vote = input("Submit your mission action (P)ass/(F)ail): ").strip().upper()
                else:
                    vote = 'P'
            else:
                time.sleep(random.uniform(0.8, 2.2))  # Simulate real player thinking
                vote = agent_mission_action(p, team, p.memory, p.memory['history'][-15:], self.round)
            if vote == 'F':
                fail_votes += 1
            # Update memory for this mission action
            p.memory['missions'].append({'round': self.round, 'team': [x.name for x in team], 'action': vote})

        mission_failed = fail_votes >= fails_needed
        if mission_failed:
            styled_print("Mission FAILED.", style='error', delay=0.12, typewriter=True)
            self.failures += 1
            if self.failures == 3:
                self.game_over(False)
        else:
            styled_print("Mission SUCCEEDED.", style='system', delay=0.12, typewriter=True)
            self.successes += 1
            if self.successes == 3:
                self.assassin_phase()
        # Update beliefs after mission
        self.update_beliefs_after_round(team, mission_failed)
        self.round += 1
        self.failed_votes = 0
        new_line()

    def update_beliefs_after_round(self, team, mission_failed):
        # Agents update beliefs based on mission outcome and voting patterns
        for agent in self.players:
            # Mission outcome: adjust beliefs for team members
            for p in team:
                if p.name == agent.name:
                    continue
                if mission_failed:
                    agent.update_belief(p.name, -1)  # More suspicious
                else:
                    agent.update_belief(p.name, 1)   # More trusting
            # Voting pattern: trust those who voted the same, suspect those who didn't
            if agent.memory['votes']:
                last_vote = agent.memory['votes'][-1]
                agent_vote = last_vote['vote']
                for other in self.players:
                    if other.name == agent.name or not other.memory['votes']:
                        continue
                    other_vote = other.memory['votes'][-1]['vote']
                    if agent_vote == other_vote:
                        agent.update_belief(other.name, 0.5)
                    else:
                        agent.update_belief(other.name, -0.5)

    def game_over(self, good_won):
        styled_print("\n" + ("The good guys win." if good_won else "Conspirators win."), style='dramatic', delay=0.15, typewriter=True)
        exit()

    def assassin_phase(self):
        assassin = next(p for p in self.players if p.role == Role.ASSASSIN)
        guess = random.choice([p for p in self.players if p != assassin]) #### Placeholder

        if guess.role == Role.WHISTLEBLOWER:
            styled_print("Wrong.", style='system', delay=1)
            styled_print(f"Assassin guessed: {guess.name}", style='player', delay=0.08)
            styled_print("Conspirators win.", style='system', delay=0.1)
            self.game_over(False)
        else:
            styled_print("The Truth Prevails.", style='system', delay=0.1)
            self.game_over(True)

    def get_leader(self):
        return self.players[self.leader_index]

    def suggest_team(self, leader, team_size):
        # Heuristic: pick self + most trusted (least accused, most agreed with, not failed missions)
        # For now, just pick self + random others, but can be improved
        trusted = [p for p in self.players if p != leader]
        random.shuffle(trusted)
        team = [leader] + trusted[:team_size-1]
        return team

    def get_consensus_team(self, discussion_history, team_size):
        # Find the most frequently mentioned team in the last N discussion messages
        mentions = {}
        for msg in discussion_history[-15:]:
            text = msg['text'].lower()
            for p in self.players:
                if p.name.lower() in text:
                    mentions[p.name] = mentions.get(p.name, 0) + 1
        # Pick top N mentioned players
        sorted_mentions = sorted(mentions.items(), key=lambda x: -x[1])
        consensus_team = [name for name, _ in sorted_mentions[:team_size]]
        # If not enough consensus, return empty
        if len(consensus_team) < team_size:
            return []
        # Map names back to player objects
        return [p for p in self.players if p.name in consensus_team]

    def discussion_phase(self, leader, team_size):
        styled_print(f"\n[DISCUSSION PHASE] Leader is {leader.name}. They will start by suggesting a team of {team_size}.", style='dramatic', delay=0.04)
        new_line()
        # Leader suggests a team
        leader_team = self.suggest_team(leader, team_size)
        leader_team_names = ', '.join([p.name for p in leader_team])
        styled_print(f"{leader.name} (Leader) suggests: {leader_team_names}", style='player', delay=0.04)
        discussion_history = [{'round': self.round, 'speaker': leader.name, 'text': f"I suggest {leader_team_names} for the mission."}]
        for pl in self.players:
            pl.memory['history'].append(discussion_history[0])
        # Discussion loop: repeat until human types 'done' or '/skip'
        done = False
        skip_discussion = False
        while not done and not skip_discussion:
            # Always ensure human is included in the round, after all agents
            agent_speakers = [p for p in self.players if p is not leader and p is not self.human]
            random.shuffle(agent_speakers)
            speakers = agent_speakers + [self.human]  # Human always last in the round
            for p in speakers:
                if p is leader:
                    continue  # Leader already spoke
                if p is self.human:
                    styled_print("Your turn to discuss the leader's suggestion (type 'done' to end discussion, or /skip to skip):", style='system', delay=0.01)
                    msg = input('> ').strip()
                    if msg.lower() == '/skip':
                        styled_print("[Discussion skipped]", style='warning', delay=0.01)
                        skip_discussion = True
                        break
                    if msg.lower() == 'done':
                        done = True
                        break
                    if msg:
                        entry = {'round': self.round, 'speaker': p.name, 'text': msg}
                        discussion_history.append(entry)
                        styled_print(f"{p.name}: {msg}", style='system', delay=0.01)
                        for pl in self.players:
                            pl.memory['history'].append(entry)
                else:
                    agent_msg = agent_discussion(p, leader_team, p.memory, discussion_history[-15:], self.round)
                    if not agent_msg or not agent_msg.strip():
                        agent_msg = "(remains silent)"
                    # Remove any role reveals
                    for role in ["cop", "detective", "president", "don", "assassin", "infiltrator", "whistleblower"]:
                        agent_msg = agent_msg.replace(f"({role})", "").replace(f"{role.capitalize()}: ", "")
                    entry = {'round': self.round, 'speaker': p.name, 'text': agent_msg}
                    discussion_history.append(entry)
                    styled_print(f"{p.name}: {agent_msg}", style='player', delay=0.04)
                    for pl in self.players:
                        pl.memory['history'].append(entry)
                    time.sleep(random.uniform(0.7, 1.7))
        new_line()
        styled_print("[Discussion phase ended]", style='dramatic', delay=0.01)
        new_line()
        # Try to get consensus team
        consensus_team = self.get_consensus_team(discussion_history, team_size)
        if consensus_team:
            return consensus_team
        else:
            return leader_team

    def start(self):
        clear_screen()
        time.sleep(2)
        styled_print(f"Your codename is {self.human.name}", style='system', delay=0.08)
        time.sleep(2)
        styled_print(f"You are the {self.human.role.name.capitalize()}", style='dramatic', delay=0.12, typewriter=True)
        time.sleep(4)
        clear_screen()
        curses.wrapper(transition)
        time.sleep(1)
        while self.round <= 5:
            team_approved = False
            while not team_approved:
                leader = self.get_leader()
                team_size = self.get_team_size()
                # Discussion phase: get team suggestion
                team = self.discussion_phase(leader, team_size)
                # Voting phase
                team_approved = self.vote_on_team(team)
                curses.wrapper(transition)
                if not team_approved and self.failed_votes == 5:
                    print("Five consecutive rejections. Bad team wins.")
                    self.game_over(False)
                self.rotate_leader()
            self.execute_mission(team)

# --- AGENT LOGIC FUNCTIONS ---
def agent_discussion(agent, team, memory, discussion_history, round_number):
    # Use LLM for agentic discussion
    return ollama_agent_message(
        agent,
        discussion_history,
        memory['missions'],
        memory['votes'],
        round_number,
        team
    )

def agent_vote(agent, team, memory, discussion_history, round_number):
    return ollama_agent_vote(
        agent,
        team,
        discussion_history,
        memory['missions'],
        memory['votes'],
        round_number
    )

def agent_mission_action(agent, team, memory, discussion_history, round_number):
    return ollama_agent_mission_action(
        agent,
        team,
        discussion_history,
        memory['missions'],
        memory['votes'],
        round_number
    )

if __name__ == '__main__':
    colors = ['Violet', 'Indigo', 'Blue', 'Green', 'Yellow', 'Orange', 'Red']
    random.shuffle(colors)
    game = GameState(colors)

    clear_screen()
    time.sleep(0.5)
    curses.wrapper(intro)
    clear_screen()
    time.sleep(0.5)
    
    def draw_main_menu():
        f = pyfiglet.Figlet(font='slant')
        title = f.renderText('SECRETS')
        print(f"\033[95m{title}\033[0m")
        styled_print('Fate Awaits', style='dramatic', delay=0.04, typewriter=True)
        new_line()
        styled_print('MAIN MENU', style='system', delay=0.04)
        new_line()
        styled_print('[R]ules', style='system', delay=0.01)
        styled_print('[S]tart', style='system', delay=0.01)
        styled_print('[Q]uit', style='system', delay=0.01)
        new_line()
        styled_print('Choose your destiny...', style='dramatic', delay=0.02)

    draw_main_menu()
    choice = input('> ').strip().upper()
    while True:
        if choice == 'R':
            print_rules()
            input('Press Enter to return to the menu...')
            clear_screen()
            draw_main_menu()
            choice = input('> ').strip().upper()
        elif choice == 'S':
            clear_screen()
            game.start()
            break
        elif choice == 'Q':
            styled_print('Goodbye!', style='dramatic', delay=0.05)
            break
        else:
            clear_screen()
            draw_main_menu()
            choice = input('> ').strip().upper()
from enum import Enum, auto
import random, time, math
import curses
from helpers import *
from aesthetics import *

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
        self.beliefs = {}
    
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

class GameState:
    def __init__(self, player_names):
        self.players = []
        self.leader_index = 0
        self.round = 1
        self.successes = 0
        self.failures = 0
        self.failed_votes = 0
        self.mission_history = []
        self.assign_roles(player_names)
        human_name = player_names[0]
        self.human = next(p for p in self.players if p.name == human_name)
        self.distribute_initial_info()

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
        self.leader_index = (self.leader_index + 1) % len(self.players)

    def propose_team(self):
        team_size = self.get_team_size()
        leader = self.players[self.leader_index]
        print(f"{leader.name} is the leader. Propose a team of {team_size} members.")

        team = []
        while len(team) < team_size:
            choice = input(f"Select player {len(team)+1}: ").strip().capitalize()
            candidate = next((p for p in self.players if p.name == choice), None)
            if candidate and candidate not in team:
                team.append(candidate)
            else:
                print("Invalid or duplicate selection.")
        return team
            
    def vote_on_team(self, team):
        print("\nVoting phase: Approve or Reject the proposed team.\n")
        votes = {}
        for p in self.players:
            if p is self.human:
                vote = input("Do you approve the team? (Y/N): ").strip().upper()
            else:
                vote = random.choice(['Y', 'N'])  # Placeholder AI
            votes[p.name] = vote
            print(f"{p.name} voted {'Approve' if vote == 'Y' else 'Reject'}.")

        approvals = sum(1 for v in votes.values() if v == 'Y')
        if approvals > len(self.players) // 2:
            print("Team approved.")
            return True
        else:
            print("Team rejected.")
            self.failed_votes += 1
            return False
        
    def execute_mission(self, team):
        fails_needed = 2 if self.round == 4 else 1
        print(f"\nMission {self.round} begins. {fails_needed} fail vote(s) required to fail.\n")
        fail_votes = 0

        for p in team:
            if p is self.human:
                if self.human.role in {Role.DON, Role.ASSASSIN, Role.INFILTRATOR}:
                    vote = input("Submit your mission action (P)ass/(F)ail): ").strip().upper()
                else:
                    vote = 'P'
            else:
                vote = 'F' if p.role in {Role.DON, Role.ASSASSIN, Role.INFILTRATOR} and random.random() < 0.5 else 'P'
            if vote == 'F':
                fail_votes += 1

        if fail_votes >= fails_needed:
            print("Mission FAILED.")
            self.failures += 1
            if self.failures == 3:
                self.game_over(False)
        else:
            print("Mission SUCCEEDED.")
            self.successes += 1
            if self.successes == 3:
                self.assassin_phase()
        self.round += 1
        self.failed_votes = 0
    
    def game_over(self, good_won):
        if good_won:
            print("\nGood wins the game!")
        else:
            print("\nBad wins the game!")
        exit()

    def assassin_phase(self):
        print("\n3 successful missions! Assassin must now guess the Whistleblower.")
        assassin = next(p for p in self.players if p.role == Role.ASSASSIN)
        guess = random.choice([p for p in self.players if p != assassin])  # Placeholder

        print(f"Assassin guessed: {guess.name}")
        if guess.role == Role.WHISTLEBLOWER:
            print("Wrong.")
            self.game_over(False)
        else:
            print("Good Prevails.")
            self.game_over(True)

    def start(self):
        clear_screen()
        time.sleep(2)
        
        print(f"Your codename is {self.human.name}")
        time.sleep(2)
        
        print(f"You are the {self.human.role.name.capitalize()}")
        time.sleep(4)
        
        clear_screen()
        curses.wrapper(transition)
        time.sleep(1)
        
        for p in self.players:
            if p is self.human:
                role_str = self.human.role.name.capitalize()
                print(f"{p.name} ({role_str}) (You): Hi!")
            else:
                if self.human.role == Role.DETECTIVE:
                    candidates = self.human.known_roles.get('detective_candidates', [])
                    if p in candidates:
                        role_str = "Don OR Whistleblower"
                    else:
                        role_str = "Unknown"
                else:
                    role_str = "Unknown"
                    for key, lst in self.human.known_roles.items():
                        if p in lst:
                            role_str = key.name.capitalize()
                            break
                print(f"{p.name} ({role_str}): Hi!")
            time.sleep(random.uniform(0.1, 1))
            
        while self.round <= 5:
            team_approved = False
            while not team_approved:
                team = self.propose_team()
                team_approved = self.vote_on_team(team)
                if not team_approved and self.failed_votes == 5:
                    print("Five consecutive rejections. Bad team wins.")
                    self.game_over(False)
                self.rotate_leader()
            self.execute_mission(team)

if __name__ == '__main__':
    colors = ['Violet', 'Indigo', 'Blue', 'Green', 'Yellow', 'Orange', 'Red']
    random.shuffle(colors)
    game = GameState(colors)

    clear_screen()
    time.sleep(0.5)
    curses.wrapper(intro)
    clear_screen()
    time.sleep(0.5)
    
    while True:
        print("=== Main Menu ===")
        print("[R]ules")
        print("[S]tart")
        print("[Q]uit")
        choice = input("Select an option: ").strip().upper()
        if choice == 'R':
            print_rules()
            input("Press Enter to return to menu...")
            clear_screen()
        elif choice == 'S':
            clear_screen()
            game.start()
            break
        elif choice == 'Q':
            print("Goodbye!")
            break
        else:
            clear_screen()
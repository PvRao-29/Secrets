from enum import Enum, auto
import random, math
import time
import curses
from helpers import *

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
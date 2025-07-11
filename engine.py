from enum import Enum, auto
import random, time, math
import curses
from helpers import *
from aesthetics import *
import pyfiglet

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
                vote = random.choice(['Y', 'N'])  # Placeholder AI
            votes[p.name] = vote
            styled_print(f"{p.name} voted {'Approve' if vote == 'Y' else 'Reject'}.", style='player' if p is not self.human else 'system', delay=0.03)

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
                vote = 'F' if (p.role in {Role.DON, Role.ASSASSIN, Role.INFILTRATOR} and random.random() < 0.5) else 'P'
            if vote == 'F':
                fail_votes += 1

        if fail_votes >= fails_needed:
            styled_print("Mission FAILED.", style='error', delay=0.12, typewriter=True)
            self.failures += 1
            if self.failures == 3:
                self.game_over(False)
        else:
            styled_print("Mission SUCCEEDED.", style='system', delay=0.12, typewriter=True)
            self.successes += 1
            if self.successes == 3:
                self.assassin_phase()
        self.round += 1
        self.failed_votes = 0
        new_line()
    
    def game_over(self, good_won):
        styled_print("\n" + ("The good guys win." if good_won else "Conspirators win."), style='dramatic', delay=0.15, typewriter=True)
        exit()

    def assassin_phase(self):
        assassin = next(p for p in self.players if p.role == Role.ASSASSIN)
        guess = random.choice([p for p in self.players if p != assassin])  # Placeholder

        if guess.role == Role.WHISTLEBLOWER:
            styled_print("Wrong.", style='system', delay=1)
            styled_print(f"Assassin guessed: {guess.name}", style='player', delay=0.08)
            styled_print("Conspirators win.", style='system', delay=0.1)
            self.game_over(False)
        else:
            styled_print("The Truth Prevails.", style='system', delay=0.1)
            self.game_over(True)

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
        for p in self.players:
            if p is self.human:
                role_str = self.human.role.name.capitalize()
                styled_print(f"{p.name} ({role_str}) (You): Hi!", style='system', delay=0.04)
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
                styled_print(f"{p.name} ({role_str}): Hi!", style='player', delay=0.04)
                time.sleep(random.uniform(0.8, 2.2))  # Simulate real player greeting
        new_line()
            
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
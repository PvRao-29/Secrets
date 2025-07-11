import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

    
def print_rules():
    clear_screen()
    rules = \
    '''SECRET Rules:
    - 7 players:    4 Good (Whistleblower, Detective, Cop, President),
                    3 Bad (Don, Assassin, Infiltrator).
    - 5 missions: Rounds 1-3 & 5 require 1 fail to fail; Round 4 requires 2 fails.
    - Leader rotates, proposes a team of size depending on round.
    - All vote Approve/Reject; 5 consecutive rejections ⇒ Bad wins.
    - Failed mission triggers emergency vote to reveal President.
    - Good wins upon 3 successful missions; Bad wins upon 3 failures
    - If Good completes 3 successful missions then Assassin may guess
        Whistleblower. If done successfully Bad team wins!
    '''
    print(rules)
    

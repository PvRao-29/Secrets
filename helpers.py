import os
import sys
import time
import random
import pyfiglet

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

    
def print_rules():
    clear_screen()
    f = pyfiglet.Figlet(font='slant')
    title = f.renderText('SECRETS')
    print(f"\033[95m{title}\033[0m")
    styled_print('Fate Awaits', style='dramatic', delay=0.04, typewriter=True)
    new_line()
    styled_print('GAME RULES', style='system', delay=0.04)
    new_line()
    styled_print('- 7 players:    4 \033[92mGood\033[0m (\033[96mWhistleblower\033[0m, \033[96mDetective\033[0m, \033[96mCop\033[0m, \033[96mPresident\033[0m),', style='system', delay=0.01)
    styled_print('              3 \033[91mConspirators\033[0m (\033[95mDon\033[0m, \033[95mAssassin\033[0m, \033[95mInfiltrator\033[0m).', style='system', delay=0.01)
    new_line()
    styled_print('- 5 missions: Rounds 1-3 & 5 require 1 fail to fail; Round 4 requires 2 fails.', style='system', delay=0.01)
    styled_print('- Leader rotates, proposes a team of size depending on round.', style='system', delay=0.01)
    styled_print('- All vote Approve/Reject; 5 consecutive rejections ⇒ Conspirators win.', style='system', delay=0.01)
    styled_print('- Failed mission triggers emergency vote to reveal President.', style='system', delay=0.01)
    styled_print('- Good wins upon 3 successful missions; Conspirators win upon 3 failures.', style='system', delay=0.01)
    styled_print('- If Good completes 3 successful missions then Assassin may guess', style='system', delay=0.01)
    styled_print('    Whistleblower. If done successfully Conspirators win!', style='system', delay=0.01)
    new_line()


def styled_print(msg, style='system', delay=0.01, typewriter=False):
    COLORS = {
        'system': '\033[92m',   # Green
        'player': '\033[94m',  # Blue
        'warning': '\033[93m',  # Yellow
        'error': '\033[91m',    # Red
        'dramatic': '\033[95m', # Magenta
        'reset': '\033[0m'
    }
    prefix = {
        'system': '[SYSTEM] ',
        'player': '[REMOTE] ',
        'warning': '[!]',
        'error': '[X]',
        'dramatic': '[***] '
    }.get(style, '')
    color = COLORS.get(style, COLORS['system'])
    reset = COLORS['reset']
    full_msg = f"{color}{prefix}{msg}{reset}"
    if typewriter:
        for c in full_msg:
            sys.stdout.write(c)
            sys.stdout.flush()
            time.sleep(delay)
        print()
    else:
        print(full_msg)
        if delay > 0:
            time.sleep(delay + random.uniform(0, 0.1))
            
def new_line():
    print()

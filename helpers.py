import os
import time
import curses
import math
import pyfiglet

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
    
def transition(stdscr):
    curses.curs_set(0)
    stdscr.clear()
    if not curses.has_colors():
        raise RuntimeError("Terminal has no color support")
    curses.start_color()
    curses.use_default_colors()
    if curses.can_change_color():
        neon_r = int(57 / 255 * 1000)
        neon_g = int(255 / 255 * 1000)
        neon_b = int(20 / 255 * 1000)
        curses.init_color(10, neon_r, neon_g, neon_b)
        curses.init_pair(3, 10, curses.COLOR_BLACK)
    else:
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)

    h, w = stdscr.getmaxyx()
    msg = "-- Press any key to continue --"
    x = max((w - len(msg)) // 2, 0)
    y = h // 2
    stdscr.attron(curses.color_pair(3) | curses.A_BOLD)
    stdscr.addstr(y, x, msg)
    stdscr.attroff(curses.color_pair(3) | curses.A_BOLD)
    stdscr.refresh()
    stdscr.getch()
    stdscr.clear()
    stdscr.refresh()

        
def intro(stdscr):
    curses.curs_set(0)
    stdscr.clear()
    
    if not curses.has_colors():
        raise RuntimeError("Terminal has no color support")
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_MAGENTA, -1)
    curses.init_pair(2, curses.COLOR_GREEN, -1)


    title_fig = pyfiglet.Figlet(font='slant')
    title_text = title_fig.renderText("SECRETS: Fate Awaits")

    subtitle_fig = pyfiglet.Figlet(font='small')
    subtitle_text = subtitle_fig.renderText("Trust No One")

    h, w = stdscr.getmaxyx()
    title_lines = title_text.splitlines()
    start_y = max((h - len(title_lines)) // 2 - 2, 0)
    for i, line in enumerate(title_lines):
        x = max((w - len(line)) // 2, 0)
        stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        stdscr.addstr(start_y + i, x, line[:w])
        stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
    stdscr.refresh()
    time.sleep(1)

    sub_lines = subtitle_text.splitlines()
    sub_y = start_y + len(title_lines)
    for i, line in enumerate(sub_lines):
        x = max((w - len(line)) // 2, 0)
        stdscr.attron(curses.color_pair(2) | curses.A_DIM)
        stdscr.addstr(sub_y + i, x, line[:w])
        stdscr.attroff(curses.color_pair(2) | curses.A_DIM)
        stdscr.refresh()
        time.sleep(0.1)

    time.sleep(0.8)
    
    for _ in range(3):
        for i, line in enumerate(sub_lines):
            x = max((w - len(line)) // 2, 0)
            stdscr.addstr(sub_y + i, x, ' ' * len(line))
        stdscr.refresh()
        time.sleep(0.2)

        for i, line in enumerate(sub_lines):
            x = max((w - len(line)) // 2, 0)
            stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
            stdscr.addstr(sub_y + i, x, line[:w])
            stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)
        stdscr.refresh()
        time.sleep(0.2)

    stdscr.clear()
    stdscr.refresh()
    
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
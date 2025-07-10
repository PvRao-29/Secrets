import os
import time
import curses
import math
import pyfiglet

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
    
def transition(stdscr):
        curses.curs_set(0)
        if not curses.has_colors():
            raise RuntimeError("Terminal has no color support")
        curses.start_color()
        curses.use_default_colors()

        # 2) define neon‐green at idx 10 (0–1000 scale)
        if curses.can_change_color():
            neon_r = int(57  / 255 * 1000)
            neon_g = int(255 / 255 * 1000)
            neon_b = int(20  / 255 * 1000)
            curses.init_color(10, neon_r, neon_g, neon_b)
            curses.init_pair(1, 10, -1)
        else:
            # fallback to bright green if you can’t redefine
            curses.init_pair(1, curses.COLOR_GREEN, -1)
            
        curses.curs_set(0)
        stdscr.clear()
        stdscr.refresh()
        h, w = stdscr.getmaxyx()
        cy, cx = h // 2, w // 2
        max_radius = int(math.hypot(cy, cx))

        drawn = set()
        for r in range(max_radius + 1):
            for angle in range(0, 360, 5):
                rad = math.radians(angle)
                y = cy + int(r * math.sin(rad))
                x = cx + int(r * math.cos(rad))
                if 0 <= y < h and 0 <= x < w and (y, x) not in drawn:
                    stdscr.addch(y, x, '#')
                    drawn.add((y, x))
            stdscr.refresh()
            time.sleep(0.01)

        time.sleep(0.2)

        for r in reversed(range(max_radius + 1)):
            for angle in range(0, 360, 5):
                rad = math.radians(angle)
                y = cy + int(r * math.sin(rad))
                x = cx + int(r * math.cos(rad))
                if (y, x) in drawn:
                    stdscr.addch(y, x, ' ')
                    drawn.remove((y, x))
            stdscr.refresh()
            time.sleep(0.005)

        stdscr.clear()
        stdscr.refresh()
        
def intro(stdscr):
    """
    Displays a large ASCII-art title and subtitle for Avalon.
    Requires `pyfiglet` for rendering big fonts.
    """
    curses.curs_set(0)
    stdscr.clear()
    
    if not curses.has_colors():
        raise RuntimeError("Terminal has no color support")
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_MAGENTA, -1)
    curses.init_pair(2, curses.COLOR_YELLOW, -1)


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
    
    for _ in range(2):
        stdscr.attron(curses.A_BLINK)
        for i, line in enumerate(sub_lines):
            x = max((w - len(line)) // 2, 0)
            stdscr.addstr(sub_y + i, x, line[:w])
        stdscr.attroff(curses.A_BLINK)
        stdscr.refresh()
        time.sleep(0.2)
        
        for i, line in enumerate(sub_lines):
            x = max((w - len(line)) // 2, 0)
            stdscr.addstr(sub_y + i, x, line[:w])
        stdscr.refresh()
        time.sleep(0.2)

    stdscr.clear()
    stdscr.refresh()
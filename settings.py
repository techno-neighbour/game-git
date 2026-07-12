import time
import random as rd
import json
import sys
import os

try:
    import msvcrt
except ImportError:
    msvcrt = None

# Enable ANSI escape codes on Windows terminal
if sys.platform == 'win32':
    import ctypes
    try:
        kernel32 = ctypes.windll.kernel32
        # 7 is ENABLE_PROCESSED_OUTPUT (1) | ENABLE_WRAP_AT_EOL_OUTPUT (2) | ENABLE_VIRTUAL_TERMINAL_PROCESSING (4)
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except Exception:
        pass

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass


class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    @staticmethod
    def red(text):
        return f"{Colors.RED}{text}{Colors.RESET}"

    @staticmethod
    def green(text):
        return f"{Colors.GREEN}{text}{Colors.RESET}"

    @staticmethod
    def yellow(text):
        return f"{Colors.YELLOW}{text}{Colors.RESET}"

    @staticmethod
    def cyan(text):
        return f"{Colors.CYAN}{text}{Colors.RESET}"

    @staticmethod
    def magenta(text):
        return f"{Colors.MAGENTA}{text}{Colors.RESET}"
        
    @staticmethod
    def bold(text):
        return f"{Colors.BOLD}{text}{Colors.RESET}"

def timed_input(prompt, timeout_check_func):
    if sys.platform != 'win32' or msvcrt is None:
        # Fallback to standard input on non-Windows platforms
        return input(prompt)
        
    sys.stdout.write(prompt)
    sys.stdout.flush()
    input_str = ''
    while True:
        if timeout_check_func():
            return None
        if msvcrt.kbhit():
            ch = msvcrt.getwch()
            if ch == '\r' or ch == '\n':
                sys.stdout.write('\n')
                sys.stdout.flush()
                return input_str
            elif ch == '\b':
                if len(input_str) > 0:
                    input_str = input_str[:-1]
                    sys.stdout.write('\b \b')
                    sys.stdout.flush()
            elif ch == '\x03': # Ctrl+C
                raise KeyboardInterrupt
            elif ch in ('\x00', '\xe0'):
                if msvcrt.kbhit():
                    msvcrt.getwch()
                continue
            else:
                # Handle UTF-16 surrogate pairs (e.g. emojis) on Windows console
                if 0xd800 <= ord(ch) <= 0xdbff:
                    try:
                        low_ch = msvcrt.getwch()
                        if 0xdc00 <= ord(low_ch) <= 0xdfff:
                            ch = chr(0x10000 + (ord(ch) - 0xd800) * 0x400 + (ord(low_ch) - 0xdc00))
                    except Exception:
                        pass
                
                input_str += ch
                try:
                    sys.stdout.write(ch)
                    sys.stdout.flush()
                except UnicodeEncodeError:
                    pass
        time.sleep(0.05)


class g_func:
    ghost_damage = {
        'strong': 40,
        'normal': 30,
        'weak': 10
    }

    def __init__(self):
        self.rooms = {
            'Foyer': {'north': 'Sunroom', 'east': 'Door', 'west': 'Hall', 'south': 'Kitchen'},
            'Garden': {'north': 'Backyard', 'west': 'Washroom'},
            'Kitchen': {'west': 'Hallway', 'east': 'Pantry', 'south': 'Dining', 'north': 'Foyer'},
            'Dining': {'north': 'Kitchen', 'east': 'Fireplace', 'south': 'Basement', 'west': 'Guestroom'},
            'Bedroom': {'east': 'Hallway', 'south': 'Tavern', 'north': 'Library'},
            'Fireplace': {'north': 'Pantry', 'west': 'Dining', 'east': 'Backyard', 'south': 'Washroom'},
            'Washroom': {'east': 'Garden', 'west': 'Basement', 'north': 'Fireplace'},
            'Tavern': {'east': 'Guestroom', 'north': 'Bedroom'},
            'Guestroom': {'north': 'Hallway', 'west': 'Tavern', 'east':'Dining'},
            'Sunroom': {'south': 'Foyer', 'west': 'Shrine'},
            'Library': {'north': 'Observatory', 'east': 'Hall', 'south': 'Bedroom'},
            'Observatory': {'south': 'Library', 'east': 'Shrine'},
            'Pantry': {'west': 'Kitchen', 'south': 'Fireplace'},
            'Shrine': {'south': 'Hall', 'west': 'Observatory', 'east': 'Sunroom'},
            'Basement': {'north': 'Dining', 'east': 'Washroom'},
            'Backyard': {'south': 'Garden', 'west': 'Fireplace'}
        }

        self.note = {
            '1234': 'The way you count, is the way you go out.',
            '2020': 'The year that locked the world down, may unlock your door.',
            '1357': 'The oddity of the line is the key to unlocking the unknown.',
            '3141': 'Follow the circle to your path of freedom, but with a constant effort.',
            '1711': "A journey marked one the first and last, but with a week's effort in.",
            '8080': 'Infinity repeats, with and without a belt, but within it, lies your finite path.',
            '0001': 'From nothing, the first spark breaks the infinite silence.',
            '1123': 'The consequences of the future is the sum of your past.',
            '3690': 'Tesla’s trinity dances in circles, follow their hum to nothingness.',
            '3333': 'Infinity divided into pieces, make your choice with thesis.',
            '1010': 'A decade in the dual-bit system, is your algorithm.',
            '2357': 'Small, yet indivisible forces stand in your way to freedom.',
            '9101': 'Everyone can have nine dreams and ten paths but only one destination.',
            '2468': 'Even in multiples, the path is yours to take.',
            '5678': 'Five moves forward, eight steps closer.',
            '4812': "A Cube's character, can decide your fate.",
            '4242': 'The answer lies collinear with the answer to the universe and everything.'
        }

        self.ROOM_SIZE = 21
        self.inventory = {}
        self.current_room = 'Hall'
        self.health = 100
        self.required_keys = 3
        self.max_password_attempts = 5
        self.time_up = False
        self.player_r = self.ROOM_SIZE // 2
        self.player_c = self.ROOM_SIZE // 2
        self.player_dir = '▲'
        self.log_messages = []

    def add_message(self, msg):
        if not hasattr(self, 'log_messages'):
            self.log_messages = []
        self.log_messages.append(msg)
        if len(self.log_messages) > 50:
            self.log_messages.pop(0)

    def status(self):
        time.sleep(1)
        print(f"Current location: {Colors.cyan(self.current_room)}")
        time.sleep(1)
        if self.health <= 20:
            print(f"Current health: {Colors.red(str(self.health))}")
            print(Colors.red("WARNING: Your health is low!"))
        else:
            print(f"Current health: {Colors.green(str(self.health))}")

    def death_by_patron(self):
        print(Colors.red("\nOh no! The patron has found you."), flush=True, end='')
        time.sleep(4)
        print(Colors.red(" He fires three bullet's from his pistol,"), flush=True, end='')
        time.sleep(2)
        print(Colors.red(' you manage to dodge two ,'), flush=True, end='')
        time.sleep(2)
        print(Colors.red(" but the last one passes through your head."), flush=True, end='')
        time.sleep(2)
        print(Colors.red("\nYou slowly start to black out,"), flush=True, end='')
        time.sleep(2)
        print(Colors.red(" as the patron stares at your lifeless body"), flush=True, end='')
        time.sleep(2)
        print(Colors.red(", with a wild grin"), flush=True, end='')
        time.sleep(2)
        print('.\n', flush=True, end='')
        time.sleep(1)
        
    def sleep_or_skip_helper(self, duration, skip_flag_ref):
        start = time.time()
        while time.time() - start < duration:
            if sys.platform == 'win32' and msvcrt is not None:
                if msvcrt.kbhit():
                    ch = msvcrt.getwch()
                    if ch in ('\r', '\n'):
                        skip_flag_ref[0] = True
                        return
            else:
                import select
                try:
                    rlist, _, _ = select.select([sys.stdin], [], [], 0.0)
                    if rlist:
                        ch = sys.stdin.read(1)
                        if ch in ('\r', '\n'):
                            skip_flag_ref[0] = True
                            return
                except Exception:
                    pass
            time.sleep(0.01)

    def flush_input(self):
        if sys.platform == 'win32' and msvcrt is not None:
            while msvcrt.kbhit():
                msvcrt.getwch()
        else:
            try:
                import select
                while select.select([sys.stdin], [], [], 0.0)[0]:
                    sys.stdin.read(1)
            except Exception:
                pass

    def print_centered(self, text, skip_flag_ref=None, delay=0.0):
        try:
            columns, _ = os.get_terminal_size()
        except Exception:
            columns = 80
        width = max(79, columns - 1)

        # Clean ANSI escape sequences to calculate exact padding
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        clean = ansi_escape.sub('', text)

        padding = max(0, (width - len(clean)) // 2)
        print(" " * padding, end="")
        if delay > 0.0:
            for char in text:
                print(char, end="", flush=True)
                if skip_flag_ref is not None and not skip_flag_ref[0]:
                    self.sleep_or_skip_helper(delay, skip_flag_ref)
        else:
            print(text, end="")
        print()

    def stream_file_centered(self, filename, skip_flag_ref, delay=0.05):
        try:
            columns, _ = os.get_terminal_size()
        except Exception:
            columns = 80
        width = max(79, columns - 1)

        lines = []
        with open(filename, "r") as file:
            for line in file:
                stripped = line.strip()
                if stripped:
                    lines.append(" ".join(stripped.split()))
                else:
                    lines.append("")

        # Find maximum length among non-empty lines
        max_len = 0
        for line in lines:
            if len(line) > max_len:
                max_len = len(line)

        padding = max(0, (width - max_len) // 2)
        pad = " " * padding

        for line in lines:
            if line:
                print(pad, end="")
                for i, char in enumerate(line):
                    print(char, end="", flush=True)
                    if not skip_flag_ref[0]:
                        self.sleep_or_skip_helper(delay, skip_flag_ref)
                    if char in ('.', ',', '!') and (i == len(line) - 1 or line[i+1] == ' '):
                        if not skip_flag_ref[0]:
                            self.sleep_or_skip_helper(0.5, skip_flag_ref)
                print()
            else:
                print()

    def dash_skipping(self, a, skip_flag_ref):
        try:
            columns, _ = os.get_terminal_size()
        except Exception:
            columns = 80
        width = max(79, columns - 1)

        for i in range(width):
            print(a, end="", flush=True)
            if not skip_flag_ref[0]:
                self.sleep_or_skip_helper(0.01 if a in ('-', '=') else 0.05, skip_flag_ref)
        print("")

    def game_intro(self):
        # Disable echo and canonical mode on Unix for the entire intro duration
        old_settings = None
        fd = None
        if sys.platform != 'win32':
            try:
                import termios
                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                new_settings = termios.tcgetattr(fd)
                new_settings[3] = new_settings[3] & ~termios.ECHO & ~termios.ICANON
                termios.tcsetattr(fd, termios.TCSADRAIN, new_settings)
            except Exception:
                pass

        try:
            self.flush_input()
            
            # --- SECTION 1: INTRO ---
            skip_intro = [False]
            if not skip_intro[0]:
                self.sleep_or_skip_helper(1.0, skip_intro)
                
            self.print_centered(Colors.cyan(Colors.bold('TEXT-BASED ADVENTURE GAME')))
            self.dash_skipping("=", skip_intro)

            self.stream_file_centered("intro.txt", skip_intro)
                    
            # --- SECTION 2: OBJECTIVE ---
            self.flush_input()
            skip_objective = [False]
            
            if not skip_objective[0]:
                self.sleep_or_skip_helper(0.5, skip_objective)
            self.dash_skipping("-", skip_objective)
            if not skip_objective[0]:
                self.sleep_or_skip_helper(0.5, skip_objective)
                
            self.print_centered(Colors.cyan('GAME OBJECTIVE:'))
            if not skip_objective[0]:
                self.sleep_or_skip_helper(0.7, skip_objective)

            self.stream_file_centered("objective.txt", skip_objective)

            # --- SECTION 3: COMMANDS ---
            self.flush_input()
            skip_commands = [False]
            
            if not skip_commands[0]:
                self.sleep_or_skip_helper(0.5, skip_commands)
            self.dash_skipping("-", skip_commands)
            if not skip_commands[0]:
                self.sleep_or_skip_helper(2.0, skip_commands)

            self.print_centered(Colors.cyan('COMMANDS:'))
            
            commands_list = [
                f"'{Colors.yellow('move [direction]')}' - move around (north, south, east, west)",
                f"'{Colors.yellow('collect [item]')}' - collect the item in the room",
                f"'{Colors.yellow('use potion')}' - heal yourself using a potion",
                f"'{Colors.yellow('read note')}' - reads the note you've collected",
                f"'{Colors.yellow('inventory')}' - see what you've collected",
                f"'{Colors.yellow('map')}' - see the blueprint of the house",
                f"'{Colors.yellow('save')}' - save your game",
                f"'{Colors.yellow('quit')}' - leave the game"
            ]
            
            try:
                columns, _ = os.get_terminal_size()
            except Exception:
                columns = 80
            width = max(79, columns - 1)

            # Calculate max length of command lines (stripping ANSI codes)
            import re
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

            max_len = 0
            for cmd in commands_list:
                clean = ansi_escape.sub('', cmd)
                if len(clean) > max_len:
                    max_len = len(clean)

            cmd_padding = max(0, (width - max_len) // 2)
            pad = " " * cmd_padding

            for cmd in commands_list:
                print(pad + cmd)
                if not skip_commands[0]:
                    self.sleep_or_skip_helper(0.5, skip_commands)
                    
            self.dash_skipping("-", skip_commands)
            print("")
            self.flush_input()

        finally:
            if old_settings is not None and fd is not None:
                try:
                    import termios
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                except Exception:
                    pass

    def check_locked_room(self, room, render_callback=None, attempts=0):
        if 'locked' in self.rooms[room] and self.rooms[room]['locked']:
            self.add_message(f"The {Colors.cyan(room)} is locked.")
            if render_callback: render_callback()
            while attempts < self.max_password_attempts:
                prompt_str = " " * 52 + f"Enter Pin ({self.max_password_attempts - attempts} left): "
                password = timed_input(prompt_str, lambda: self.time_up)
                if password is None or self.time_up:
                    return True
                if password == self.rooms[room].get('password', ''):
                    time.sleep(1)
                    self.add_message(f"You unlocked the {Colors.cyan(room)}!")
                    if render_callback: render_callback()
                    self.rooms[room]['locked'] = False
                    return False
                else:
                    time.sleep(1)
                    attempts += 1
                    self.add_message(f"{Colors.red('Wrong password.')}")
                    if render_callback: render_callback()
            valid_ejection_directions = []
            for direction in ('north', 'south', 'east', 'west'):
                if direction in self.rooms[self.current_room]:
                    target_room = self.rooms[self.current_room][direction]
                    if target_room != room:
                        valid_ejection_directions.append(direction)
            if valid_ejection_directions:
                s = rd.choice(valid_ejection_directions)
            else:
                s = rd.choice([d for d in ('north', 'south', 'east', 'west') if d in self.rooms[self.current_room]])
            self.add_message(f"Too many wrong attempts. Sent {Colors.cyan(s)}.")
            if render_callback: render_callback()
            self.current_room = self.rooms[self.current_room][s]
            self.player_r = self.ROOM_SIZE // 2
            self.player_c = self.ROOM_SIZE // 2
            return True
        return False

    def draw_room(self, player_r, player_c):
        grid = []
        room_data = self.rooms[self.current_room]

        has_north = 'north' in room_data
        has_south = 'south' in room_data
        has_west = 'west' in room_data
        has_east = 'east' in room_data

        center = self.ROOM_SIZE // 2
        max_idx = self.ROOM_SIZE - 1

        for r in range(self.ROOM_SIZE):
            row_chars = []
            for c in range(self.ROOM_SIZE):
                if r == 0:
                    if c == center and has_north:
                        row_chars.append(' ')
                    else:
                        row_chars.append('█')
                elif r == max_idx:
                    if c == center and has_south:
                        row_chars.append(' ')
                    else:
                        row_chars.append('█')
                elif c == 0:
                    if r == center and has_west:
                        row_chars.append(' ')
                    else:
                        row_chars.append('█')
                elif c == max_idx:
                    if r == center and has_east:
                        row_chars.append(' ')
                    else:
                        row_chars.append('█')
                else:
                    row_chars.append('.')
            grid.append(row_chars)

        if 'item' in room_data:
            if 'item_pos' not in room_data:
                room_data['item_pos'] = (rd.randint(1, self.ROOM_SIZE - 2), rd.randint(1, self.ROOM_SIZE - 2))
            ir, ic = room_data['item_pos']
            if room_data['item'] == 'key':
                grid[ir][ic] = '🗝'
            elif room_data['item'] == 'potion':
                grid[ir][ic] = '☤'
            elif room_data['item'] == 'note':
                grid[ir][ic] = '🗎'

        if room_data.get('ghost') and not room_data.get('attacked'):
            if 'ghost_pos' not in room_data:
                room_data['ghost_pos'] = (rd.randint(1, self.ROOM_SIZE - 2), rd.randint(1, self.ROOM_SIZE - 2))
            gr, gc = room_data['ghost_pos']
            grid[gr][gc] = '☠'

        grid[player_r][player_c] = self.player_dir

        # Render each cell as 2 characters wide for emoji alignment
        colored_grid = []
        for r in range(self.ROOM_SIZE):
            line_parts = []
            for c in range(self.ROOM_SIZE):
                char = grid[r][c]
                if char == '█':
                    line_parts.append(Colors.cyan("██"))
                elif char == '.':
                    line_parts.append(Colors.WHITE + ". " + Colors.RESET)
                elif char == ' ':
                    line_parts.append("  ")
                elif char in ('▲', '▼', '◄', '►'):
                    line_parts.append("🧑")
                elif char == '☠':
                    line_parts.append("👻")
                elif char == '🗝':
                    line_parts.append("🔑")
                elif char == '☤':
                    line_parts.append("🧪")
                elif char == '🗎':
                    line_parts.append("📜")
                else:
                    # Fallback for any other characters
                    line_parts.append(char + " ")
            colored_grid.append("".join(line_parts))

        return "\n".join(colored_grid)
    
    def blueprint(self): 
        layout = """                +-------------+     +--------+     +---------+
                | Observatory |-----| Shrine |-----| Sunroom |
                +-------------+     +--------+     +---------+
                       |                 |              |
                +-------------+     +--------+     +---------+      +------+
                |   Library   |-----|  Hall  |-----|  Foyer  |------| Door |
                +-------------+     +--------+     +---------+      +------+
                        |                |              |
                +-------------+     +---------+     +---------+    +--------+
                |   Bedroom   |-----| Hallway |-----| Kitchen |----| Pantry |
                +-------------+     +---------+     +---------+    +--------+
                       |                 |               |              |
                  +--------+       +-----------+    +--------+    +-----------+     +----------+
                  | Tavern |-------| Guestroom |----| Dining |----| Fireplace |-----| Backyard |
                  +--------+       +-----------+    +--------+    +-----------+     +----------+
                                                         |               |               |
                                                   +----------+     +----------+     +--------+
                                                   | Basement |-----| Washroom |-----| Garden |
                                                   +----------+     +----------+     +--------+ """
        print(Colors.cyan(layout))

    def ghost(self, render_callback=None):
        time.sleep(1)
        self.add_message(Colors.red('Oh no! A Ghost!'))
        if render_callback: render_callback()
        time.sleep(1)
        self.add_message(Colors.red("The ghost attacks!"))
        if render_callback: render_callback()
        time.sleep(1)
        s = rd.choice(list(self.ghost_damage.keys()))
        s1 = f' {s} ' if s != 'normal' else ' '
        self.health -= self.ghost_damage[s]
        if self.health <= 0:
            self.add_message(Colors.red("The ghost has defeated you! You died..."))
            if render_callback: render_callback()
            return True
        else:
            self.add_message(Colors.red(f"You were attacked by a{s1}ghost."))
            if render_callback: render_callback()
            time.sleep(1)
            self.add_message(f"Your health is now {Colors.green(str(self.health)) if self.health > 20 else Colors.red(str(self.health))}.")
            if render_callback: render_callback()
            time.sleep(1)
        return False

    def give_health(self):
        return self.health

    def use_potion(self):
        time.sleep(1)
        d = {'Super': 40, 'Normal': 30, 'Weak': 10}
        s = rd.choice(list(d.keys()))
        potions_count = self.inventory.get('potion', 0)
        if potions_count > 0 and self.health < 100:
            healing_amount = min(d[s], 100 - self.health)
            self.health += healing_amount
            self.inventory['potion'] -= 1
            s1 = f' {s} ' if s != 'Normal' else ' '
            self.add_message(f"You used a{s1}potion. HP is now {Colors.green(str(self.health))}.")
        elif self.health == 100:
            self.add_message("Your health is already full.")
        elif potions_count == 0:
            self.add_message(Colors.yellow("No potions in your inventory!"))

    def save(self, note_key, note_text, SAVE_FILE):
        with open(SAVE_FILE, 'w') as f:
            json.dump({
                'rooms': self.rooms,
                'inventory': self.inventory,
                'current_room': self.current_room,
                'health': self.health,
                'note_key': note_key,
                'note_text': note_text,
                'player_r': self.player_r,
                'player_c': self.player_c,
                'player_dir': self.player_dir
            }, f)
        self.add_message("Game saved.")

    @classmethod
    def load(cls, SAVE_FILE):
        with open(SAVE_FILE, 'r') as f:
            data = json.load(f)
        inst = cls()
        inst.rooms = data['rooms']
        inst.inventory = data['inventory']
        inst.current_room = data['current_room']
        inst.health = data['health']
        inst.player_r = data.get('player_r', inst.ROOM_SIZE // 2)
        inst.player_c = data.get('player_c', inst.ROOM_SIZE // 2)
        inst.player_dir = data.get('player_dir', '▲')
        return inst, data['note_key'], data['note_text']
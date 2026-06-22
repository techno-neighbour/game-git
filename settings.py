import time
import random as rd
import json
import sys

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
            else:
                if ch in ('\x00', '\xe0'):
                    if msvcrt.kbhit():
                        msvcrt.getwch()
                    continue
                input_str += ch
                sys.stdout.write(ch)
                sys.stdout.flush()
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

        self.inventory = {}
        self.current_room = 'Hall'
        self.health = 100
        self.required_keys = 3
        self.max_password_attempts = 5
        self.time_up = False

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
        
    def dash(self,a):
        print("    ",end="")
        for i in range(69):
            print(a,end="",flush=True)
            time.sleep(0.05)
        print("")

    def game_intro(self):
        time.sleep(1)
        print(f"\n{Colors.cyan(Colors.bold('                                TEXT-BASED ADVENTURE GAME'))}")
        self.dash("=")

        with open("intro.txt", "r") as file: #opens the intro file
            for line in file:
                words = line.split()
                print("    ", end='')  #indentation for the text
                for word in words:
                    for char in word:
                        print(char, end='', flush=True) #prints each character with a delay
                        time.sleep(0.05)  
                    print(' ', end='', flush=True)  #adds a space between words
                    time.sleep(0.05)  
                    if word.endswith('.') or word.endswith(','):
                        time.sleep(0.5)
                print()
        time.sleep(0.5)
        self.dash("-")
        time.sleep(0.5)
        print(f"    {Colors.cyan('GAME OBJECTIVE:')}")
        time.sleep(0.7)

        with open("objective.txt", "r") as file: # opens the objective file
            for line in file:
                words = line.split()
                print("    ", end='')  #indentation for the text
                for word in words:
                    for char in word:
                        print(char, end='', flush=True) #prints each character with a delay
                        time.sleep(0.05)  
                    print(' ', end='', flush=True)  #adds a space between words  
                    time.sleep(0.05)
                    if (word.endswith(',') or word.endswith('!')):
                        time.sleep(0.45)
                print()

        self.dash("-")
        time.sleep(2)

        print(f"    {Colors.cyan('COMMANDS:')}")
        time.sleep(0.5)
        print(f"   '{Colors.yellow('move [direction]')}' - move around (north, south, east, west)")
        time.sleep(0.5)
        print(f"   '{Colors.yellow('collect [item]')}' - collect the item in the room")
        time.sleep(0.5)
        print(f"   '{Colors.yellow('use potion')}' - heal yourself using a potion")
        time.sleep(0.5)
        print(f"   '{Colors.yellow('read note')}' - reads the note you've collected")
        time.sleep(0.5)
        print(f"   '{Colors.yellow('inventory')}' - see what you've collected")
        time.sleep(0.5)
        print(f"   '{Colors.yellow('map')}' - see the blueprint of the house")
        time.sleep(0.5)
        print(f"   '{Colors.yellow('save')}' - save your game")
        time.sleep(0.5)
        print(f"   '{Colors.yellow('quit')}' - leave the game")
        time.sleep(0.5)
        self.dash("-")
        print("")

    def check_locked_room(self, room, attempts=0):
        if 'locked' in self.rooms[room] and self.rooms[room]['locked']:
            print(f"The {Colors.cyan(room)} is locked.")
            while attempts < self.max_password_attempts:
                password = timed_input("Enter the Pin (----): ", lambda: self.time_up)
                if password is None or self.time_up:
                    return True
                if password == self.rooms[room].get('password', ''):
                    time.sleep(1)
                    print(f"\nYou've unlocked the {Colors.cyan(room)}!")
                    self.rooms[room]['locked'] = False
                    return False
                else:
                    time.sleep(1)
                    attempts += 1
                    print(f"\n{Colors.red('Wrong password.')} {Colors.yellow(f'{self.max_password_attempts - attempts}')} attempts left.")
            s = rd.choice(['north', 'south', 'east', 'west'])
            while True:
                if s not in self.rooms[self.current_room]:
                    s = rd.choice(['north', 'south', 'east', 'west'])
                else:
                    break
            print(f"Too many wrong attempts. You're being sent {Colors.cyan(s)}.")
            self.current_room = self.rooms[self.current_room][s]
            return True
        return False
    
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

    def ghost(self):
        time.sleep(1)
        print(Colors.red('\nOh no!'),end='')
        time.sleep(1)
        print(Colors.red(' A Ghost!'))
        time.sleep(1)
        print(Colors.red("The ghost attacks!"))
        time.sleep(1)
        s = rd.choice(list(self.ghost_damage.keys()))
        s1 = f' {s} ' if s != 'normal' else ' '
        self.health -= self.ghost_damage[s]
        if self.health <= 0:
            print(Colors.red("The ghost has defeated you! You died..."))
            return True
        else:
            print(Colors.red(f"You were attacked by a{s1}ghost."))
            time.sleep(1)
            print(f"Your health is now {Colors.green(str(self.health)) if self.health > 20 else Colors.red(str(self.health))}.")
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
            print(f"You used a{s1}potion. Your health is now {Colors.green(str(self.health))}.")
        elif self.health == 100:
            print("Your health is already full. You can't use a potion now.")
        elif potions_count == 0:
            print(Colors.yellow("No potions in your inventory!"))

    def save(self, note_key, note_text, SAVE_FILE):
        with open(SAVE_FILE, 'w') as f:
            json.dump({
                'rooms': self.rooms,
                'inventory': self.inventory,
                'current_room': self.current_room,
                'health': self.health,
                'note_key': note_key,
                'note_text': note_text
            }, f)
        print("Game saved.")

    @classmethod
    def load(cls, SAVE_FILE):
        with open(SAVE_FILE, 'r') as f:
            data = json.load(f)
        inst = cls()
        inst.rooms = data['rooms']
        inst.inventory = data['inventory']
        inst.current_room = data['current_room']
        inst.health = data['health']
        return inst, data['note_key'], data['note_text']
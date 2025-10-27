import time
import random as rd
import json

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
        print(f"Current location: {self.current_room}")
        time.sleep(1)
        print(f"Current health: {self.health}")
        if self.health <= 20:
            print("WARNING: Your health is low!")

    def death_by_patron(self):
        print("\nOh no! The patron has found you.", flush=True, end='')
        time.sleep(4)
        print(" He fires three bullet's from his pistol,", flush=True, end='')
        time.sleep(2)
        print(' you manage to dodge two ,', flush=True, end='')
        time.sleep(2)
        print(" but the last one passes through your head.", flush=True, end='')
        time.sleep(2)
        print("\nYou slowly start to black out,", flush=True, end='')
        time.sleep(2)
        print(" as the patron stares at your lifeless body", flush=True, end='')
        time.sleep(2)
        print(", with a wild grin", flush=True, end='')
        time.sleep(2)
        print('.', flush=True, end='')
        time.sleep(1)
        
    def dash(self,a):
        print("    ",end="")
        for i in range(69):
            print(a,end="",flush=True)
            time.sleep(0.05)
        print("")

    def game_intro(self):
        time.sleep(1)
        print("""
                                TEXT-BASED ADVENTURE GAME""")
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
        print("    GAME OBJECTIVE:")
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

        print("    COMMANDS:")
        time.sleep(0.5)
        print("   'move [direction]' - move around (north, south, east, west)")
        time.sleep(0.5)
        print("   'collect [item]' - collect the item in the room")
        time.sleep(0.5)
        print("   'use potion' - heal yourself using a potion")
        time.sleep(0.5)
        print("   'read note' - reads the note you've collected")
        time.sleep(0.5)
        print("   'inventory' - see what you've collected")
        time.sleep(0.5)
        print("   'map' - see the blueprint of the house")
        time.sleep(0.5)
        print("   'save' - save your game")
        time.sleep(0.5)
        print("   'quit' - leave the game")
        time.sleep(0.5)
        self.dash("-")
        print("")

    def check_locked_room(self, room, attempts=0):
        if 'locked' in self.rooms[room] and self.rooms[room]['locked']:
            print(f"The {room} is locked.")
            while attempts < self.max_password_attempts:
                password = input(f"Enter the Pin (----): ")
                if password == self.rooms[room].get('password', ''):
                    time.sleep(1)
                    print(f"\nYou've unlocked the {room}!")
                    self.rooms[room]['locked'] = False
                    return False
                else:
                    time.sleep(1)
                    attempts += 1
                    print(f"\nWrong password. {self.max_password_attempts - attempts} attempts left.")
            s = rd.choice(['north', 'south', 'east', 'west'])
            while True:
                if s not in self.rooms[self.current_room]:
                    s = rd.choice(['north', 'south', 'east', 'west'])
                else:
                    break
            print(f"Too many wrong attempts. You're being sent {s}.")
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
        print(layout)

    def ghost(self):
        time.sleep(1)
        print('\nOh no!',end='')
        time.sleep(1)
        print(' A Ghost!')
        time.sleep(1)
        print("The ghost attacks!")
        time.sleep(1)
        s = rd.choice(list(self.ghost_damage.keys()))
        s1 = f' {s} ' if s != 'normal' else ' '
        self.health -= self.ghost_damage[s]
        if self.health <= 0:
            print("The ghost has defeated you! You died...")
            return True
        else:
            print(f"You were attacked by a{s1}ghost.")
            time.sleep(1)
            print(f"Your health is now {self.health}.")
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
            print(f"You used a{s1}potion. Your health is now {self.health}.")
        elif self.health == 100:
            print("Your health is already full. You can't use a potion now.")
        elif potions_count == 0:
            print("No potions in your inventory!")

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
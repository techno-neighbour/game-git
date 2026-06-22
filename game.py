import time 
import threading
import random as rd
import os
import sys
try:
    import msvcrt
except ImportError:
    msvcrt = None
from settings import g_func, Colors, timed_input

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def timed_key_input(timeout_check_func):
    if sys.platform != 'win32' or msvcrt is None:
        return sys.stdin.read(1).lower()
    while True:
        if timeout_check_func():
            return None
        if msvcrt.kbhit():
            ch = msvcrt.getwch().lower()
            if ch in ('\x00', '\xe0'):
                if msvcrt.kbhit():
                    msvcrt.getwch()
                continue
            return ch
        time.sleep(0.05)

# variables for the game
def game_start():
    SAVE_FILE = 'game_save.json' # file to save the game state
    time_up = False
    time_limit = 300

    ss = g_func() # initialize the game state

    def initialize_new_game(ss):
        # randomly selects a note and gets text
        n = rd.choice(list(ss.note.keys()))
        nk = ss.note[n]
        rv = list(ss.rooms.values())

        # Select 6 unique rooms for keys, potions, and note to prevent item overwriting
        item_rooms = rd.sample(rv, 6)
        sk = item_rooms[0:3]
        sp = item_rooms[3:5]
        nt = item_rooms[5]

        # Select 3 unique rooms for ghosts
        sg = rd.sample(rv, 3)

        # Select locked room nl (cannot be the note room nt)
        nl = rd.choice(rv)
        while nl == nt:
            nl = rd.choice(rv)

        for room in sp:
            room['item'] = 'potion'
            room['item_pos'] = (rd.randint(1, 7), rd.randint(1, 7))
        for room in sk:
            room['item'] = 'key'
            room['item_pos'] = (rd.randint(1, 7), rd.randint(1, 7))
        for room in sg:
            room.update({'ghost': True, 'attacked': False})
            room['ghost_pos'] = (rd.randint(1, 7), rd.randint(1, 7))

        nt['item'] = 'note'
        nt['item_pos'] = (rd.randint(1, 7), rd.randint(1, 7))
        nl.update({'locked': True, 'password': str(n)})

        # Ensure door, hall, hallway don't have ghosts, keys, or potions
        ss.rooms.update({
            'Door': {'west': 'Foyer'},
            'Hall': {'south': 'Hallway', 'east': 'Foyer', 'west': 'Library', 'north': 'Shrine'},
            'Hallway': {'north': 'Hall', 'east': 'Kitchen', 'south': 'Guestroom', 'west': 'Bedroom'}
        })
        
        # Reset player position
        ss.player_r = 4
        ss.player_c = 4
        
        return n, nk

    # to check if a game file exists and user wants to load it
    if os.path.exists(SAVE_FILE):
        choice = input("Your last game save is available.\nDo you want to load it? (yes/no): ").strip().lower()
        time.sleep(0.25)

        while (choice != 'yes' and choice != 'no'): # ensures valid input
            time.sleep(0.5)
            print("Please enter 'yes' or 'no' only.\n")
            time.sleep(0.5)
            choice = input("Do you want to load your last save? (yes/no): ").strip().lower()
        time.sleep(1)

        if choice == 'yes': # if user wants to load the last save
            try:
                ss, n, nk = ss.load(SAVE_FILE)
                time.sleep(1)
                print("Loading your last save",end="", flush=True)
                time.sleep(0.5)
                print(".", end='', flush=True)
                time.sleep(0.5)
                print(".", end='', flush=True)
                time.sleep(0.5)
                print(".")
                time.sleep(0.25)
                print("Game loaded successfully!")
                print("")
            except Exception as e:
                time.sleep(1)
                print(Colors.yellow(f"\nWarning: Save file load failed (corrupted or invalid save file: {e})."))
                time.sleep(1)
                print("Starting a new game instead...\n")
                time.sleep(1)
                n, nk = initialize_new_game(ss)

        else:
            n, nk = initialize_new_game(ss)
    else:
        n, nk = initialize_new_game(ss)
    ss.game_intro() # game premise and instructions

    def countdown_timer(): # game time limit
        nonlocal time_up
        start = time.time()
        while time.time() - start < time_limit:
            time.sleep(1)
        time_up = True
        ss.time_up = True

    threading.Thread(target=countdown_timer, daemon=True).start() # start countdown timer in a separate thread

    start_time = time.time()
    action_message = ""

    def render_game_screen(action_message=""):
        clear_screen()
        print(ss.draw_room(ss.player_r, ss.player_c))
        print("\n" + "=" * 55)
        
        # Calculate remaining time
        elapsed = time.time() - start_time
        remaining = max(0, int(time_limit - elapsed))
        mins, secs = divmod(remaining, 60)
        time_str = f"{mins:02d}:{secs:02d}"
        
        # Health bar
        num_blocks = int(ss.health / 10)
        health_bar = "■" * num_blocks + "░" * (10 - num_blocks)
        health_color = Colors.green if ss.health > 20 else Colors.red
        
        print(f" Location: {Colors.cyan(ss.current_room)}")
        print(f" HP:       [{health_color(health_bar)}] {ss.health} HP")
        print(f" Time:     {Colors.yellow(time_str)}")
        potions_str = Colors.green(str(ss.inventory.get('potion', 0)))
        keys_str = Colors.green(str(ss.inventory.get('key', 0)))
        print(f" Items:    Keys: {keys_str}/3 | Potions: {potions_str}")
        if ss.inventory.get('note', 0) > 0:
            print(f" Note:     '{Colors.yellow(nk)}'")
        print("-" * 55)
        if action_message:
            print(f" {action_message}")
        else:
            print(" Walk around the room to collect items and find doorways.")
        print("=" * 55)
        print(f" Controls: {Colors.yellow('WASD')} - Move | {Colors.yellow('U')} - Potion | {Colors.yellow('R')} - Read Note | {Colors.yellow('V')} - Save | {Colors.yellow('Q')} - Quit")

    # main game loop
    while not time_up:
        render_game_screen(action_message)
        action_message = "" # clear message for next turn

        key = timed_key_input(lambda: time_up)
        if key is None or time_up:
            ss.death_by_patron()
            break
            
        room_data = ss.rooms[ss.current_room]
        
        if key == 'q':
            clear_screen()
            print(Colors.red("You chose to die! "), end='', flush=True)
            time.sleep(1)
            print(Colors.red("May your soul be at peace."))
            break
            
        elif key == 'v':
            clear_screen()
            ss.save(n, nk, SAVE_FILE)
            time.sleep(1.5)
            
        elif key == 'u':
            clear_screen()
            ss.use_potion()
            time.sleep(1.5)
            
        elif key == 'r':
            clear_screen()
            if ss.inventory.get('note', 0) > 0:
                print(f"The note reads: '{Colors.yellow(nk)}'")
            else:
                print("You don't have a note.")
            time.sleep(2.5)
            
        elif key in ('w', 'a', 's', 'd'):
            # Calculate target coordinates
            tr, tc = ss.player_r, ss.player_c
            if key == 'w': tr -= 1
            elif key == 's': tr += 1
            elif key == 'a': tc -= 1
            elif key == 'd': tc += 1
            
            # Check walkability / doorways
            is_doorway = False
            next_room = None
            entry_r, entry_c = 4, 4
            
            if tr == 0 and tc == 4:
                is_doorway = True
                if 'north' in room_data:
                    next_room = room_data['north']
                    entry_r, entry_c = 7, 4
            elif tr == 8 and tc == 4:
                is_doorway = True
                if 'south' in room_data:
                    next_room = room_data['south']
                    entry_r, entry_c = 1, 4
            elif tr == 4 and tc == 0:
                is_doorway = True
                if 'west' in room_data:
                    next_room = room_data['west']
                    entry_r, entry_c = 4, 7
            elif tr == 4 and tc == 8:
                is_doorway = True
                if 'east' in room_data:
                    next_room = room_data['east']
                    entry_r, entry_c = 4, 1
                    
            if is_doorway:
                if next_room is not None:
                    # Check locked room/door connection
                    if next_room == 'Door':
                        if ss.inventory.get('key', 0) == ss.required_keys:
                            # Victory!
                            ss.current_room = 'Door'
                            break
                        else:
                            action_message = Colors.red("The Door won't open! You need all 3 keys.")
                    elif ss.rooms[next_room].get('locked'):
                        clear_screen()
                        print(f"The doorway to {Colors.cyan(next_room)} is locked!")
                        if ss.check_locked_room(next_room):
                            # Ejected to a random room!
                            continue
                        else:
                            # Unlocked! Continue into the room
                            ss.current_room = next_room
                            ss.player_r = entry_r
                            ss.player_c = entry_c
                            action_message = f"You entered {Colors.cyan(ss.current_room)}."
                    else:
                        # Move to adjacent room
                        if 'ghost' in room_data:
                            room_data['attacked'] = False
                            
                        ss.current_room = next_room
                        ss.player_r = entry_r
                        ss.player_c = entry_c
                        action_message = f"You entered {Colors.cyan(ss.current_room)}."
                else:
                    action_message = Colors.yellow("You can't go that way!")
            elif 1 <= tr <= 7 and 1 <= tc <= 7:
                # Walk inside current room
                ss.player_r = tr
                ss.player_c = tc
                
                # Check item pick up
                if 'item' in room_data and room_data.get('item_pos') == (tr, tc):
                    item = room_data['item']
                    ss.inventory[item] = ss.inventory.get(item, 0) + 1
                    item_colored = Colors.green(item) if item in ('key', 'potion') else Colors.yellow(item)
                    action_message = f"You picked up a {item_colored}!"
                    if item == 'note':
                        action_message += f" Note reads: '{Colors.yellow(nk)}'"
                    del room_data['item']
                    if 'item_pos' in room_data:
                        del room_data['item_pos']
                    
                # Check ghost attack
                elif room_data.get('ghost') and not room_data.get('attacked') and room_data.get('ghost_pos') == (tr, tc):
                    clear_screen()
                    if ss.ghost():
                        break
                    ss.health = ss.give_health()
                    room_data['attacked'] = True
                    time.sleep(1.5)
            else:
                action_message = Colors.yellow("Ouch! You hit a wall.")

    if ss.current_room == 'Door' and ss.inventory.get('key', 0) == ss.required_keys:
        print(Colors.green("\nYou have made it to the exit and start to run. "), end='', flush=True)
        time.sleep(2)
        print(Colors.green('While you run, you start to think, '), end='', flush=True)
        time.sleep(2.5)
        print(Colors.green("'Why were there ghosts in the house?'"), end='', flush=True)
        time.sleep(2.5)
        print(Colors.green(" That's when you realize...\n"), flush=True)
        time.sleep(3)
    else:
        ss.death_by_patron()

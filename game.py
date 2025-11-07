import time 
import threading
import random as rd
import os
from settings import g_func

# variables for the game
def game_start():
    SAVE_FILE = 'game_save.json' # file to save the game state
    inventory = {}
    health = 200
    time_up = False
    time_limit = 360

    ss = g_func() # initialize the game state

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
            ss, n, nk = ss.load(SAVE_FILE)
            time.sleep(1)
            print("Loading your last save",end="", flush=True)
            time.sleep(1)
            print(".", end='', flush=True)
            time.sleep(1)
            print(".", end='', flush=True)
            time.sleep(1)
            print(".")
            time.sleep(1)
            print("Game loaded successfully!")
            time.sleep(1)
            print("")

        else:
            n = rd.choice(list(ss.note.keys())) # randomly selects a note
            nk = ss.note[n] # gets the text of the note
            rv = list(ss.rooms.values()) # gets the list of rooms
            sk, sg, sp = rd.sample(rv, 3), rd.sample(rv, 3), rd.sample(rv, 2) # randomly selects rooms for keys, ghosts, potions
            nt, nl = rd.choice(rv), rd.choice(rv) # randomly selects rooms for note and locked room

            while nt == nl: # ensures that the note and locked room are not in the same room
                nt, nl = rd.choice(rv), rd.choice(rv)

            for room in sp:
                room['item'] = 'potion' # assigning potions to rooms
            for room in sk:
                room['item'] = 'key' # assigning keys to rooms
            for room in sg:
                room.update({'ghost': True, 'attacked': False}) # assigning ghosts to rooms

            nt['item'] = 'note'
            nl.update({'locked': True, 'password': str(n)}) # setting the locked room with a password

            # making sure that the door, hall, and hallway don't have ghosts,keys, or potions
            ss.rooms.update({
                'Door': {'west': 'Foyer'},
                'Hall': {'south': 'Hallway', 'east': 'Foyer', 'west': 'Library', 'north': 'Shrine'},
                'Hallway': {'north': 'Hall', 'east': 'Kitchen', 'south': 'Guestroom', 'west': 'Bedroom'}
            })
    else:
        n = rd.choice(list(ss.note.keys())) # randomly selects a note
        nk = ss.note[n] # gets the text of the note
        rv = list(ss.rooms.values()) # gets the list of rooms
        sk, sg, sp = rd.sample(rv, 3), rd.sample(rv, 3), rd.sample(rv, 2) # randomly selects rooms for keys, ghosts, potions
        nt, nl = rd.choice(rv), rd.choice(rv) # randomly selects rooms for note and locked room

        while nt == nl: # ensures that the note and locked room are not in the same room
            nt, nl = rd.choice(rv), rd.choice(rv)

        for room in sp:
            room['item'] = 'potion' # assigning potions to rooms
        for room in sk:
            room['item'] = 'key' # assigning keys to rooms
        for room in sg:
            room.update({'ghost': True, 'attacked': False}) # assigning ghosts to rooms

        nt['item'] = 'note'
        nl.update({'locked': True, 'password': str(n)}) # setting the locked room with a password

        # making sure that the door, hall, and hallway don't have ghosts,keys, or potions
        ss.rooms.update({
            'Door': {'west': 'Foyer'},
            'Hall': {'south': 'Hallway', 'east': 'Foyer', 'west': 'Library', 'north': 'Shrine'},
            'Hallway': {'north': 'Hall', 'east': 'Kitchen', 'south': 'Guestroom', 'west': 'Bedroom'}
        })
    ss.game_intro() # game premise and instructions

    def countdown_timer(): # game time limit
        global time_up
        start = time.time()
        while time.time() - start < time_limit:
            time.sleep(1)
        time_up = True

    threading.Thread(target=countdown_timer, daemon=True).start() # start countdown timer in a separate thread

    # main game loop
    while not time_up:
        ss.status()

        if ss.check_locked_room(ss.current_room):
            continue

        room_data = ss.rooms[ss.current_room]

        if 'item' in room_data:
            time.sleep(1)
            print(f"You see a {room_data['item']} here.")

        if room_data.get('ghost') and not room_data['attacked']:
            if ss.ghost():
                break
            ss.health = ss.give_health()
            room_data['attacked'] = True

        time.sleep(1)
        command = input("\nWhat's your move? ").lower().split()
        print()
        time.sleep(1)
        if not command: # if no command is given
            print('Invalid command.')
            time.sleep(1)
            print('Please enter a valid command')
            continue

        if time_up:
            ss.death_by_patron()
            break

        action = command[0]

        if action == 'quit':
            print("You chose to die! ", end='', flush=True)
            time.sleep(1)
            print("May your soul be at peace.")
            break

        elif action == 'save':
            ss.save(n, nk, SAVE_FILE)

        elif action == 'inventory':
            potions = ss.inventory.get('potion', 0)
            keys = ss.inventory.get('key', 0)
            print(f"Your inventory: {ss.inventory} (Keys: {keys}) (Potions: {potions})")

        elif action == 'move' and len(command) > 1:
            direction = command[1]
            if direction in room_data:
                next_room = room_data[direction] # stores the next room data based on the direction

                if ss.current_room == 'Foyer' and direction == 'east' and ss.inventory.get('key', 0) < ss.required_keys:
                    time.sleep(1)
                    print("The Door won't open! You need all 3 keys.")
                else:
                    # resets attack status only when actually leaving
                    if 'ghost' in room_data:
                        room_data['attacked'] = False

                    ss.current_room = next_room
                    time.sleep(1)
                    print(f"You moved to the {ss.current_room}.")
            else:
                time.sleep(1)
                print("You can't go that way!")

        elif action == 'read' and len(command) > 1 and command[1] == 'note':
            if ss.inventory.get('note', 0) > 0:
                print(f"The note reads: '{nk}'")
            else:
                print("You don't have a note.")

        elif action == 'collect' and len(command) > 1:
            item = command[1]
            if room_data.get('item') == item:
                ss.inventory[item] = ss.inventory.get(item, 0) + 1
                print(f"You picked up a {item}.")
                if item == 'note':
                    print(f"The note reads: '{nk}'")
                del room_data['item']
            else:
                print(f"There's no {item} here.")

        elif action == 'use' and len(command) > 1 and command[1] == 'potion':
            ss.use_potion()

        elif action == 'map':
            ss.blueprint()

        else:
            print('Invalid command. Please enter a valid direction, item, or action.')

        if ss.current_room == 'Door' and ss.inventory.get('key', 0) == ss.required_keys:
            print("\nYou have made it to the exit and start to run. ", end='', flush=True)
            time.sleep(2)
            print('While you run, you start to think, ', end='', flush=True)
            time.sleep(2.5)
            print("'Why were there ghosts in the house?'", end='', flush=True)
            time.sleep(2.5)
            print(" That's when you realize...", flush=True)
            time.sleep(3)
            break
    else:
        ss.death_by_patron()

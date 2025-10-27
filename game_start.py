from game import game_start

if __name__ == "__main__":
    try:
        game_start()
    except KeyboardInterrupt:
        print(" Stopped executing: User interruption") 
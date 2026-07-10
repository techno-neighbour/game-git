import sys, time, select
try:
    import termios
    import tty
except ImportError:
    pass

def test_input():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        while True:
            rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
            if rlist:
                ch = sys.stdin.read(1)
                print(f"got {repr(ch)}\r")
                if ch == 'q':
                    break
            else:
                print("tick\r")
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

test_input()

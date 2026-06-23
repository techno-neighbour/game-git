# 🕹️ The Exit Command

A retro, text-based terminal escape Roguelike puzzle game built for the command line.

You play as a student PG trapped in a mysterious house by your patron. To survive, you must explore rooms, gather items, manage your health, and find the way out before the clock runs out!

---

## 🚀 Quick Start

### Prerequisites
* **Python**: Python 3.8 or later
* **Terminal**: A terminal emulator supporting **ANSI escape codes** and **UTF-8 character/emoji encoding**.
  * *Windows*: **Windows Terminal** is highly recommended for best emoji and color support.
  * *macOS/Linux*: Default terminals (Terminal.app, iTerm2, Alacritty) work out-of-the-box.

### Run the Game
1. **Clone this repository**:
   ```bash
   git clone https://github.com/techno-neighbour/GameGit.git
   ```
2. **Navigate into the directory**:
   ```bash
   cd GameGit
   ```
3. **Run the launch command**:
   ```bash
   python game_start.py
   ```

---

## 🎮 How to Play

### Legend
* 🧑 : **Player Character** (You!)
* 👻 : **Ghost** (Wandering hazards that deal damage)
* 🔑 : **Key** (Collect 3 to unlock the exit door)
* 🧪 : **Potion** (Use to restore 40 Health Points)
* 📜 : **Note** (Lore and clues with hints to locked door passwords)
* ██ : **Room Walls** (Cyan boundaries)
* `. ` : **Floor** (Walkable space)

### Controls
* `W` / `A` / `S` / `D` : **Move character** (North, West, South, East)
* `M` : **Toggle House Map** (Shows layout and room connections)
* `U` : **Use Potion** (Restores HP if you have one in inventory)
* `R` : **Read Note** (Displays note text clues)
* `V` : **Save Game** (Persists progress to `game_save.json`)
* `Q` : **Quit** (Exit the game)

### Objective
Explore the rooms of the haunted house, collect **3 hidden keys**, and escape through the exit door (`Door`) connected to the `Foyer` before the **5-minute timer** runs out. Avoid wandering ghosts, read notes to figure out room passwords, and keep your health above 0!

---

## 🛠️ Tech Stack & Libraries
* **Language**: Python 3
* **Libraries**:
  * `msvcrt` (Standard library on Windows for non-blocking console key detection)
  * `threading` & `time` (For managing the real-time timer and background ghost movement updates)
  * `json` (Used for reading and writing saved game states)

---

## 📺 Recommended Terminal Settings
* **Font**: Monospaced (e.g., Fira Code, JetBrains Mono, MS Gothic, Cascadia Code)
* **Window Size**: Minimum **80x25 characters** (100x30 or wider recommended to comfortably view side-by-side room grids and sidebar logs)
* **Color**: UTF-8 and 256-color support enabled.

# 🚀 Alien Invasion (Pygame)

* **University:** Karabakh University

* **Faculty:** Faculty of Mathematics and Information Technologies

* **Major:** Computer Engineering

* **Course:** Fundamentals of Programming 1

* **Instructor:** Shamil Humbatov

* **Group:** Group 9

* **Team Members:** Ibrahim Aliyev, Ismat Gurbanov, Safar Garayev, Elchin Abdurahimov, and Umid Aliyev

A 2D space shooter (arcade) game developed collaboratively using Python and the **Pygame** library. This project is structured modularly following modern software development teamwork principles (Git/GitHub branching and Pull Request workflow).

## ✨ Key Features

* **Smooth Movement Mechanics:** Seamless left and right spaceship movement constrained within screen boundaries using `float`-based coordinate tracking.

* **Firing & Projectile System:** A `Sprite`-based bullet system that fires directly from the top center of the ship, allowing a maximum of 3 active bullets on the screen simultaneously.

* **Memory Optimization:** Automatic removal of bullets from memory once they pass beyond the top edge of the screen.

* **Centralized Configuration:** Unified management of screen dimensions, colors, speed factors, and bullet limits via a dedicated `Settings` class.

## 📁 Project Structure

```
alien-invasion/
│
├── images/
│   └── ship.bmp            # Spaceship sprite image
│
├── alien_invasion.py       # Main game entry point and core loop (Main Loop)
├── settings.py             # Centralized visual and physical game settings
├── ship.py                 # Spaceship class, image scaling, and movement logic
├── bullet.py               # Bullet class inheriting from Pygame's Sprite
├── game_functions.py       # Keyboard event handling, bullet updates, and screen rendering
└── README.md               # Project documentation

```

## 👥 Team Roles & Git Workflow

The project was divided into 4 core engineering roles. Each member developed their module in a dedicated Git branch and merged their work into the `main` branch via **Pull Requests**:

| Role | Git Branch | Responsible Files | Key Responsibilities | Assignee | 
| ----- | ----- | ----- | ----- | ----- | 
| **1. System Architect** | `feature-settings-main` | `settings.py`, `alien_invasion.py` | Repository setup, creating the `Settings` class, and building the main game loop (`run_game`). | Ibrahim Aliyev | 
| **2. Ship Engineer** | `feature-ship-movement` | `ship.py`, `images/ship.bmp` | Loading and scaling the ship image (`60x60`), setting transparency (`colorkey`), and implementing boundary-checked movement. | `[Full Name]` | 
| **3. Weapons & Projectile Engineer** | `feature-bullet-system` | `bullet.py` | Creating the `Sprite`-based `Bullet` class, spawning bullets at the ship's nose, and handling upward motion. | `[Full Name]` | 
| **4. Controls & Display Engineer** | `feature-game-functions` | `game_functions.py` | Handling keyboard events (`KEYDOWN`/`KEYUP`), cleaning up off-screen bullets, and updating the display. | `[Full Name]` | 

## 🎮 Controls

| Key | Action | 
| ----- | ----- | 
| **`→` (Right Arrow)** | Move the spaceship to the right | 
| **`←` (Left Arrow)** | Move the spaceship to the left | 
| **`Space`** | Fire a bullet (max. 3 on screen at once) | 
| **`Q`** | Quit the game | 

## ⚙️ Installation & Execution

Follow these steps to run the game locally on your machine:

1. **Clone the repository:**

   ```
   git clone <repository-url>
   cd alien-invasion
   
   ```

2. **Install the required dependency (`pygame`):**

   ```
   pip install pygame
   
   ```

3. **Run the game:**

   ```
   python alien_invasion.py
   
   ```
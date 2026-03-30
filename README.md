# ASTROS 🚀

A simple arcade-style space shooter built with **Pygame**.
Dodge meteorites, shoot them down, and survive as long as you can while racking up your score.

---

## 🎮 Gameplay
You control a small ship drifting through space. Meteorites fall from above in waves, and your job is to avoid them or destroy them with projectiles.
From time to time, upgrades will spawn — grab them before they disappear (currently they just get collected, but they’re ready for expansion).
The game ends when your ship is hit.

---

## 🕹 Controls
* **Arrow Keys** → Move the ship
* **Space** → Shoot
* **Enter** → Start the game
* **R** → Restart after Game Over
* **F1** → Toggle fullscreen
* **F2** → Toggle debug mode (shows hitboxes)
---

## 🧠 Features
* Smooth ship movement and shooting
* Random meteor spawning with spacing logic
* Basic collision system using hitboxes
* Explosion animations on impact
* Score tracking
* Upgrade system (expandable)
* Background starfield effect
* Sound effects and looping music
* Debug mode for collision visualization

---
## ⚙️ Requirements
* Python 3.x
* Pygame

Install dependencies:
```bash
pip install pygame
```

---

## ▶️ Running the Game
```bash
python main.py
```

---

## 🛠 Notes
* The upgrade system is currently minimal (collect-only), but the structure is there to extend it with effects (fire rate, speed, etc.).
* Collision uses custom hitboxes instead of raw sprite rectangles for better control.
* Debug mode is useful if you're tweaking collision or spawn behavior.

---

## 📌 Future Ideas
* Add actual upgrade effects (power-ups)
* Different meteor types (sizes, speeds)
* Player health instead of instant death
* Menu polish and UI improvements
* Sound/music settings
* Difficulty scaling over time

---

## 👨‍💻 Author
Made as a small Pygame project focused on gameplay fundamentals and clean structure.

---

Enjoy the game 👾

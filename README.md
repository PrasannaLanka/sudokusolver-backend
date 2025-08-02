
---

## ✅ Backend `README.md`

```markdown
# 🔗 Let's solve sudoku — Backend

This is the **Flask backend** for the Sudoku Solver app. It handles puzzle generation, user auth, save/resume features, and streak tracking.

---

## 🔗 Frontend Repo  
👉 [Sudoku Frontend (React)](https://github.com/PrasannaLanka/sudokusolver-frontend.git)

---

## ⚙️ Features

- 🧩 Generates valid Sudoku puzzles (3 difficulties)
- 🔐 Login & Signup with JWT authentication
- 💾 Save/resume last puzzle for each user
- 🔥 Tracks streaks and last-played time
- 🗂️ Lightweight SQLite DB for storage
- 🌐 CORS-enabled for frontend integration

---

## 🛠 Tech Stack

- Python 3.x
- Flask
- Flask-JWT-Extended
- SQLite
- Flask-CORS

---

## 🛠 Setup Instructions

```bash
git clone https://github.com/PrasannaLanka/sudokusolver-backend.git
cd sudoku-backend
pip install -r requirements.txt
python app.py

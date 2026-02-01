# 🔗 Let's Solve Sudoku — Backend

This is the **Flask backend** for the Sudoku Solver app. It handles puzzle generation, user authentication, save/resume functionality, and streak tracking.

---
## 🔗 Website is now live on Vercel and Railway  
👉 [Sudoku Game for kids](https://sudokugameforkids.vercel.app/)

## 🔗 Frontend Repository  
👉 [Sudoku Frontend (React)](https://github.com/PrasannaLanka/sudokusolver-frontend.git)

---

## ⚙️ Features

- 🧩 Generates valid Sudoku puzzles (Easy / Medium / Hard)
- 🔐 Login & Signup with JWT authentication
- 💾 Save/resume last puzzle for each user
- 🔥 Tracks daily streaks and last-played date
- 🗂️ Lightweight SQLite database for storage
- 🌐 CORS-enabled for seamless frontend integration

---

## 🛠 Tech Stack

- Python 3.x
- Flask
- Flask-JWT-Extended
- SQLite
- Flask-CORS

---

## 🚀 Setup Instructions

```bash
# Clone the repo
git clone https://github.com/PrasannaLanka/sudokusolver-backend.git
cd sudokusolver-backend

# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py

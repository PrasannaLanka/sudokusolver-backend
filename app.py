import random
import numpy as np
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from auth import auth_bp, init_db
from flask_jwt_extended import jwt_required, get_jwt_identity
from sudoku_extra import sudoku_bp, init_extra_tables
from datetime import timedelta
from db_utils import get_db
import os


app = Flask(__name__)

init_db()
init_extra_tables()

app.config['JWT_SECRET_KEY'] = 'super-secret-key'
CORS(
    app,
    supports_credentials=True,
    resources={
        r"/*": {
            "origins": [
                "http://localhost:3000"          # local dev
                "https://sudokugameforkids.vercel.app", # production
            ]
        }
    }
)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)  
jwt = JWTManager(app)

@app.route("/")
def health():
    return {"status": "backend alive"}

# init_db()
# init_extra_tables()
app.register_blueprint(auth_bp)
app.register_blueprint(sudoku_bp)
def is_board_valid(board):
    def is_valid_group(group):
        nums = [n for n in group if n != 0]
        return len(nums) == len(set(nums))

    for i in range(9):
        row = board[i]
        col = [board[r][i] for r in range(9)]
        if not is_valid_group(row) or not is_valid_group(col):
            return False

    for box_row in range(0, 9, 3):
        for box_col in range(0, 9, 3):
            block = [
                board[r][c]
                for r in range(box_row, box_row + 3)
                for c in range(box_col, box_col + 3)
            ]
            if not is_valid_group(block):
                return False

    return True

def is_valid(board, row, col, num):
    """Check if a number can be placed in the given row and column."""
    for i in range(9):
        if board[row][i] == num or board[i][col] == num:
            return False

    start_row, start_col = (row // 3) * 3, (col // 3) * 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def solve_sudoku(board):
    """Solve the Sudoku board using backtracking."""
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                nums = list(range(1, 10))
                random.shuffle(nums)  

                for num in nums:
                    if is_valid(board, row, col, num):
                        board[row][col] = num
                        if solve_sudoku(board):
                            return True
                        board[row][col] = 0
                return False
    return True
def fill_diagonal_boxes(board):
    for i in range(0, 9, 3):
        nums = list(range(1, 10))
        random.shuffle(nums)
        idx = 0
        for r in range(3):
            for c in range(3):
                board[i + r][i + c] = nums[idx]
                idx += 1


def has_unique_solution(board):
    """Check if a Sudoku board has only one valid solution."""
    count = 0

    def solve(b):
        nonlocal count
        for row in range(9):
            for col in range(9):
                if b[row][col] == 0:
                    for num in range(1, 10):
                        if is_valid(b, row, col, num):
                            b[row][col] = num
                            solve(b)
                            b[row][col] = 0
                    return
        count += 1
        if count > 1:
            return  # Early exit if multiple solutions

    copied = [row[:] for row in board]
    solve(copied)
    return count == 1

def generate_sudoku(difficulty):
    """Generate a Sudoku puzzle based on difficulty level."""
    board = np.zeros((9, 9), dtype=int)
    fill_diagonal_boxes(board)
    solve_sudoku(board)
    solution = board.copy()
    puzzle = board.copy()

    # Define number of given clues based on difficulty
    if difficulty == 'easy':
        num_clues = random.randint(37, 45)
    elif difficulty == 'medium':
        num_clues = random.randint(22, 36)
    elif difficulty == 'hard':
        num_clues = random.randint(17, 22)
    else:
        return None, None  # Invalid difficulty

    # Remove numbers until only `num_clues` remain, ensuring a unique solution
    removed_positions = set()
    while (81 - len(removed_positions)) > num_clues:
        row, col = random.randint(0, 8), random.randint(0, 8)
        if (row, col) not in removed_positions:
            puzzle[row][col] = 0
            removed_positions.add((row, col))

            # Check if the puzzle still has a unique solution
            # if not has_unique_solution(puzzle):
            #     puzzle[row][col] = solution[row][col]
            #     removed_positions.remove((row, col))

    return solution.tolist(), puzzle.tolist()

@app.route('/protected_data', methods=['GET'])
@jwt_required()
def protected_data():
    current_user = get_jwt_identity()
    return jsonify({"message": f"Hello {current_user}, you're authenticated!"})

@app.route('/generate', methods=['GET'])
@jwt_required()
def generate():
    """API endpoint to generate a Sudoku puzzle with a specified difficulty and clear saved game."""
    difficulty = request.args.get('difficulty', 'medium').lower()
    user = get_jwt_identity()

    # Delete saved game for this user
    conn = get_db()
    conn.execute('DELETE FROM saved_games WHERE username = ?', (user,))
    conn.commit()
    conn.close()

    # Generate puzzle
    solution, puzzle = generate_sudoku(difficulty)
    
    if solution is None:
        return jsonify({'error': 'Invalid difficulty. Choose from easy, medium, hard.'}), 400

    return jsonify({'puzzle': puzzle, 'solution': solution, 'difficulty': difficulty})

    
    return jsonify({'puzzle': puzzle, 'solution': solution, 'difficulty': difficulty})
@app.route("/record_game", methods=["POST"])
@jwt_required()
def record_game():
    current_user = get_jwt_identity()
    data = request.get_json()
    time_taken = data.get("timeTaken")
    difficulty = data.get("difficulty")
    date = data.get("date")  # 'YYYY-MM-DD'

    if time_taken is None or difficulty is None or date is None:
        return jsonify({"message": "Missing fields", "status": "error"}), 400

    conn = get_db()
    cursor = conn.cursor()

    # Insert into leaderboard
    cursor.execute(
        "INSERT INTO leaderboard (username, difficulty, time_taken) VALUES (?, ?, ?)",
        (current_user, difficulty, time_taken)
    )

    # Insert/update daily_results
    cursor.execute(
        "SELECT id FROM daily_results WHERE username = ? AND date = ?",
        (current_user, date)
    )
    existing = cursor.fetchone()

    if existing:
        cursor.execute(
            "UPDATE daily_results SET time_taken = ? WHERE id = ?",
            (time_taken, existing["id"])
        )
    else:
        cursor.execute(
            "INSERT INTO daily_results (username, date, time_taken) VALUES (?, ?, ?)",
            (current_user, date, time_taken)
        )

    conn.commit()
    conn.close()

    return jsonify({"message": "Game recorded", "status": "success"})


@app.route('/check', methods=['POST'])
def check_solution():
    data = request.get_json()

    if not data or 'board' not in data:
        return jsonify({'error': 'Invalid request. Missing board.'}), 400

    user_board = data['board']

    if not isinstance(user_board, list) or len(user_board) != 9:
        return jsonify({'error': 'Invalid board format. Expected 9x9 grid.'}), 400

    for row in user_board:
        if not isinstance(row, list) or len(row) != 9:
            return jsonify({'error': 'Invalid board format. Each row must have 9 elements.'}), 400

    # Check for 0s — if any, the board is incomplete
    if any(0 in row for row in user_board):
        return jsonify({'message': 'Incomplete board. Fill all cells.', 'status': 'incomplete'})

    # Validate based on Sudoku rules
    if is_board_valid(user_board):
        return jsonify({'message': 'You won! 🎉 Valid Sudoku!', 'status': 'success'})
    else:
        return jsonify({'message': 'Invalid solution. ❌ Check Sudoku rules.', 'status': 'failure'})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

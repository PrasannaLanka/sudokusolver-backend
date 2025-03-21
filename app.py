import random
import numpy as np
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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
                for num in range(1, 10):
                    if is_valid(board, row, col, num):
                        board[row][col] = num
                        if solve_sudoku(board):
                            return True
                        board[row][col] = 0
                return False
    return True

def generate_sudoku(difficulty):
    """Generate a Sudoku puzzle based on difficulty level."""
    board = np.zeros((9, 9), dtype=int)
    solve_sudoku(board)
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

    # Remove numbers until only `num_clues` remain
    removed_positions = set()
    while (81 - len(removed_positions)) > num_clues:
        row, col = random.randint(0, 8), random.randint(0, 8)
        if (row, col) not in removed_positions:
            puzzle[row][col] = 0
            removed_positions.add((row, col))

    return board.tolist(), puzzle.tolist()

@app.route('/generate', methods=['GET'])
def generate():
    """API endpoint to generate a Sudoku puzzle with a specified difficulty."""
    difficulty = request.args.get('difficulty', 'medium').lower()
    solution, puzzle = generate_sudoku(difficulty)
    
    if solution is None:
        return jsonify({'error': 'Invalid difficulty. Choose from easy, medium, hard, or evil'}), 400
    
    return jsonify({'puzzle': puzzle, 'solution': solution, 'difficulty': difficulty})

@app.route('/check', methods=['POST'])
def check_solution():
    """API endpoint to check if the user's solution is correct."""
    data = request.get_json()
    user_board = data['board']
    solution = data['solution']

    if user_board == solution:
        return jsonify({'message': 'You won! 🎉'})
    else:
        return jsonify({'message': 'You lost. Try again! ❌'}), 400

if __name__ == '__main__':
    app.run(debug=True)

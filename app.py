import random
import numpy as np
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def is_valid(board, row, col, num):
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

def generate_sudoku():
    board = np.zeros((9, 9), dtype=int)
    solve_sudoku(board)
    puzzle = board.copy()
    for _ in range(40):  # Remove 40 numbers to create a puzzle
        row, col = random.randint(0, 8), random.randint(0, 8)
        puzzle[row][col] = 0
    return board.tolist(), puzzle.tolist()

@app.route('/generate', methods=['GET'])
def generate():
    solution, puzzle = generate_sudoku()
    return jsonify({'puzzle': puzzle, 'solution': solution})

@app.route('/check', methods=['POST'])
def check_solution():
    data = request.get_json()
    user_board = data['board']
    solution = data['solution']

    if user_board == solution:
        return jsonify({'message': 'You won! 🎉'})
    else:
        return jsonify({'message': 'You lost. Try again! ❌'}), 400

if __name__ == '__main__':
    app.run(debug=True)

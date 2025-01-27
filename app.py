from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow requests from your React frontend

def is_valid(board, row, col, num):
    for i in range(9):
        if board[row][i] == num or board[i][col] == num:
            return False
        if board[row // 3 * 3 + i // 3][col // 3 * 3 + i % 3] == num:
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

@app.route('/solve-sudoku', methods=['POST'])
def solve():
    try:
        data = request.get_json()
        board = data.get('board')
        if not board or len(board) != 9 or any(len(row) != 9 for row in board):
            return jsonify({"error": "Invalid board format"}), 400

        solved_board = [row[:] for row in board]  # Copy the board
        if solve_sudoku(solved_board):
            return jsonify({"solvedBoard": solved_board})
        else:
            return jsonify({"error": "No solution exists"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)

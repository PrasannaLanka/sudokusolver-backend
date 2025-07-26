import json
from datetime import datetime

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from db_utils import get_db, init_extra_tables

sudoku_bp = Blueprint('sudoku', __name__)

# Initialize tables on module load
init_extra_tables()

# --- Leaderboard Endpoints ---
@sudoku_bp.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    difficulty = request.args.get('difficulty', 'easy')
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT username, time_taken, difficulty FROM leaderboard
    WHERE LOWER(difficulty) = LOWER(?)
    ORDER BY time_taken ASC
    LIMIT 10
''', (difficulty,))

    # cursor.execute('''SELECT username, time_taken, difficulty FROM leaderboard''')

    scores = [dict(row) for row in cursor.fetchall()]
    conn.close() 
    return jsonify(scores)

@sudoku_bp.route('/leaderboard', methods=['POST'])
@jwt_required()
def submit_score():
    data = request.get_json()
    difficulty = data.get('difficulty')
    time_taken = data.get('time_taken')
    user = get_jwt_identity()
    conn = get_db()
    conn.execute('''INSERT INTO leaderboard (username, difficulty, time_taken)
                    VALUES (?, ?, ?)''', (user, difficulty, time_taken))
    conn.commit()
    conn.close() 
    return jsonify({'message': 'Score submitted.'})

# --- Save & Resume Game ---
@sudoku_bp.route('/save_game', methods=['POST'])
@jwt_required()
def save_game():
    data = request.get_json()
    puzzle = json.dumps(data.get('puzzle'))
    progress = json.dumps(data.get('progress'))
    solution = json.dumps(data.get('solution'))
    user = get_jwt_identity()

    conn = get_db()
    conn.execute('DELETE FROM saved_games WHERE username = ?', (user,))
    conn.execute('''INSERT INTO saved_games (username, puzzle, progress, solution)
                    VALUES (?, ?, ?, ?)''', (user, puzzle, progress, solution))
    conn.commit()
    conn.close() 
    return jsonify({'message': 'Game saved.'})

@sudoku_bp.route('/resume_game', methods=['GET'])
@jwt_required()
def resume_game():
    user = get_jwt_identity()
    conn = get_db()
    cursor = conn.execute('SELECT puzzle, progress, solution FROM saved_games WHERE username = ?', (user,))
    row = cursor.fetchone()
    conn.close() 
    if row:
        return jsonify({
            'puzzle': json.loads(row['puzzle']),
            'progress': json.loads(row['progress']),
            'solution': json.loads(row['solution'])
        })
    else:
        return jsonify({'message': 'No saved game found.'}), 404

# --- Daily Puzzle ---
@sudoku_bp.route('/daily_puzzle', methods=['GET'])
def daily_puzzle():
    today = datetime.now().strftime('%Y-%m-%d')
    conn = get_db()
    cursor = conn.execute('SELECT puzzle, solution FROM daily_puzzle WHERE date = ?', (today,))
    row = cursor.fetchone()
    if row:
        conn.close() 
        return jsonify({'puzzle': json.loads(row['puzzle']), 'solution': json.loads(row['solution'])})
    else:
        conn.close() 
        from app import generate_sudoku  # import if in separate file
        solution, puzzle = generate_sudoku('medium')
        conn.execute('''INSERT OR REPLACE INTO daily_puzzle (date, puzzle, solution)
                        VALUES (?, ?, ?)''', (today, json.dumps(puzzle), json.dumps(solution)))
        conn.commit()
        return jsonify({'puzzle': puzzle, 'solution': solution})

@sudoku_bp.route('/daily_result', methods=['POST'])
@jwt_required()
def daily_result():
    user = get_jwt_identity()
    data = request.get_json()
    time_taken = data.get('time_taken')
    today = datetime.now().strftime('%Y-%m-%d')
    conn = get_db()
    conn.execute('INSERT INTO daily_results (username, date, time_taken) VALUES (?, ?, ?)',
                 (user, today, time_taken))
    conn.commit()
    conn.close() 
    return jsonify({'message': 'Daily challenge recorded.'})

# --- Streak Handling ---
@sudoku_bp.route('/streak', methods=['GET'])
@jwt_required()
def get_streak():
    user = get_jwt_identity()
    conn = get_db()
    cursor = conn.execute('SELECT streak_count, last_played_date FROM user_stats WHERE username = ?', (user,))
    row = cursor.fetchone()
    conn.close() 
    if row:
        return jsonify(dict(row))
    else:
        return jsonify({'streak_count': 0, 'last_played_date': None})

@sudoku_bp.route('/update_streak', methods=['POST'])
@jwt_required()
def update_streak():
    user = get_jwt_identity()
    today = datetime.now().strftime('%Y-%m-%d')
    conn = get_db()
    cursor = conn.execute('SELECT streak_count, last_played_date FROM user_stats WHERE username = ?', (user,))
    row = cursor.fetchone()

    if row:
        last_date = row['last_played_date']
        if last_date == today:
            return jsonify({'message': 'Already updated today.'})
        elif (datetime.strptime(today, '%Y-%m-%d') - datetime.strptime(last_date, '%Y-%m-%d')).days == 1:
            new_streak = row['streak_count'] + 1
        else:
            new_streak = 1
        conn.execute('UPDATE user_stats SET streak_count = ?, last_played_date = ? WHERE username = ?',
                     (new_streak, today, user))
    else:
        conn.execute('INSERT INTO user_stats (username, streak_count, last_played_date) VALUES (?, ?, ?)',
                     (user, 1, today))
    conn.commit()
    conn.close() 
    return jsonify({'message': 'Streak updated.'})

# --- Delete Saved Game ---
@sudoku_bp.route('/delete_saved_game', methods=['DELETE'])
@jwt_required()
def delete_saved_game():
    user = get_jwt_identity()
    conn = get_db()
    conn.execute('DELETE FROM saved_games WHERE username = ?', (user,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Saved game deleted.'})

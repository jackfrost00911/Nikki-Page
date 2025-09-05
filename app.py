# Unused imports 'json' and 'os' have been removed for cleanliness
from flask import Flask, request, jsonify, g
from flask_cors import CORS
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

# --- Configuration ---
# Moved configuration variables to a central place
app.config.update(
    DATABASE='bookings.db',
    BOOKINGS_PER_DAY_LIMIT=4  # The maximum number of bookings to consider a day "full"
)

CORS(app)  # Enable CORS for all routes

# --- Database Connection Management (Your code was already perfect here) ---
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        # This allows you to access columns by name (e.g., row['datetime'])
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# --- Database Initialization ---
def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT,
                datetime TEXT NOT NULL,
                service TEXT NOT NULL,
                location TEXT,
                notes TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        db.commit()

# --- API Endpoints ---

@app.route('/api/bookings', methods=['POST'])
def create_booking():
    data = request.json
    
    # --- Improvement: Input Validation ---
    required_fields = ['name', 'email', 'datetime', 'service']
    missing_fields = [field for field in required_fields if field not in data or not data[field]]
    
    if missing_fields:
        return jsonify({
            'success': False,
            'message': f"Validation error: Missing required fields: {', '.join(missing_fields)}"
        }), 400 # 400 Bad Request

    # You could add more validation here, e.g., for email format or datetime format
    
    db = get_db()
    try:
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO bookings (name, email, phone, datetime, service, location, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['name'],
            data['email'],
            data.get('phone'), # .get() is great for optional fields
            data['datetime'],
            data['service'],
            data.get('location'),
            data.get('notes')
        ))
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'Booking request submitted successfully.',
            'id': cursor.lastrowid
        }), 201
    except sqlite3.IntegrityError as e:
        # Example of catching a more specific error
        return jsonify({
            'success': False,
            'message': f'Database integrity error: {str(e)}'
        }), 409 # 409 Conflict
    except Exception as e:
        # --- Improvement: Better Error Handling for Production ---
        # In a real app, you would log the error `e` here
        # For example: app.logger.error(f"Error creating booking: {e}")
        return jsonify({
            'success': False,
            'message': 'An internal server error occurred.'
        }), 500

@app.route('/api/availability', methods=['GET'])
def get_availability():
    start_date = request.args.get('start', datetime.now().strftime('%Y-%m-%d'))
    end_date_obj = datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=30)
    end_date = end_date_obj.strftime('%Y-%m-%d')
    
    db = get_db()
    cursor = db.cursor()
    
    # --- Improvement: More Efficient SQL Queries ---
    
    # Query 1: Get all individual booked slots
    cursor.execute('''
        SELECT datetime FROM bookings 
        WHERE date(datetime) BETWEEN ? AND ? 
        AND status != 'cancelled'
    ''', (start_date, end_date))
    booked_slots = [row['datetime'] for row in cursor.fetchall()]
    
    # Query 2: Let the database count bookings per day
    cursor.execute('''
        SELECT date(datetime) as booking_date, COUNT(id) as booking_count
        FROM bookings
        WHERE date(datetime) BETWEEN ? AND ?
          AND status != 'cancelled'
        GROUP BY booking_date
        HAVING booking_count >= ?
    ''', (start_date, end_date, app.config['BOOKINGS_PER_DAY_LIMIT']))
    fully_booked_dates = [row['booking_date'] for row in cursor.fetchall()]

    return jsonify({
        'booked_slots': booked_slots,
        'fully_booked_dates': fully_booked_dates
    })

if __name__ == '__main__':
    # The init_db call is perfect here for development
    init_db()
    app.run(debug=True, port=5000)


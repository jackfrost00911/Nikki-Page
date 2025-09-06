import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, jsonify, g
from flask_cors import CORS
import sqlite3
from datetime import datetime, timedelta
from twilio.rest import Client

app = Flask(__name__)

# --- Configuration ---
app.config.update(
    DATABASE='bookings.db',
    BOOKINGS_PER_DAY_LIMIT=4  # Maximum bookings per day to consider full
)

CORS(app)  # Enable CORS for all routes

# Twilio credentials from environment variables
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
MY_PHONE_NUMBER = os.getenv('MY_PHONE_NUMBER')  # Phone to receive SMS notification

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Email SMTP configuration from environment variables
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
NOTIFY_EMAIL_TO = os.getenv('NOTIFY_EMAIL_TO')  # Email to receive notifications

def send_email(subject, body, to_email):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_HOST_USER
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        server.sendmail(EMAIL_HOST_USER, to_email, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Failed to send email: {e}")

# --- Database connection management ---
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# --- Database initialization ---
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

# --- API endpoints ---
@app.route('/api/bookings', methods=['POST'])
def create_booking():
    data = request.json

    required_fields = ['name', 'email', 'datetime', 'service']
    missing_fields = [f for f in required_fields if f not in data or not data[f]]
    if missing_fields:
        return jsonify({
            'success': False,
            'message': f"Validation error: Missing required fields: {', '.join(missing_fields)}"
        }), 400

    db = get_db()
    try:
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO bookings (name, email, phone, datetime, service, location, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['name'], data['email'], data.get('phone'),
            data['datetime'], data['service'], data.get('location'), data.get('notes')
        ))
        db.commit()

        # SMS notification
        if TWILIO_ACCOUNT_SID and MY_PHONE_NUMBER and TWILIO_PHONE_NUMBER:
            message_body = f"New booking from {data['name']} for {data['service']} on {data['datetime']}."
            twilio_client.messages.create(
                body=message_body,
                from_=TWILIO_PHONE_NUMBER,
                to=MY_PHONE_NUMBER
            )

        # Email notification
        if EMAIL_HOST and NOTIFY_EMAIL_TO:
            subject = "New Booking Notification"
            body = (
                f"A new booking was made:\n\n"
                f"Name: {data['name']}\n"
                f"Email: {data['email']}\n"
                f"Phone: {data.get('phone', 'N/A')}\n"
                f"Service: {data['service']}\n"
                f"Date & Time: {data['datetime']}\n"
                f"Location: {data.get('location', 'N/A')}\n"
                f"Notes: {data.get('notes', 'N/A')}\n"
            )
            send_email(subject, body, NOTIFY_EMAIL_TO)

        return jsonify({
            'success': True,
            'message': 'Booking request submitted successfully.',
            'id': cursor.lastrowid
        }), 201

    except sqlite3.IntegrityError as e:
        return jsonify({'success': False, 'message': f'Database integrity error: {str(e)}'}), 409
    except Exception:
        return jsonify({'success': False, 'message': 'An internal server error occurred.'}), 500

@app.route('/api/availability', methods=['GET'])
def get_availability():
    start_date = request.args.get('start', datetime.now().strftime('%Y-%m-%d'))
    end_date_obj = datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=30)
    end_date = end_date_obj.strftime('%Y-%m-%d')

    db = get_db()
    cursor = db.cursor()

    cursor.execute('''
        SELECT datetime FROM bookings
        WHERE date(datetime) BETWEEN ? AND ?
        AND status != 'cancelled'
    ''', (start_date, end_date))
    booked_slots = [row['datetime'] for row in cursor.fetchall()]

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
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)

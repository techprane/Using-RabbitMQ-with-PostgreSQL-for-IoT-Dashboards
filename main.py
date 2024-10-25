from flask import Flask, render_template, request
import psycopg2
from datetime import datetime, timedelta

app = Flask(__name__)

# Database connection
def get_db_connection():
    return psycopg2.connect(
        database="iot_db", 
        user="saintvandora", 
        password="1234567890", 
        host="localhost", 
        port="5432"
    )

@app.route('/')
def dashboard():
    # Get optional time range from query parameters
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')

    conn = get_db_connection()
    cur = conn.cursor()

    # If start_time and end_time are provided, filter data within this time range
    if start_time and end_time:
        cur.execute("""
            SELECT device_id, temperature, humidity, timestamp 
            FROM iot_data 
            WHERE timestamp BETWEEN %s AND %s
            ORDER BY timestamp DESC
            """, (start_time, end_time))
    else:
        # Default query: retrieve the latest 30 records if no time range is specified
        cur.execute("SELECT device_id, temperature, humidity, timestamp FROM iot_data ORDER BY timestamp DESC LIMIT 30")

    data = cur.fetchall()

    # Get the total number of data points
    cur.execute("SELECT COUNT(*) FROM iot_data")
    data_count = cur.fetchone()[0]

    cur.close()
    conn.close()

    return render_template('dashboard.html', data=data, data_count=data_count)

if __name__ == '__main__':
    app.run(debug=True)
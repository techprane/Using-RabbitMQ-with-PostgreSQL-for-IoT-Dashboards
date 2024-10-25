from flask import Flask, jsonify, render_template, request
import psycopg2
from datetime import datetime
import pytz  # Make sure pytz is installed
import random  # Import the random module

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

# Function to insert random IoT data into the database
def insert_random_data():
    conn = get_db_connection()
    cur = conn.cursor()
    
    device_id = random.randint(1, 5)  # Assuming you have 5 devices
    temperature = random.uniform(15.0, 30.0)  # Random temperature between 15°C and 30°C
    humidity = random.uniform(30.0, 70.0)  # Random humidity between 30% and 70%
    timestamp = datetime.now(pytz.UTC)

    query = """
        INSERT INTO iot_data (device_id, temperature, humidity, timestamp)
        VALUES (%s, %s, %s, %s)
    """
    cur.execute(query, (device_id, temperature, humidity, timestamp))
    conn.commit()  # Save changes
    cur.close()
    conn.close()

@app.route('/')
def dashboard():
    # Insert random data into the database on each access
    insert_random_data()

    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')

    print("Start Time:", start_time)
    print("End Time:", end_time)

    utc = pytz.UTC
    conn = get_db_connection()
    cur = conn.cursor()

    device_ids, temperatures, humidities, timestamps = [], [], [], []

    try:
        if start_time and end_time:
            # Convert to datetime objects
            start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M')
            end_time = datetime.strptime(end_time, '%Y-%m-%dT%H:%M')
            # Convert to UTC
            start_time = utc.localize(start_time)
            end_time = utc.localize(end_time)

            print("Querying with:", start_time, end_time)

            query = """
                SELECT device_id, temperature, humidity, timestamp 
                FROM iot_data 
                WHERE timestamp BETWEEN %s AND %s
                ORDER BY timestamp DESC
            """
            cur.execute(query, (start_time, end_time))
            data = cur.fetchall()
            print("Data fetched with parameters:", (start_time, end_time), "Data:", data)
        else:
            cur.execute("SELECT device_id, temperature, humidity, timestamp FROM iot_data ORDER BY timestamp DESC LIMIT 30")
            data = cur.fetchall()
            print("Fallback data fetched:", data)

        if not data:
            return jsonify({"message": "No data found"}), 404

        device_ids = [row[0] for row in data]
        temperatures = [row[1] for row in data]
        humidities = [row[2] for row in data]
        # Format timestamps to desired format
        timestamps = [row[3].strftime('%Y-%m-%d %H:%M:%S') for row in data]

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()

    return render_template('dashboard.html', data=data, data_count=len(data), device_ids=device_ids, temperatures=temperatures, humidities=humidities, timestamps=timestamps)

if __name__ == '__main__':
    app.run(debug=True)
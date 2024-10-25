from flask import Flask, jsonify, render_template, request
import psycopg2
from datetime import datetime
import pytz  # Make sure pytz is installed

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
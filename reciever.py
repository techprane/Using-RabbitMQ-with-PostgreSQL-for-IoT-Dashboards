import pika
import json
import psycopg2

# Establish RabbitMQ connection
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Declare queue
channel.queue_declare(queue='iot_queue')

# PostgreSQL connection
conn = psycopg2.connect(database="iot_db", user="saintvandora", password="1234567890", host="localhost", port="5432")
cur = conn.cursor()

# Callback function to process messages
def callback(ch, method, properties, body):
   data = json.loads(body)
   print(" [x] Received ", data)

   # Insert the sensor data into PostgreSQL
   cur.execute("""
       INSERT INTO iot_data (device_id, temperature, humidity, timestamp)
       VALUES (%s, %s, %s, %s)
   """, (data['device_id'], data['temperature'], data['humidity'], data['timestamp']))
   conn.commit()

channel.basic_consume(queue='iot_queue', on_message_callback=callback, auto_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()



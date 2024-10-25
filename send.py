import pika
import json

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Declare a queue
channel.queue_declare(queue='iot_queue')

# Sample IoT sensor data
sensor_data = {
   'device_id': 'sensor_1',
   'temperature': 22.5,
   'humidity': 60,
   'timestamp': '2024-10-16T10:30:00'
}

# Publish message to the queue
channel.basic_publish(
   exchange='',
   routing_key='iot_queue',
   body=json.dumps(sensor_data)
)
print(" [x] Sent 'IoT data'")

connection.close()





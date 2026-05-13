import redis
import json
import os
import time

redis_host = os.environ.get('REDIS_HOST', 'localhost')
r = redis.Redis(host=redis_host, port=6379)

def process_notification(notification):
    to_user = notification['to_user']
    message = notification['message']

    print(f"Sending {message} to: {to_user}")

while True:
    notification_data = r.brpop('notification_queue', timeout=5)
    if notification_data:
        notif = json.loads(notification_data[1])
        process_notification(notif)
    time.sleep(0.1)

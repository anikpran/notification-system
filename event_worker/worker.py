import redis
import json
import os
import time

redis_host = os.environ.get('REDIS_HOST', 'localhost')
r = redis.Redis(host=redis_host, port=6379)

def process_event(event):
    event_type = event['event_type']
    from_user = event['from_user']
    to_user = event['to_user']
    target = event.get('target', '')

    if event_type == 'like':
        message = f"{from_user} liked your photo"
    elif event_type == 'follow':
        message = f"{from_user} started following you"
    elif event_type == 'comment':
        message = f"{from_user} commented on your post"
    else:
        message = f"{from_user} interacted with your content"

    notification = {
        'to_user' : to_user,
        'message' : message
    }

    r.lpush('notification_queue', json.dumps(notification))
    print(f"Event process: {event_type} from {from_user} to {to_user}")

while True:
    event_data = r.brpop('event_queue', timeout=5)
    if event_data: 
        event = json.loads(event_data[1])
        process_event(event)
    time.sleep(0.1)
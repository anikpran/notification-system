from flask import Flask, request, jsonify
import redis
import json
import os
from datetime import datetime

app = Flask(__name__)

redis_host = os.environ.get('REDIS_HOST', 'localhost')
cache = redis.Redis(host=redis_host, port=6379)

@app.route('/event', methods=['POST'])
def create_event():
    data = request.json

    event = {
        'event_type' : data['event_type'],
        'from_user' : data['from_user'],
        'to_user' : data['to_user'],
        'target' : data.get('target', ''),
        'timestamp' : datetime.utcnow().isoformat()
    }

    cache.lpush('event_queue', json.dumps(event))

    return jsonify({'status': 'event queued', 'event': event})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
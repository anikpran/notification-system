## What it is
A distributed notification system that receives user interaction events via a REST API 
and processes them asynchronously through a two-stage pipeline. Incoming events are 
serialized and pushed onto an event queue, where an event worker consumes and translates 
them into human-readable notification messages. Those notifications are then pushed onto 
a notification queue, where a notification worker consumes and delivers them to the 
intended recipient — simulating real-world push notification, email, or SMS delivery.

## Architecture overview
The system is built around five components running as isolated Docker containers 
coordinated through Docker Compose:

- **Flask API** — the entry point for the system. Receives incoming events from users 
  via POST /event, builds an event object, and pushes it onto the event queue in Redis. 
  Returns immediately without waiting for the notification to be delivered.
- **Redis** — acts as the message broker, maintaining two queues: event_queue and 
  notification_queue. All containers connect to Redis internally using the service 
  name redis:6379 through Docker's internal network.
- **Event Worker** — continuously consumes from the event queue, translates raw events 
  into human readable notification messages, and pushes them onto the notification queue.
- **Notification Worker** — continuously consumes from the notification queue and 
  delivers notifications to the intended recipient.
- **Docker** — runs each component as an isolated container on a shared internal network. 
  Port 5001 is the only externally exposed port, allowing users to send requests to the API.

Request flow: User → API → event_queue → Event Worker → notification_queue → Notification Worker

## Key decisions
- **Asynchronous processing** — the API responds immediately and processing happens in 
  the background via queues, keeping response times fast regardless of downstream load.
- **Separation of concerns via Docker** — each component runs in its own container with 
  one responsibility, making the system easier to scale and modify independently.
- **Redis over RabbitMQ or Kafka** — chose Redis for simplicity since it was already 
  part of the stack. The tradeoff is Redis lacks built-in acknowledgements and message 
  replay that production systems need. At scale you'd migrate to RabbitMQ or Kafka.

## How to run it

**Prerequisites:**
- Docker Desktop

**1. Clone the repository:**
    git clone https://github.com/anikpran/notification-system.git
    cd notification-system

**2. Start all containers:**
    docker compose up --build

**3. Send a test event:**
    curl -X POST http://127.0.0.1:5001/event \
      -H "Content-Type: application/json" \
      -d '{"event_type": "like", "from_user": "user123", "to_user": "user456"}'

Supported event types: like, follow, comment

**4. Stop the system:**
    docker compose down

## What I'd do differently at scale
- **Worker scaling** — a single event worker and notification worker would get 
  overwhelmed at high volume. I'd spin up multiple worker instances behind a load 
  balancer to distribute processing load.
- **Production grade message broker** — Redis queues would get overloaded at scale. 
  I'd migrate to RabbitMQ or Kafka which are built for high throughput and provide 
  features like message acknowledgements, dead letter queues, and message replay.
- **Redis redundancy** — Redis running in a single container is a single point of 
  failure. If it goes down the entire system stops. I'd use a managed service like 
  AWS ElastiCache which handles redundancy and automatic failover.
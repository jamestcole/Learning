from flask import Flask, Response
from prometheus_client import generate_latest, Counter, CONTENT_TYPE_LATEST

app = Flask(__name__)

# Define a Prometheus Counter metric
REQUEST_COUNT = Counter('flask_app_requests_total', 'Total number of requests received')

@app.route('/')
def home():
    REQUEST_COUNT.inc()  # Increment the counter
    return "Hello, Docker!"

@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

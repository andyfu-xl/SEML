from prometheus_client import start_http_server, Summary, Counter, Gauge

import random

import time



# Create a metric to track time spent and requests made.

REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')

# Messages metrics
message_metrics = {
    "messages_received": Counter('messages_received', 'Number of messages received'),
    "null_messages": Counter('null_messages', 'Number of null messages received'),
    "invalid_messages": Counter('invalid_messages', 'Number of invalid messages received'),
    "num_blood_test_results": Counter('blood_test_messages', 'Number of blood test results received')
}

# Connection metrics
communicator_metrics = {
    "connection_attempts": Counter('connection_attempts', 'Number of connection attempts'),
    "connection_failures": Counter('connection_failures', 'Number of connection failures'),
    "page_failures": Counter('page_failures', 'Number of page failures')
}

# Prediction metrics
prediction_metrics = {
    "sum_blood_test_results": Counter('sum_blood_test_results', 'Sum of blood test results'),
    "running_mean_blood_test_results": Gauge('running_mean_blood_test_results', 'Running mean of blood test results'),
    "positive_predictions": Counter('positive_predictions', 'Number of positive predictions'),
    "positive_prediction_rate": Gauge('positive_prediction_rate', 'Positive prediction rate')
}

def start_monitoring():
    server, t = start_http_server(8000)
    return server, t

# Decorate function with metric.

@REQUEST_TIME.time()

def process_request(t):

    """A dummy function that takes some time."""

    time.sleep(t)

if __name__ == '__main__':

    # Start up the server to expose the metrics.

    start_http_server(8000)

    # Generate some requests.

    while True:
        process_request(random.random())
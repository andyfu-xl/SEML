from prometheus_client import start_http_server, Summary, Counter, Gauge

import random
import time



# Create a metric to track time spent and requests made.

REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')

# Main Server metrics
server_metrics = {
    "num_of_startup": Counter('num_of_startup', 'Number of server startups'),
    "num_of_shutdown": Counter('num_of_shutdown', 'Number of server shutdowns'),
}

def increase_num_of_startup():
    server_metrics['num_of_startup'].inc()
    return True

def increase_num_of_shutdown():
    server_metrics['num_of_shutdown'].inc()
    return True

# Messages metrics
message_metrics = {
    "messages_received": Counter('messages_received', 'Number of messages received'),
    "null_messages": Counter('null_messages', 'Number of null messages received'),
    "invalid_messages": Counter('invalid_messages', 'Number of invalid messages received'),
    "num_blood_test_results": Counter('blood_test_messages', 'Number of blood test results received')
}

def increase_message_received():
    message_metrics['messages_received'].inc()
    return True

def increase_null_messages():
    message_metrics['null_messages'].inc()
    return True

def increase_invalid_messages():
    message_metrics['invalid_messages'].inc()
    return True

def increase_blood_test_messages():
    message_metrics['num_blood_test_results'].inc()
    return True

# Connection metrics
communicator_metrics = {
    "connection_attempts": Counter('connection_attempts', 'Number of connection attempts'),
    "connection_failures": Counter('connection_failures', 'Number of connection failures'),
    "page_failures": Counter('page_failures', 'Number of page failures')
}

def increase_connection_attempts():
    communicator_metrics['connection_attempts'].inc()
    return True

def increase_connection_failures():
    communicator_metrics['connection_failures'].inc()
    return True

def increase_page_failures():
    communicator_metrics['page_failures'].inc()
    return True

# Prediction metrics
prediction_metrics = {
    "sum_blood_test_results": Counter('sum_blood_test_results', 'Sum of blood test results'),
    "running_mean_blood_test_results": Gauge('running_mean_blood_test_results', 'Running mean of blood test results'),
    "positive_predictions": Counter('positive_predictions', 'Number of positive predictions'),
    "positive_prediction_rate": Gauge('positive_prediction_rate', 'Positive prediction rate')
}

def increase_sum_blood_test_results(value):
    prediction_metrics['sum_blood_test_results'].inc(value)
    return True

def update_running_mean_blood_test_results():
    prediction_metrics['running_mean_blood_test_results'].set(
            prediction_metrics['sum_blood_test_results']._value.get() 
            / message_metrics['num_blood_test_results']._value.get())
    return True

def increase_positive_predictions():
    prediction_metrics['positive_predictions'].inc()
    return True

def update_positive_prediction_rate():
    prediction_metrics['positive_prediction_rate'].set(
            prediction_metrics['positive_predictions']._value.get() 
            / message_metrics['num_blood_test_results']._value.get())
    return True

database_metrics = {
    "DATABASE_file_path_connection_attempts": Counter('file_path_connection_attempts', 'Number of database connection attempts'),
    "DATABASE_ERROR_file_path_connection_failures": Counter('file_path_connection_failures', 'Number of database connection failures'),
    "DATABASE_ERROR_dates_not_in_order": Counter('dates_not_in_order', 'Number of dates not in order'),
    "DATABASE_ERROR_missing_mrn": Counter('missing_mrn', 'Number of missing mrn'),
    "DATABASE_ERROR_invalid_test_results_length": Counter('invalid_test_results_length', 'Number of invalid test results length'),
    "DATABASE_ERROR_multiple_patients_same_mrn": Counter('multiple_patients_same_mrn', 'Number of multiple patients with same mrn'),
    "DATABASE_ERROR_page_nonexistent_patient": Counter('page_non_existent_patient', 'Number of paging for non_existent patient'),
}

def increase_DATABASE_file_path_connection_attempts():
    database_metrics['DATABASE_file_path_connection_attempts'].inc()
    return True

def increase_DATABASE_ERROR_file_path_connection_failures():
    database_metrics['DATABASE_ERROR_file_path_connection_failures'].inc()
    return True

def increase_DATABASE_ERROR_dates_not_in_order():
    database_metrics['DATABASE_ERROR_dates_not_in_order'].inc()
    return True

def increase_DATABASE_ERROR_missing_mrn():
    database_metrics['DATABASE_ERROR_missing_mrn'].inc()
    return True

def increase_DATABASE_ERROR_invalid_test_results_length():
    database_metrics['DATABASE_ERROR_invalid_test_results_length'].inc()
    return True

def increase_DATABASE_ERROR_multiple_patients_same_mrn():
    database_metrics['DATABASE_ERROR_multiple_patients_same_mrn'].inc()
    return True

def increase_DATABASE_ERROR_page_nonexistent_patient():
    database_metrics['DATABASE_ERROR_page_non-existent_patient'].inc()
    return True

### Preprocessor metrics
preprocessor_metrics = {
    "num_of_preprocess_failures": Counter('num_of_preprocess_failures', 'Number of preprocess failures'),
}

def increase_num_of_preprocess_failures():
    preprocessor_metrics['num_of_preprocess_failures'].inc()
    return True


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
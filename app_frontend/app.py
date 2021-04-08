import requests
import logging
import sys
from flask import Flask, jsonify, request
from py_zipkin.zipkin import zipkin_span, create_http_headers_for_new_span, ZipkinAttrs, Kind, zipkin_client_span
from py_zipkin.request_helpers import create_http_headers
from py_zipkin.encoding import Encoding

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] - %(name)s %(threadName)s : %(message)s'
)

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

def default_handler(encoded_span):
    body = encoded_span
    app.logger.info("body %s", body)
    return requests.post(
        "http://zipkin:9411/api/v2/spans",
        data=body,
        headers={'Content-Type': 'application/json'},
    )

@app.before_request
def log_request_info():
    app.logger.info('Headers: %s', request.headers)
    app.logger.info('Body: %s', request.get_data())

@zipkin_client_span(service_name='app-frontend', span_name='call_backend')
def call_backend():
    headers = create_http_headers()
    inventory = requests.get('http://app-backend:5000/api/v1/list', headers=headers).json()
    return jsonify(inventory)

@app.route('/')
def index():
    with zipkin_span(
        service_name='app-frontend',
        span_name='index_app-frontend',
        transport_handler=default_handler,
        port=5000,
        sample_rate=100,
        encoding=Encoding.V2_JSON
    ):
        response = call_backend()
    return response, 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)

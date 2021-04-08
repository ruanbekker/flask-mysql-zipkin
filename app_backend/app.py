from flask import Flask, jsonify, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields, ValidationError, pre_load
from os import environ

import requests
from py_zipkin.zipkin import zipkin_span, create_http_headers_for_new_span, ZipkinAttrs, Kind, zipkin_client_span
from py_zipkin.encoding import Encoding

MYSQL_USER     = environ['MYSQL_USER']
MYSQL_PASSWORD = environ['MYSQL_PASSWORD']
MYSQL_HOST     = environ['MYSQL_HOST']
MYSQL_DATABASE = environ['MYSQL_DATABASE']

app = Flask(__name__)

app.config['JSON_SORT_KEYS'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{user}:{passwd}@{host}/{db}'.format(
    user=MYSQL_USER,
    passwd=MYSQL_PASSWORD,
    host=MYSQL_HOST,
    db=MYSQL_DATABASE
)

db = SQLAlchemy(app)

class Inventory(db.Model):
    __tablename__ = 'inventory'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    category = db.Column(db.String(1000))

class InventorySchema(Schema):
    class Meta:
        fields = ('id', 'name', 'category')
        ordered = True

    id = fields.Int(dump_only=True)
    name = fields.Str()
    category = fields.Str()

def default_handler(encoded_span):
    body = encoded_span
    return requests.post(
        "http://zipkin:9411/api/v2/spans",
        data=body,
        headers={'Content-Type': 'application/json'},
    )

@app.before_request
def log_request_info():
    app.logger.debug('Headers: %s', request.headers)
    app.logger.debug('Body: %s', request.get_data())

@zipkin_client_span(service_name='app-backend', span_name='dbcall_app_backend')
def dbcall():
    inventory_schema = InventorySchema(many=True)
    all_inventory = Inventory.query.all()
    result = inventory_schema.dump(all_inventory)
    return {"inventory": result}

@app.route('/api/v1/list')
def index():
    with zipkin_span(
        service_name='app-backend',
        zipkin_attrs=ZipkinAttrs(
            trace_id=request.headers['X-B3-TraceID'],
            span_id=request.headers['X-B3-SpanID'],
            parent_span_id=request.headers['X-B3-ParentSpanID'],
            flags=request.headers['X-B3-Flags'],
            is_sampled=request.headers['X-B3-Sampled'],
        ),
        span_name='index_app-backend',
        transport_handler=default_handler,
        port=5000,
        sample_rate=100,
        encoding=Encoding.V2_JSON
    ):
        response = dbcall()
    return response, 200

if __name__ == '__main__':
    db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=False)

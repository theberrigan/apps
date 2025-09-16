import os, json, time

from uuid import uuid4
from flask import Flask, jsonify, request, Response
from flask_cors import CORS


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
HOST = 'localhost'
PORT = 16050
HOSTNAME = 'http://{}:{}'.format(HOST, PORT)


class Coverage:
    def __init__ (self):
        self.data = []

    def get (self):
        return self.data

    def set (self, data):
        self.data = data


def createApp ():
    app = Flask(__name__, static_url_path='', static_folder='./static')
    CORS(app)

    coverage = Coverage()

    # Ping back test endpoint
    # https://tnp-console-dev-server.eu.ngrok.io/ping/some_value 
    @app.route('/ping/<value>', methods=[ 'GET' ])
    def test (value):
        return jsonify({ 'value': value }) #-

    @app.route('/console/coverage', methods=[ 'GET' ])
    def getCoverage ():
        return jsonify(coverage.get())

    @app.route('/console/coverage', methods=[ 'POST' ])
    def setCoverage ():
        data = request.get_json(force=True, silent=True)

        if data == None:
            return jsonify({ 'status': 'ERROR' })

        coverage.set(data)

        return jsonify({ 'status': 'OK' })

    return app


if __name__ == '__main__':
    createApp().run(debug=True, host='localhost', port=PORT)


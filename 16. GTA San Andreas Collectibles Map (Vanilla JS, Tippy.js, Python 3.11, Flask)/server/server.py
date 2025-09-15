from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from consts import STATIC_DIR, MAP_DATA_PATH, HOST, PORT, LOCAL_HOSTNAME
from utils import copyFile, readJson, parseJson, writeJson, removeFile



print(f'\n{ LOCAL_HOSTNAME }\n')

app = Flask(__name__, static_url_path='', static_folder=STATIC_DIR)
CORS(app)


@app.route('/', methods=[ 'GET' ])
def indexHTML ():
    return send_from_directory(STATIC_DIR, 'index.html')


@app.route('/map-data', methods=[ 'GET' ])
def getMapData ():
    mapData = readJson(MAP_DATA_PATH)

    return jsonify({
        'isOk': True,
        'data': mapData
    })


@app.route('/map-data', methods=[ 'POST' ])
def setMapData ():
    backupPath = MAP_DATA_PATH + '.bkp'

    removeFile(backupPath)

    copyFile(MAP_DATA_PATH, backupPath)

    mapData = parseJson(request.data)

    writeJson(MAP_DATA_PATH, mapData)

    return jsonify({
        'isOk': True
    })



if __name__ == '__main__':
    app.run(debug=True, host=HOST, port=PORT)


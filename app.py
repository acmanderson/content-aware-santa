import os
import traceback
from base64 import b64encode

from flask import Flask, request, jsonify
from request_schema import validate, SchemaError

app = Flask(__name__)
# debug state can depend on Flask's debug or the STAGE environment variable Zappa sets in Lambda
app.config['IN_DEBUG'] = lambda: app.debug or os.getenv('STAGE') == 'dev'


@app.errorhandler(SchemaError)
def handle_schema_error(error):
    response = jsonify({'message': str(error).split()[-1], 'error': True})
    response.status_code = 400
    return response


@app.errorhandler(Exception)
def handle_exception(_):
    if app.config['IN_DEBUG']():
        message = traceback.format_exc()
    else:
        message = 'An error occurred.'
    response = jsonify({'message': message, 'error': True})
    response.status_code = 500
    return response


@app.route('/', methods=['POST'])
def index():
    body = validate(request.get_json())
    image = body['image']
    rescale_width = body['rescale_width']
    rescale_height = body['rescale_height']
    start_width = body.get('start_width', rescale_width)
    start_height = body.get('start_height', rescale_height)

    with image as rescaled:
        rescaled.content_aware_scale(rescale_width, rescale_height, start_width, start_height,
                                     use_slow_scaling='USE_SLOW_SCALING' in os.environ)
        return jsonify({'image': b64encode(rescaled.make_blob()).decode('utf-8')})


if __name__ == '__main__':
    app.run(debug=True)

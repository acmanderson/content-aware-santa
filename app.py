import os
from base64 import b64encode, b64decode

from flask import Flask, request, jsonify
from schema import Schema, And, Use, Optional, SchemaError

from content_aware_image import ContentAwareImage

app = Flask(__name__)

RESCALE_DEFAULT = 50
RESCALE_SCHEMA = And(Use(int), lambda n: 1 <= n <= 100)


def debug():
    return app.debug or os.getenv('STAGE') == 'dev'


def base64_to_image(b64):
    try:
        decoded = b64decode(b64)
        return ContentAwareImage(blob=decoded)
    except Exception as e:
        if debug():
            raise e
        else:
            # raise generic error that is appropriate to return to a user
            raise SchemaError("Could not decode image.")


schema = Schema({
    'image': Use(base64_to_image),
    Optional('rescale_width', default=RESCALE_DEFAULT): RESCALE_SCHEMA,
    Optional('rescale_height', default=RESCALE_DEFAULT): RESCALE_SCHEMA,
    Optional('start_width'): RESCALE_SCHEMA,
    Optional('start_height'): RESCALE_SCHEMA,
})


@app.errorhandler(SchemaError)
def handle_schema_error(error):
    response = jsonify({'message': error.message, 'error': True})
    response.status_code = 400
    return response


@app.errorhandler(Exception)
def handle_exception(error):
    if debug():
        message = error.message
    else:
        message = 'An error occurred.'
    response = jsonify({'message': message, 'error': True})
    response.status_code = 500
    return response


@app.route('/', methods=['POST'])
def index():
    body = schema.validate(request.get_json())
    image = body['image']
    rescale_width = body['rescale_width']
    rescale_height = body['rescale_height']
    start_width = body.get('start_width', rescale_width)
    start_height = body.get('start_height', rescale_height)

    with image as rescaled:
        rescaled.content_aware_scale(rescale_width, rescale_height, start_width, start_height)

        return jsonify({'image': b64encode(rescaled.make_blob())})


if __name__ == '__main__':
    app.run(debug=True)

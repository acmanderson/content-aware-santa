from base64 import b64decode

import requests
from schema import Schema, And, Use, Or, Optional, SchemaError
from flask import current_app as app

from content_aware_image import ContentAwareImage

RESCALE_DEFAULT = 50
RESCALE_SCHEMA = And(Use(int), lambda n: n > 0)
BASE_SCHEMA = {
    Optional('rescale_width', default=RESCALE_DEFAULT): RESCALE_SCHEMA,
    Optional('rescale_height', default=RESCALE_DEFAULT): RESCALE_SCHEMA,
    Optional('start_width'): RESCALE_SCHEMA,
    Optional('start_height'): RESCALE_SCHEMA,
}


def decode_image(decode_function):
    """
    Wrapper function to generate a decode function with boilerplate code to handle errors and
    instantiation of the Wand image type.
    :param decode_function:
    :return:
    """
    def _decode(data):
        try:
            decoded = decode_function(data)
            return ContentAwareImage(blob=decoded)
        except Exception as e:
            if app.config['IN_DEBUG']() or isinstance(e, SchemaError):
                raise e
            else:
                # raise generic error that is appropriate to return to a user
                raise SchemaError('Could not decode image.')

    return _decode


def url_to_image(url):
    res = requests.get(url)
    if res.status_code != 200:
        raise SchemaError('Could not fetch image.')

    return res.content


image_decoders = {
    'image_base64': b64decode,
    'image_url': url_to_image,
}


def validate(body):
    """
    Validate request body and put image in `image` key so `app.py` doesn't need to resolve which key to use.
    :param body:
    :return:
    """
    # build schema as an Or between BASE_SCHEMA + the image decoders
    schema = Schema(Or(
        *(dict(BASE_SCHEMA, **{name: Use(decode_image(function))}) for name, function in image_decoders.items())
    ))
    body = schema.validate(body)
    image = None
    for decoder in image_decoders.keys():
        image = body.pop(decoder, None)
        if image is not None:
            break
    body['image'] = image
    return body

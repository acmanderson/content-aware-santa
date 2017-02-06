import base64
import os
import subprocess

from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/', methods=['POST'])
def index():
    # need to update the LD_LIBRARY_PATH environment variable so ImageMagick will find its dependencies in the
    # build dir
    ld_library_path = os.getenv('LD_LIBRARY_PATH')
    dependencies_dir = [os.path.join(os.getcwd(), 'build', 'lib')]
    if dependencies_dir[0] not in ld_library_path:
        if ld_library_path:
            dependencies_dir.append(ld_library_path)
        os.environ['LD_LIBRARY_PATH'] = ':'.join(dependencies_dir)

    body = request.get_json()
    image_b64 = body['image_b64']
    rescale_x = body.get('rescale_x', 50)
    rescale_y = body.get('rescale_y', 50)

    rescaled = rescale_image(base64.b64decode(image_b64), rescale_x, rescale_y)

    return jsonify({'image_b64': base64.b64encode(rescaled)})


def generate_command(method, rescale_x, rescale_y):
    return [
        'build/bin/convert',
        '-',
        '-{}'.format(method),
        '{}x{}%'.format(rescale_x, rescale_y),
        '-',
    ]


def rescale_command(image, method, rescale_x, rescale_y):
    command = generate_command(method, rescale_x, rescale_y)
    p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    rescaled, err = p.communicate(input=image)
    if err:
        pass

    return rescaled


def rescale_image(image, rescale_x, rescale_y):
    liquid_rescale = rescale_command(image, 'liquid-rescale', rescale_x, rescale_y)

    upscale_x = 100.0 / rescale_x * 100
    upscale_y = 100.0 / rescale_y * 100
    original_size = rescale_command(liquid_rescale, 'resize', upscale_x, upscale_y)

    return original_size


if __name__ == '__main__':
    app.run()

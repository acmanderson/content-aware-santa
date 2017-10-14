# content-aware-santa
AWS API Gateway/Lambda Flask service for liquid-rescaling images using ImageMagick inspired by http://contentawaresatan.com/

## Examples
![before](https://i.imgur.com/NyuJLXs.gif) -> ![after](https://i.imgur.com/zmgMAeq.gif)

## Requirements
* [ImageMagick](https://www.imagemagick.org/script/index.php) built with [liblqr](http://liblqr.wikidot.com/) support.

## Usage
After installing dependencies, the service can be run locally with `python app.py`. This starts an HTTP server, and you can begin making requests. Requests are `POST`s to the root of the service, e.g. `http://localhost:8080/`, and are JSON blobs with the following fields:

One of:
* `image_base64` (string) - base64 string of the image to be rescaled
* `image_url` (string) - URL of the image to be rescaled

Any of:
* `rescale_width` (positive int) - optional final width percentage (relative to original width) for the image, default 50%
* `rescale_height` (positive int) - optional final height percentage (relative to original height) for the image, default 50%
* `start_width` (positive int) - valid only for animated GIFs, optional starting width percentage (relative to original width) for the image, default 100%
* `start_height` (positive int) - valid only for animated GIFs, optional starting height percentage (relative to original height) for the image, default 100%

An example request might look like:
```json
{
  "image_url": "https://i.imgur.com/NyuJLXs.gif",
  "rescale_width": 75,
  "rescale_width": 75,
  "start_width": 20,
  "start_height": 20
}
```

## Deploying to AWS
The service can also be deployed to AWS as an API Gateway/Lambda service via [Zappa](https://github.com/Miserlou/Zappa). The Dockerfile in this repo will download and compile ImageMagick with liblqr support for use with Lambda. Copy the contents of `/var/task/build` in the Docker container into your local clone of this repo before using Zappa to deploy.

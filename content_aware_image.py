import numbers
from concurrent.futures import ThreadPoolExecutor

from wand import exceptions
from wand.api import library
from wand.image import Image


class ContentAwareImage(Image):
    def __init__(self, *args, **kwargs):
        super(ContentAwareImage, self).__init__(*args, **kwargs)
        if self.animation:
            # MagickWand doesn't seem to get the proper size for gifs with
            # variable frame sizes, so find the max width and height and use those
            frame_sizes_x, frame_sizes_y = zip(*[frame.size for frame in self.sequence])
            self.original_size = max(frame_sizes_x), max(frame_sizes_y)
        else:
            self.original_size = self.size

    def clone(self):
        return ContentAwareImage(image=self)

    def content_aware_scale(self, width, height, start_width, start_height, units_percent=True, use_slow_scaling=False,
                            delta_x=1, rigidity=0):
        if not isinstance(width, numbers.Integral):
            raise TypeError('width must be an integer, not ' + repr(width))
        elif not isinstance(height, numbers.Integral):
            raise TypeError('height must be an integer, not ' + repr(height))
        elif not isinstance(start_width, numbers.Integral):
            raise TypeError('start_width must be an integer, not ' + repr(height))
        elif not isinstance(start_height, numbers.Integral):
            raise TypeError('start_height must be an integer, not ' + repr(height))
        elif not isinstance(delta_x, numbers.Real):
            raise TypeError('delta_x must be a float, not ' + repr(delta_x))
        elif not isinstance(rigidity, numbers.Real):
            raise TypeError('rigidity must be a float, not ' + repr(rigidity))

        if self.animation:
            # scale each frame in the image, linearly scaling the rescale amount per frame
            # if start_width/height != rescale_width/height

            # coalesce outputs each frame as the viewer sees it instead of in its optimized form, as rescaling a
            # non-coalesced image results in artifacts on the optimized frames
            self.wand = library.MagickCoalesceImages(self.wand)

            num_frames = len(self.sequence)
            rescale_width_step = float(start_width - width) / num_frames
            rescale_height_step = float(start_height - height) / num_frames

            def _rescale_frame(index):
                rescale_width = int(start_width - rescale_width_step * index)
                rescale_height = int(start_height - rescale_height_step * index)

                rescaled_frame = ContentAwareImage(image=self.sequence[index])
                rescaled_frame.content_aware_scale(rescale_width, rescale_height, start_width, start_height,
                                                   units_percent=units_percent, use_slow_scaling=use_slow_scaling,
                                                   delta_x=delta_x, rigidity=rigidity)
                return rescaled_frame

            # process gifs concurrently for maximum speed
            with ThreadPoolExecutor(max_workers=None) as executor:
                sequence = list(executor.map(_rescale_frame, range(num_frames)))
            # replace the old frames in the sequence with the new ones
            self.sequence.extend(sequence)
            del self.sequence[:int(len(self.sequence) / 2)]
            # free the generated frames from memory
            for frame in sequence:
                frame.close()
        else:
            # scale an individual frame or non-animated image
            original_width, original_height = self.original_size
            if units_percent:
                width = int(original_width * float(width) / 100)
                height = int(original_height * float(height) / 100)
                start_width = int(original_width * float(start_width) / 100)
                start_height = int(original_height * float(start_height) / 100)

            if not use_slow_scaling:
                library.MagickLiquidRescaleImage(self.wand, width, height, float(delta_x), float(rigidity))
                library.MagickSampleImage(self.wand, original_width, original_height)
            else:
                # upscaling the image before downscaling it with liquid rescale can produce different/better results,
                # but is a lot slower
                library.MagickSampleImage(self.wand,
                                          int(float(original_width) / width * original_width),
                                          int(float(original_height) / height * original_height))
                library.MagickLiquidRescaleImage(self.wand, original_width, original_height, float(delta_x),
                                                 float(rigidity))
                library.MagickSetSize(self.wand, original_width, original_height)

        try:
            self.raise_exception()
        except exceptions.MissingDelegateError as e:
            raise exceptions.MissingDelegateError(
                str(e) + '\n\nImageMagick in the system is likely to be '
                         'impossible to load liblqr.  You might not install liblqr, '
                         'or ImageMagick may not compiled with liblqr.'
            )

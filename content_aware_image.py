import numbers

from wand import exceptions
from wand.api import library
from wand.image import Image


class ContentAwareImage(Image):
    def __init__(self, *args, **kwargs):
        super(ContentAwareImage, self).__init__(*args, **kwargs)
        self.original_size = self.size

    def clone(self):
        return ContentAwareImage(image=self)

    def content_aware_scale(self, width, height, start_width, start_height, units_percent=True, delta_x=1, rigidity=0):
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

        original_width, original_height = self.original_size
        if units_percent:
            width = int(original_width * float(width) / 100)
            height = int(original_height * float(height) / 100)
            start_width = int(original_width * float(start_width) / 100)
            start_height = int(original_height * float(start_height) / 100)

        if self.animation:
            self.wand = library.MagickCoalesceImages(self.wand)
            library.MagickSetLastIterator(self.wand)
            n = library.MagickGetIteratorIndex(self.wand)
            library.MagickResetIterator(self.wand)

            num_frames = len(self.sequence)
            rescale_width_step = float(start_width - width) / num_frames
            rescale_height_step = float(start_height - height) / num_frames
            for i in xrange(n + 1):
                rescale_width = int(start_width - rescale_width_step * i)
                rescale_height = int(start_height - rescale_height_step * i)
                library.MagickSetIteratorIndex(self.wand, i)
                # sampling up before doing the liquid rescale results in better image quality but is much slower
                # than doing it this way
                library.MagickLiquidRescaleImage(self.wand, rescale_width, rescale_height, float(delta_x),
                                                 float(rigidity))
                library.MagickSampleImage(self.wand, original_width, original_height)
        else:
            library.MagickLiquidRescaleImage(self.wand, width, height, float(delta_x), float(rigidity))
            library.MagickSampleImage(self.wand, original_width, original_height)
        library.MagickSetSize(self.wand, original_width, original_height)

        try:
            self.raise_exception()
        except exceptions.MissingDelegateError as e:
            raise exceptions.MissingDelegateError(
                str(e) + '\n\nImageMagick in the system is likely to be '
                         'impossible to load liblqr.  You might not install liblqr, '
                         'or ImageMagick may not compiled with liblqr.'
            )

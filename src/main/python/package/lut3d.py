## THIS FILE AS BEEN WRTITTEN BY Arseny Kravchenko
# https://gist.github.com/arsenyinfo/74e42b41749cf29a7bbb69ed839bff1a

from functools import partial

import numpy as np
from tqdm import tqdm

LUT_SIZE = 33


def _convert(pixel, lut):
    r, g, b = map(lambda x: round((x / 255) * LUT_SIZE - 1), pixel)
    idx = r + g * LUT_SIZE + b * (LUT_SIZE ** 2)
    result = lut[int(idx)]
    r_, g_, b_ = map(lambda i: np.float(result[i]), range(3))
    return np.array([r_, g_, b_])


def read_lut_file(path):
    with open(path) as fd:
        lines = [x.rstrip() for x in fd.readlines()]
    lut = list(map(lambda x: x.split(' '), lines[-LUT_SIZE ** 3:]))
    return lut


def convert_with_lut(img, lut_path):
    lut = read_lut_file(lut_path)

    pixels = img.reshape(-1, 3)
    convert = partial(_convert, lut=lut)
    new_pixels = list(map(convert, tqdm(pixels)))
    new_img = np.array(new_pixels).reshape(img.shape)

    new_img = (new_img * 255).astype('uint8')

    return new_img
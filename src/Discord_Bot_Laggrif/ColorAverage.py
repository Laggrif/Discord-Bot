import cv2
import numpy as np
from skimage import io


def dominant_color(image):
    img = io.imread(image)[:, :, :]

    pixels = np.float32(img.reshape(-1, 3))

    n_colors = 5
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
    flags = cv2.KMEANS_RANDOM_CENTERS

    _, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
    _, counts = np.unique(labels, return_counts=True)

    dominant = palette[np.argmax(counts)]

    return tuple(map(int, dominant.tolist()))


def mix_color(image):
    average = average_color(image)
    dominant = dominant_color(image)

    mix = [int((average[i] + dominant[i]) / 2) for i in range(3)]

    return tuple(mix)


def average_color(image):
    img = io.imread(image)[:, :, :]

    average = img.mean(axis=0).mean(axis=0)

    return tuple(map(int, average.tolist()))

"""Unit conversions."""


import math


π = math.pi

# 1 inch = 0.0254 meters
METERS_PER_INCH = 0.0254

RADIANS_PER_DEGREE = π / 180
RADIANS_PER_REVOLUTION = 2 * π


def celsius_to_kelvin(T):
    # https://en.wikipedia.org/wiki/Kelvin
    return T + 273.15


def fahrenheit_to_celsius(T):
    # https://en.wikipedia.org/wiki/Fahrenheit
    return (5 / 9) * (T - 32)


assert fahrenheit_to_celsius(212) == 100
assert fahrenheit_to_celsius(32) == 0

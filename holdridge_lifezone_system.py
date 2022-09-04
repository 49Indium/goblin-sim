"""
Functions relating to the biomes of the Holdridge lifezone system and its perameters. See https://en.wikipedia.org/wiki/Holdridge_life_zones for more information on the Holdridge lifezone system.
"""
from itertools import combinations
import math

# Compared to typical pictures of the Holdridge lifezone triangle, this will look slighly rotated and skewed, so that the top point of the triangle is in the top-left corner and extended for all values. Rows have same annual precipitation, columns have the same PET (potential evapotranspirational ratio). Based upon Parry, M.L. et al's 1988 The effects on Holdridge Life Zones. In: The Impact of Climatic Variations on Agriculture (pages 473-484).
_HOLDRIDGE_LIFEZONE_TRIANGLE = [
    ["Dry Tundra", "Dry Tundra", "Dry Tundra", "Dry Tundra",
        "Desert", "Desert", "Desert", "Desert"],
    ["Moist Tundra", "Moist Tundra", "Moist Tundra", "Dry Bush",
        "Desert Bush", "Desert Bush", "Desert Bush"],
    ["Wet Tundra", "Wet Tundra", "Moist Forrest",
        "Steppe", "Thorn Steppe", "Thorn Woodland"],
    ["Rain Tundra", "Wet Forrest", "Moist Forrest",
        "Dry Forrest", "Very Dry Forrest"],
    ["Rain Forrest", "Wet Forrest", "Moist Forrest", "Dry Forrest"],
    ["Rain Forrest", "Wet Forrest", "Moist Forrest"],
    ["Rain Forrest", "Wet Forrest"],
    ["Rain Forrest"]
]

# How each parameter is seen within _HOLDRIDGE_LIFEZONE_TRIANGLE
_PARAMETER_LINE_TYPES = {"Humidity": "Diagonal",
                         "Annual Precipitation": "Column",
                         "PET": "Row",
                         "Latitudinal Region": "Antidiagonal",
                         "Altitudinal Belt": "Antidiagonal",
                         "Biotemperature": "Antidiagonal"}

# Humidity provinces and their diagonals on the Holdridge lifezone triangle
_HUMIDITY_PROVINCES = {"Super-Arid": -7,
                       "Perarid": -5,
                       "Arid": -3,
                       "Semi-Arid": -1,
                       "Sub-Humid": 1,
                       "Humid": 3,
                       "Perhumid": 5,
                       "Super-Humid": 7}

# Latitudinal regions and their antidiagonals on the Holdridge lifezone triangle
_LATITUDINAL_REGIONS = {"Polar": 2,
                        "Subpolar": 3,
                        "Boreal": 4,
                        "Temperate": 5,
                        "Subtropical": 6,
                        "Tropical": 7}

# Altitudinal belts and their antidiagonals on the Holdridge lifezone triangle
_ALTITUDINAL_BELTS = {"Nival": 2,
                      "Alpine": 3,
                      "Subalpine": 4,
                      "Montane": 5,
                      "Lower Montane": 6,
                      "Premontane": 7}


class HoldridgeParameter():
    """
    One of the six parameters defining a position on the Holdridge lifezone system (note that only two parameters are needed to get a biome)
    Parameters should be one of the following, with types indicating the expected type of value:
        humdity(string): the humidity province
        annual_precipitation(int): the annual precipitation in mm
        PET(float): the potential evapotranspiration ratio, i.e. the amount of water able to be evaporated and transpired, if such water existed, compared to the annual precipitation amount
        latitudinal_region(string): the latitudinal region
        altitudinal_best(string): the altitudinal belt
        bio_temperature(float): the biotemperature of the region in degrees celcius. Defined by the average of max(min(temperature, 30), 0) over a year.
    """

    def __init__(self, parameter_name, value):
        self.name = parameter_name
        self.value = value
        self.line_type = _PARAMETER_LINE_TYPES[parameter_name]
        if parameter_name == "Humidity":
            self.line_value = _HUMIDITY_PROVINCES[value]
        elif parameter_name == "Annual Precipitation":
            self.line_value = math.log2(value) - math.log2(62.5) if value > 0 else 0
        elif parameter_name == "PET":
            self.line_value = math.log2(value) - math.log2(0.125) if value > 0 else 0
        elif parameter_name == "Latitudinal Region":
            self.line_value = _LATITUDINAL_REGIONS[value]
        elif parameter_name == "Altitudinal Belt":
            self.line_value = _ALTITUDINAL_BELTS[value]
        elif parameter_name == "Biotemperature":
            self.line_value = math.log2(value) - math.log2(0.1875) if value > 0 else 0
        else:
            raise ValueError("Invalid parameter_name for Holdridge parameter")


def _get_holdridge_coordinates(parameter1, parameter2):
    """
    Get the coordinates (x,y) of the respective biome in _HOLDRIDGE_LIFEZONE_TRIANGLE given two lines.
    """
    if parameter1.line_type == parameter2.line_type:
        raise ValueError(
            "A coordinate cannot be derived from the two parameters given")

    if parameter1.line_type == "Row":
        if parameter2.line_type == "Column":
            return (parameter2.line_value, parameter1.line_value)
        elif parameter2.line_type == "Diagonal":
            return (parameter1.line_value + parameter2.line_value, parameter1.line_value)
        elif parameter2.line_type == "Antidiagonal":
            return (parameter2.line_value - parameter1.line_value, parameter1.line_value)
        else:
            raise ValueError("Unknown Holdridge parameter line_type")
    elif parameter1.line_type == "Column":
        if parameter2.line_type == "Diagonal":
            return (parameter1.line_value, parameter1.line_value - parameter2.line_value)
        elif parameter2.line_type == "Antidiagonal":
            return (parameter1.line_value, parameter2.line_value - parameter1.line_value)
        else:
            return _get_holdridge_coordinates(parameter2, parameter1)
    elif parameter1.line_type == "Diagonal":
        if parameter2.line_type == "Antidiagonal":
            return ((parameter1.line_value + parameter2.line_value)/2, (-parameter1.line_value + parameter2.line_value)/2)
        else:
            return _get_holdridge_coordinates(parameter2, parameter1)
    elif parameter1.line_type == "Antidiagonal":
        return _get_holdridge_coordinates(parameter2, parameter1)
    raise ValueError("Unknown Holdridge parameter line_type")


def _move_coordinate_within_triangle(x, y):
    """
    Find the closest coordinate that is within the Holdridge triangle
    """
    x = max(x, 0)
    y = max(y, 0)
    if x + y >= len(_HOLDRIDGE_LIFEZONE_TRIANGLE):
        if -len(_HOLDRIDGE_LIFEZONE_TRIANGLE) <= x - y <= len(_HOLDRIDGE_LIFEZONE_TRIANGLE):
            # Move along diagonal
            x = (x - y + len(_HOLDRIDGE_LIFEZONE_TRIANGLE)-1)/2
            y = (y - x + len(_HOLDRIDGE_LIFEZONE_TRIANGLE)-1)/2
        elif x > y:
            x = len(_HOLDRIDGE_LIFEZONE_TRIANGLE)-1
            y = 0
        else:
            x = 0
            y = len(_HOLDRIDGE_LIFEZONE_TRIANGLE)-1
    return (x, y)


def get_holdridge_biome(parameters):
    """
    Get the biome based upon the Holdridge lifezone system given at least two of the parameters.
    Parameters:
        parameters(list[HoldridgeParameter]): A list of parameters to try to estimate the biome of
    """

    if len(parameters) < 2:
        raise ValueError("At least two parameters must be specified")

    triangle_coordinates = []
    for parameter1, parameter2 in combinations(parameters, 2):
        try:
            triangle_coordinates.append(_move_coordinate_within_triangle(
                *_get_holdridge_coordinates(parameter1, parameter2)))
        except ValueError:
            # Parameter will be of same line
            pass

    if triangle_coordinates == []:
        raise ValueError(
            "Parameters specified were unable to define any coordinates")
    x_total, y_total = 0, 0
    for coordinate in triangle_coordinates:
        x_total += coordinate[0]
        y_total += coordinate[1]
    average_x, average_y = _move_coordinate_within_triangle(x_total/len(triangle_coordinates), y_total/len(triangle_coordinates))
    return _HOLDRIDGE_LIFEZONE_TRIANGLE[math.floor(average_y)][math.floor(average_x)]

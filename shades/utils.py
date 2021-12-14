def color_clamp(color):
    """
    Ensures a three part iterable is a properly formatted color.

    Parameters:
    color (tuple): RGB tuple

    Returns:
    color (tuple): Same color as input, as integers between 0 and 255
    """
    clamped_color = [max(min(int(i), 255), 0) for i in color]
    return tuple(clamped_color)


def distance_between_points(xy1, xy2):
    """
    Returns the euclidean distance between two points.
    https://en.wikipedia.org/wiki/Euclidean_distance

    Parameters:
    xy1 (coordinate): first point
    xy2 (coordiante): second point

    Returns:
    float: euclidean distance betewen the two points
    """
    return (((xy1[0] - xy2[0]) ** 2) + ((xy1[1] - xy2[1]) ** 2)) ** 0.5


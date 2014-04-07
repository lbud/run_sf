from math import atan2, cos, degrees, pi, pow, radians, sin, sqrt, tan

from geopy import distance, Point

import dbs


def find_dist(x1, x2):
    """ Finds distance, in feet, between two node or intersection objects """
    pt1 = Point(x1.lat, x1.lon)
    pt2 = Point(x2.lat, x2.lon)
    dist = distance.distance(pt1, pt2).feet
    return dist


def find_miles(x1, x2):
    """ Finds distance, in miles, between two node or intersection objects """
    pt1 = Point(x1.lat, x1.lon)
    pt2 = Point(x2.lat, x2.lon)
    dist = distance.distance(pt1, pt2).miles
    return dist


def nearest_intersection(loc):
    """ Takes loc as tuple; returns closest intersection object """
    here_string = 'POINT(%r %r)' % (loc[1], loc[0])
    here = dbs.WKTElement(here_string, srid=4326)
    nearest = dbs.session.query(dbs.GIntersection).order_by(
        dbs.func.ST_Distance(dbs.GIntersection.loc, here)
    ).first()
    return nearest


def vert_climb(x1, x2):
    """ Finds vertical climb (feet) between two node or intersection objects
    """
    return x2.elev - x1.elev



# Below functions are currently unused.
# These can be used as an alternative to hackish A* algorithm:
# gen_radii uses radials (which uses vincenty) to generate a circular grid
# of points within a given radius of a location, which can then be checked
# for elevations similar to starting elevation.

def radials(x1, dist, offset=0):
    """ Returns a set of eight intersection objects in cardinal + ordinal
        directions (or offsets)
        Args:)
        x1: node or intersection object
        dist: desired distance in each direction, in miles
        offset (optional): offset angles (22.5 for tertiary directions)
    Returns:
        List of intersection objects closest to geo location in each direction
    """
    # N NE E SE S SW W NW, or offset
    bearings = [b + offset for b in [0, 45, 90, 135, 180, 225, 270, 315]]
    # gets coordinates
    radii = [vincenty(x1, bearing, dist) for bearing in bearings]
    nearest_ints = []
    for r in radii:
        result = nearest_intersection(r)
        nearest_ints.append(result.id)
    radial_points = [
        dbs.session.query(dbs.GIntersection).get(i) for i in nearest_ints
    ]
    return radial_points


def gen_radii(loc, dist):
    valids = []
    for i in [float(r)/2 for r in range(1, dist * 2)]:
        if i % 1 == 0:
            rads = radials(loc, i)
        else:
            rads = radials(loc, i, 22.5)
        valids += rads
    return valids


def vincenty(x1, bearing, dist):
    """ Finds the coordinates of a point a given distance away from another
    Args:
        x1: node or intersection object
        bearing: degrees. 0 corresponds with N, 90 with E, etc
        dist: desired distance, in miles
    Returns:
        Tuple of geographical coordinates (lat, lon)
    Adapted from
        Vincenty Direct Solution of Geodesics on the Ellipsoid (c) Chris Veness
        2005-2012
        http://www.movable-type.co.uk/scripts/latlong-vincenty-direct.html
    """
    a = 6378137
    b = 6356752.3142
    f = 1/298.257223563
    # Vincenty direct uses meters -- this function takes miles as arg; convert
    # here
    s = dist * 1609.34
    lat1 = x1.lat
    lon1 = x1.lon
    alpha1 = radians(bearing)
    sin_alpha1 = sin(alpha1)
    cos_alpha1 = cos(alpha1)

    tan_u1 = (1-f) * tan(radians(lat1))
    cos_u1 = 1 / sqrt((1 + pow(tan_u1, 2)))
    sin_u1 = tan_u1 * cos_u1

    sigma1 = atan2(tan_u1, cos_alpha1)
    sin_alpha = cos_u1 * sin_alpha1
    cos_sq_alpha = 1 - pow(sin_alpha, 2)
    u_sq = cos_sq_alpha * (pow(a, 2) - pow(b, 2)) / pow(b, 2)
    A = 1 + u_sq/16384 * (4096 + u_sq * (-768 + u_sq * (320 - 175*u_sq)))
    B = u_sq/1024 * (256 + u_sq * (-128 + u_sq * (74 - 47*u_sq)))

    sigma = s / (b * A)
    sigma_p = 2 * pi
    while abs(sigma - sigma_p) > pow(10, -12):
        cos2_sigma_m = cos(2 * sigma1 + sigma)
        sin_sigma = sin(sigma)
        cos_sigma = cos(sigma)
        delta_sigma = B * sin_sigma * (
            cos2_sigma_m + B/4 * (-1 + 2*pow(cos2_sigma_m, 2)) - B/6 *
            cos2_sigma_m * (-3 + 4*pow(sin_sigma, 2)) *
            (-3 + 4 * pow(cos2_sigma_m, 2))
        )
        sigma_p = sigma
        sigma = s / (b * A) + delta_sigma

    tmp = sin_u1 * sin_sigma - cos_u1 * cos_sigma * cos_alpha1
    lat2 = atan2(
        (sin_u1 * cos_sigma + cos_u1 * sin_sigma * cos_alpha1),
        (1-f) * sqrt(pow(sin_alpha, 2) + pow(tmp, 2))
    )
    lambd = atan2(
        (sin_sigma * sin_alpha1),
        (cos_u1 * cos_sigma - sin_u1 * sin_sigma * cos_alpha1)
    )
    C = f/16 * cos_sq_alpha * (4 + f * (4 - 3 * cos_sq_alpha))
    L = lambd - (1 - C) * f * sin_alpha * (
        sigma + C * sin_sigma *
        (cos2_sigma_m + C * cos_sigma * (-1 + 2 * pow(cos2_sigma_m, 2)))
    )
    lon2 = (radians(lon1) + L + 3 * pi) % (2*pi) - pi

    return (degrees(lat2), degrees(lon2))

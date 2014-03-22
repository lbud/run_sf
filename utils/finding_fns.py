from geopy import distance, Point
import dbs
from math import atan2, degrees, radians, sin, cos, tan, sqrt, pow, pi
from dbs import mdb, MongoClient, SON

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


def vert_climb(x1,x2):
    """ Finds vertical climb (feet) between two node or intersection objects """
    return x2.elev - x1.elev


def radials(x1, dist, offset = 0):
    """ Returns a set of eight intersection objects in cardinal + ordinal directions (or offsets)
        Args:)
        x1: node or intersection object
        dist: desired distance in each direction, in miles
        offset (optional): offset angles (22.5 for tertiary directions)
    Returns:
        List of intersection objects closest to geo location in each direction
    """
    center = Point(x1.lat, x1.lon)
    bearings = [ b + offset for b in [0, 45, 90, 135, 180, 225, 270, 315] ]  # N NE E SE S SW W NW, or offset
    radii = [ vincenty(x1, bearing, dist) for bearing in bearings ]  # gets coordinates
    nearest_ints = []
    for r in radii:
        res = dbs.mdb.command(SON([('geoNear', 'nodes'), ('near', r), ('limit', 1)]))['results'][0].get('obj')
        resloc = res.get('loc')
        res_id = res.get('node_id')
        nearest_ints.append(res_id)
    radial_points = [ dbs.session.query(dbs.Intersection).get(i) for i in nearest_ints ]
    return radial_points


def gen_radii(loc, dist):
    valids = []
    for i in [ float(r)/2 for r in range(dist * 2) ]:
        if i%1 == 0:        
            rads = radials(loc,i)
        else:
            rads = radials(loc,i,22.5)
        valids += rads
    return rads



def vincenty(x1, bearing, dist):
    """ Finds the coordinates of a point a given distance away from another
    Args:
        x1: node or intersection object
        bearing: degrees. 0 corresponds with N, 90 with E, etc
        dist: desired distance, in miles
    Returns:
        Tuple of geographical coordinates (lat, lon)
    Adapted from 
        Vincenty Direct Solution of Geodesics on the Ellipsoid (c) Chris Veness 2005-2012
        http://www.movable-type.co.uk/scripts/latlong-vincenty-direct.html
    """
    a = 6378137
    b = 6356752.3142
    f = 1/298.257223563
    s = dist * 1609.34  # Vincenty direct uses meters -- this function takes miles as arg; convert here
    lat1 = x1.lat
    lon1 = x1.lon
    alpha1 = radians(bearing)
    sin_alpha1 = sin(alpha1)
    cos_alpha1 = cos(alpha1)

    tan_u1 = (1-f) * tan(radians(lat1))
    cos_u1 = 1 / sqrt((1 + pow(tan_u1,2)))
    sin_u1 = tan_u1 * cos_u1

    sigma1 = atan2(tan_u1, cos_alpha1)
    sin_alpha = cos_u1 * sin_alpha1
    cos_sq_alpha = 1 - pow(sin_alpha, 2)
    u_sq = cos_sq_alpha * (pow(a,2) - pow(b,2)) / pow(b,2)
    A = 1 + u_sq/16384 * (4096 + u_sq * (-768 + u_sq * (320 - 175*u_sq)))
    B = u_sq/1024 * (256 + u_sq * (-128 + u_sq * (74 - 47*u_sq)))

    sigma = s / (b * A)
    sigma_p = 2 * pi
    while abs(sigma - sigma_p) > pow(10,-12):
        cos2_sigma_m = cos(2 * sigma1 + sigma)
        sin_sigma = sin(sigma)
        cos_sigma = cos(sigma)
        delta_sigma = B * sin_sigma * (cos2_sigma_m + B/4 * (-1 + 2*pow(cos2_sigma_m,2)) - B/6
            * cos2_sigma_m * (-3 + 4*pow(sin_sigma,2)) * (-3 + 4*pow(cos2_sigma_m,2)))
        sigma_p = sigma
        sigma = s / (b * A) + delta_sigma

    tmp = sin_u1 * sin_sigma - cos_u1 * cos_sigma * cos_alpha1
    lat2 = atan2((sin_u1 * cos_sigma + cos_u1 * sin_sigma * cos_alpha1), 
        (1-f) * sqrt(pow(sin_alpha,2) + pow(tmp,2)))
    lambd = atan2((sin_sigma * sin_alpha1),
        (cos_u1 * cos_sigma - sin_u1 * sin_sigma * cos_alpha1))
    C = f/16 * cos_sq_alpha * (4 + f * (4 - 3 * cos_sq_alpha))
    L = lambd - (1 - C) * f * sin_alpha * (sigma + C * sin_sigma * 
        (cos2_sigma_m + C * cos_sigma * (-1 + 2 * pow(cos2_sigma_m,2))))
    lon2 = (radians(lon1) + L + 3 * pi) % (2*pi) - pi

    return (degrees(lat2), degrees(lon2))

# def get_angle(p1, p2):
#     """ tbd if using -- may delete """
#     lat_diff = p2.lat - p1.lat
#     lon_diff = p2.lon - p1.lon
#     angle = degrees(atan2(lon_diff,lat_diff))
#     if angle < 0:
#         angle += 360
#     return angle

# def convert_to_directions(angle):
#     """ tbd if using -- may delete """
#     if 337.5 < angle or angle <= 22.5:
#         return 'N'
#     if 22.5 < angle <= 67.5:
#         return 'NE'
#     if 67.5 < angle <= 112.5:
#         return 'E'
#     if 112.5 < angle <= 157.5:
#         return 'SE'
#     if 157.5 < angle <= 202.5:
#         return 'S'
#     if 202.5 < angle <= 247.5:
#         return 'SW'
#     if 247.5 < angle <= 292.5:
#         return 'W'
#     if 292.5 < angle <= 337.5:
#         return 'NW'


# def find_closest(i_id):
#     """ tbd if using -- may delete """
#     global route
#     ends = find_edges(i_id)
#     ends = (e for e in ends if e not in route)
#     best = None
#     current_elev = dbs.session.query(dbs.Intersection).get(i_id).elev
#     for e in ends:
#         next_elev = dbs.session.query(dbs.Intersection).get(e).elev
#         diff = abs(current_elev - next_elev)
#         if not best:
#             best = e
#         if e < best:
#             best = e
#     route.append(best)
#     return best

from geopy import distance, Point
import save_data as sd
from math import atan2, degrees

def find_dist(x1, x2):
    pt1 = Point(x1.lat, x1.lon)
    pt2 = Point(x2.lat, x2.lon)
    dist = distance.distance(pt1, pt2).feet
    return dist

def find_miles(x1, x2):
    pt1 = Point(x1.lat, x1.lon)
    pt2 = Point(x2.lat, x2.lon)
    dist = distance.distance(pt1, pt2).miles
    return dist

def vert_climb(x1,x2):
    return x2.elev - x1.elev

# def find_edges(i_id):
#     edges = sd.session.query(sd.Edge).filter_by(end_a=i_id).all()
#     ends = [e.end_b for e in edges]
#     edges = sd.session.query(sd.Edge).filter_by(end_b=i_id).all()
#     ends += [e.end_a for e in edges]
#     return ends

def find_closest(i_id):
    global route
    ends = find_edges(i_id)
    ends = (e for e in ends if e not in route)
    best = None
    current_elev = sd.session.query(sd.Intersection).get(i_id).elev
    for e in ends:
        next_elev = sd.session.query(sd.Intersection).get(e).elev
        diff = abs(current_elev - next_elev)
        if not best:
            best = e
        if e < best:
            best = e
    route.append(best)
    return best

def get_angle(p1, p2):
    lat_diff = p2.lat - p1.lat
    lon_diff = p2.lon - p1.lon
    angle = degrees(atan2(lon_diff,lat_diff))
    if angle < 0:
        angle += 360
    return angle

def convert_to_directions(angle):
    if 337.5 < angle or angle <= 22.5:
        return 'N'
    if 22.5 < angle <= 67.5:
        return 'NE'
    if 67.5 < angle <= 112.5:
        return 'E'
    if 112.5 < angle <= 157.5:
        return 'SE'
    if 157.5 < angle <= 202.5:
        return 'S'
    if 202.5 < angle <= 247.5:
        return 'SW'
    if 247.5 < angle <= 292.5:
        return 'W'
    if 292.5 < angle <= 337.5:
        return 'NW'
from finding_fns import find_miles as dist
from finding_fns import find_dist as dist_feet
import dbs


def find_route(start, route_distance):

    ## explore out
    first_distance = float(route_distance) * (float(3)/5)
    first_leg = a_star(start, None, first_distance, explore_score_fn)
    first_end = first_leg.get('path')[-1]

    ## make score function for return, to avoid path out
    return_score_fn = make_square_score_fn(first_leg.get('path'))

    ## explore back, avoiding path already taken
    return_leg = a_star(first_end, start, None, return_score_fn)

    ## combine route info
    route = {}
    route['path'] = first_leg['path'] + return_leg['path'][1:]
    route['distance'] = first_leg['distance'] + return_leg['distance']
    route['gain'] = first_leg['gain'] + return_leg['gain']

    return route


def explore_score_fn(start, end, current):
    ## exploring: minimize elevation gain, incentivize going "away" by minimizing inverse dist
    return ( pow((current.rel_climb + current.abs_climb + current.grade + current.elev_diff),2) + 
        pow(current.i_value(start),2))


def make_square_score_fn(path_to_avoid):
    def actual_square_score_fn(start, end, current):
        ## more traditional A* scoring coming back
        score = (pow((current.rel_climb + current.abs_climb + current.grade + current.elev_diff),2) + 
            current.distance + current.h_value(end))

        ## encourage going away from path already taken
        path_ids = [n.id for n in path_to_avoid]
        nearest = dbs.session.query(dbs.GIntersection).filter(dbs.GIntersection.id.in_(path_ids)).order_by(dbs.func.ST_Distance(dbs.GIntersection.loc, current.loc)).first()
        dist_to_path = dist(current, nearest)
        if dist_to_path != 0:
            score_from_avoiding = 1/dist_to_path
        else:
            score_from_avoiding = 100

        return score + score_from_avoiding

    return actual_square_score_fn


def a_star(start, end, route_distance, score_fn):
    open_set = set()
    closed_set = set()
    current = start
    open_set.add(current)
    path = []
    route_info = {}
    gain = 0

    while open_set:
        current = min(open_set, key=lambda this: score_fn(start, end, this))
        closed_set.add(current)
        open_set.remove(current)
        print current.distance

        if (end is not None and current.id == end.id) or (route_distance is not None and current.distance > route_distance):
            while current.parent:
                path.append(current)
                gain += abs(current.elev - current.parent.elev)
                current = current.parent
            path.append(current)
            route_info['path'] = path[::-1]
            route_info['distance'] = path[0].distance
            route_info['gain'] = gain
            return route_info
        for neighbor in current.ends:
            # cost = current.g + neighbor.move_cost(current)

            if neighbor.is_in(closed_set):
                continue

            # if neighbor.is_in(open_set):
            #     if cost < neighbor.g:
            #         open_set.remove(neighbor)
            if not neighbor.is_in(open_set) and not neighbor.is_in(closed_set):
                neighbor.parent = current
                neighbor.distance = current.distance + dist(neighbor, current)
                neighbor.from_way = neighbor.find_from_way(neighbor.parent)
                neighbor.rel_climb = neighbor.elev - current.elev
                neighbor.abs_climb = current.abs_climb + neighbor.rel_climb
                neighbor.grade = neighbor.rel_climb / dist_feet(neighbor, current)
                neighbor.elev_diff = abs(neighbor.elev - start.elev)
                open_set.add(neighbor)
    return None

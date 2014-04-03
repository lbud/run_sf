from finding_fns import find_miles as dist
from finding_fns import find_dist as dist_feet
import dbs


## take street names into account
## make it super expensive to double back onto itself


def find_route(start, route_distance):

    ## explore out
    first_distance = float(route_distance) * (float(9)/20)
    first_leg = a_star(start, None, first_distance, explore_score_fn)
    first_end = first_leg.get('path')[-1]
    print [(p.id, p.lat, p.lon) for p in first_leg.get('path')]

    ## make score function for return, to avoid path out
    return_score_fn = make_square_score_fn(first_leg.get('path'))

    ## explore back, avoiding path already taken
    return_leg = a_star(first_end, start, route_distance, return_score_fn)
    print [(p.id, p.lat, p.lon) for p in return_leg.get('path')]

    ## combine route info
    route = {}
    route['path'] = return_leg['path']  #first_leg['path'] +
    route['distance'] = return_leg['distance']  #first_leg['distance'] +
    route['gain'] = first_leg['gain'] + return_leg['gain']

    return route


def explore_score_fn(start, end, current, route_distance):
    ## exploring: minimize elevation gain, incentivize going "away" by minimizing inverse dist

    climb_score = (current.rel_climb + current.abs_climb + abs(pow(current.grade,3)) + 
        2*current.elev_diff)
    distance_score = 60000 * current.i_value(start)

    return climb_score + distance_score


def make_square_score_fn(path_to_avoid):
    def actual_square_score_fn(start, end, current, route_distance):
        ## more traditional A* scoring coming back
        # score = (pow((current.rel_climb + current.abs_climb + current.grade + current.elev_diff),2) + current.distance + current.h_value(end))
        score = 10*current.grade + pow(current.elev_diff,2) 
        print "rel climb", current.rel_climb
        print "abs climb", current.abs_climb
        print "grade", current.grade
        print "overall elev d", current.elev_diff
        print "distance", current.distance
        print "dist desired remaining", route_distance - current.distance
        print "h_value", current.h_value(end)
        print "score w/o avoiding,", score

        ## encourage going away from path already taken
        path_ids = [n.id for n in path_to_avoid]
        nearest = dbs.session.query(dbs.GIntersection).filter(dbs.GIntersection.id.in_(path_ids)).order_by(dbs.func.ST_Distance(dbs.GIntersection.loc, current.loc)).first()
        dist_to_path = dist(current, nearest)
        if dist_to_path != 0:
            score_from_avoiding = 1/dist_to_path
            print "score from avoiding", score_from_avoiding
        else:
            score_from_avoiding = 100
            print "oops found a non-score: score_from_avoiding=100"

        print "SCORE," 
        print score + score_from_avoiding
        print "\n"
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
        current = min(open_set, key=lambda this: score_fn(start, end, this, route_distance))
        closed_set.add(current)
        open_set.remove(current)

        if (end is not None and current.distance > (.95 * route_distance)  and current.id == end.id) or (route_distance is not None and current.distance > route_distance):
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
                # neighbor.distance = current.distance + dist(neighbor, current)
                # neighbor.from_way = neighbor.find_from_way(neighbor.parent)
                neighbor.elev_diff = abs(neighbor.elev - start.elev)
                open_set.add(neighbor)
    return None

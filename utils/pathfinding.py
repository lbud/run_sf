from finding_fns import find_miles as dist
from finding_fns import find_dist as dist_feet
import dbs


## take street names into account
## make it super expensive to double back onto itself


def find_route(start, route_distance):

    ## explore out
    start_node = start
    global total_route_distance
    total_route_distance = route_distance
    first_distance = float(route_distance) * .45
    first_leg = a_star(start_node, None, first_distance, explore_score_fn)
    first_end = first_leg.get('path')[-1]
    # print [(p.id, p.lat, p.lon) for p in first_leg.get('path')]

    ## make score function for return, to avoid path out
    return_score_fn = make_loop_score_fn(first_leg.get('path'))

    ## explore back, avoiding path already taken
    return_leg = a_star(first_end, start_node, None, return_score_fn)
    for p in return_leg.get('path'):
        print (p.lat, p.lon)

    ## route info to return -- only needs return_leg info as everything is calculated from parents
    route = {}
    route['path'] = return_leg['path']
    route['distance'] = return_leg['distance']
    route['gain'] = return_leg['gain']

    return route


def explore_score_fn(start, end, current, route_distance):
    ## exploring out: minimize elevation gain, incentivize going "away" by minimizing inverse dist

    climb_score = current.rel_climb*current.elev_diff
    # (pow(current.rel_climb, 2) + abs(pow(current.grade,3)) + 2*current.elev_diff)
    distance_score = 60000 * current.i_value(start) + 2*current.distance

    # print "try", current.rel_climb*current.elev_diff
    # print "rel climb", current.rel_climb
    # print "abs climb", current.abs_climb
    # print "grade", current.grade
    # print "overall elev d", current.elev_diff
    # print  "climb score", climb_score
    # print "distance score", distance_score, "\n"
    return climb_score + distance_score


def make_loop_score_fn(path_to_avoid):
    def actual_loop_score_fn(start, end, current, route_distance):
        ## more traditional A* scoring coming back
        # score = (pow((current.rel_climb + current.abs_climb + current.grade + current.elev_diff),2) + current.distance + current.h_value(end))
        score = 10*abs(current.grade) + current.elev_diff + 20*current.distance + 20*current.h_value(end)
        print "10*grade", 10*abs(current.grade)
        print "overall gain squared", current.elev_diff
        print "total dist", current.distance*20
        print "h val", current.h_value(end)*20
        print "score", score, "\n"
        # print "rel climb", current.rel_climb
        # print "abs climb", current.abs_climb
        # print "grade", current.grade
        # print "overall elev d", current.elev_diff
        # print "distance", current.distance
        # print "dist desired remaining", route_distance - current.distance
        # print "h_value", current.h_value(end)
        # print "score w/o avoiding,", score

        ## encourage going away from path already taken
        path_ids = [n.id for n in path_to_avoid]
        nearest = dbs.session.query(dbs.GIntersection).filter(dbs.GIntersection.id.in_(path_ids)).order_by(dbs.func.ST_Distance(dbs.GIntersection.loc, current.loc)).first()
        dist_to_path = dist(current, nearest)
        print "dist to path", dist_to_path
        if dist_to_path != 0:
            score_from_avoiding = 1/dist_to_path
            # print "score from avoiding", score_from_avoiding
        else:
            score_from_avoiding = 100
            # print "oops found a non-score: score_from_avoiding=100"

        # print "SCORE," 
        # print score + score_from_avoiding
        # print "\n"
        print score_from_avoiding*current.h_value(end)
        print "scored from avoiding\n"
        return score + current.h_value(end)*10*score_from_avoiding

    return actual_loop_score_fn


def a_star(start, end, route_distance, score_fn):
    global total_route_distance
    print total_route_distance
    open_set = set()
    closed_set = set()
    current = start
    open_set.add(current)
    path = []
    route_info = {}
    gain = 0

    while open_set:
        current = min(open_set, key=lambda n: n.score)
        closed_set.add(current)
        open_set.remove(current)

        if (end is not None and current.distance > (.95 * total_route_distance)  and current.id == end.id) or (route_distance is not None and current.distance > route_distance):
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
            neighbor.parent = current
            if end:
                neighbor.elev_diff = abs(neighbor.elev - end.elev)
            else:
                neighbor.elev_diff = abs(neighbor.elev - start.elev)
            score = score_fn(start, end, neighbor, route_distance)

            if neighbor.is_in(closed_set):
                continue

            # if neighbor.is_in(open_set):
            #     if score < neighbor.score:
            #         open_set.remove(neighbor)

            found = None
            for n in open_set:
                if n.id == neighbor.id:
                    # print "found open set"
                    if score < n.score:
                        found = n
            if found:
                open_set.remove(found)
                # print "removing"

            if not neighbor.is_in(open_set) and not neighbor.is_in(closed_set):
                neighbor.score = score
                open_set.add(neighbor)
    return None

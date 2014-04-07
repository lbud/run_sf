from .finding_fns import find_miles as dist
import dbs


def find_route(start, route_distance):

    # explore out
    start_node = start
    global total_route_distance
    total_route_distance = route_distance
    first_distance = float(route_distance) * .38
    first_leg = a_star(start_node, None, first_distance, explore_score_fn)
    first_end = first_leg.get('path')[-1]
    print [(p.id, p.lat, p.lon) for p in first_leg.get('path')]

    # make score function for return, to avoid path out
    return_score_fn = make_loop_score_fn(first_leg.get('path'))

    # explore back, avoiding path already taken
    return_leg = a_star(first_end, start_node, None, return_score_fn)
    for p in return_leg.get('path'):
        print (p.lat, p.lon)

    # route info to return -- only needs return_leg info as everything is
    # calculated from parents
    route = {}
    route['path'] = return_leg['path']
    route['distance'] = return_leg['distance']
    route['gain'] = return_leg['gain']

    return route


def explore_score_fn(start, end, current, route_distance):
    # exploring out: minimize elevation gain, incentivize going "away" by
    # minimizing inverse dist

    climb_score = current.rel_climb*current.elev_diff
    # TODO: refine. options:
    # current.rel_climb
    # current.elev_diff
    # current.abs_climb
    # current.grade
    # current.elev_diff

    distance_score = 60000 * current.i_value(start) + 2*current.distance
    # TODO: refine

    # try to make it not double back on the other side of a divided street
    doubling_back = 0
    if current.parent and current.parent.parent and \
            current.parent.parent.parent:
        if current.way_name != current.parent.way_name and \
                current.way_name == current.parent.parent.way_name or \
                current.way_name == current.parent.parent.parent.way_name:
            doubling_back = 100
    return climb_score + distance_score + doubling_back


def make_loop_score_fn(path_to_avoid):
    def actual_loop_score_fn(start, end, current, route_distance):
        # more traditional A* scoring coming back
        score = 10 * abs(current.grade) + current.elev_diff + \
            20 * current.distance + 20 * current.h_value(end)
        # TODO: refine. options:
        # current.grade
        # current.elev_diff
        # current.distance
        # current.h_value(end)
        # current.rel_climb
        # current.abs_climb
        # current.grade
        # current.elev_diff
        # current.distance
        # route_distance - current.distance

        # encourage going away from path already taken
        path_ids = [n.id for n in path_to_avoid]
        nearest = dbs.session.query(
            dbs.GIntersection).filter(dbs.GIntersection.id.in_(path_ids)).\
            order_by(
                dbs.func.ST_Distance(dbs.GIntersection.loc, current.loc)
            ).first()
        dist_to_path = dist(current, nearest)

        if dist_to_path != 0:
            score_from_avoiding = 1/dist_to_path

        else:
            score_from_avoiding = 100
            # TODO check to see that this is an appropriate score -- both
            # beginning and end of return

        return score + (10 * current.h_value(end) * score_from_avoiding)

    return actual_loop_score_fn


def a_star(start, end, route_distance, score_fn):
    global total_route_distance
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

        if (end is not None and current.distance > (.95 * total_route_distance)
                and current.id == end.id) or \
                (route_distance is not None and current.distance >
                 route_distance):
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

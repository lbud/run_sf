from .finding_fns import find_miles as dist
import dbs


def find_route(start, route_distance):
    """
    Finds a route out and back from a point, given a distance.

    On the way out, with no endpoint, this searches for nodes with relatively
    little elevation gain in the general direction of "away."

    On the way back, the start point is the endpoint and it acts more like
    traditional A*, but also takes into account elevation as well as the path
    already taken (and tries to avoid it), so as to create a looping route.
    """

    start_node = start
    global total_route_distance
    total_route_distance = route_distance

    # Explore out from starting point.
    first_distance = float(route_distance) * .35
    first_leg = a_star(start_node, None, first_distance, explore_score_fn)
    first_end = first_leg.get('path')[-1]
    # print [(p.id, p.lat, p.lon) for p in first_leg.get('path')]

    # Make score function for return, to avoid the path already taken.
    return_score_fn = make_loop_score_fn(first_leg.get('path'))

    # Explore back, avoiding path already taken.
    return_leg = a_star(first_end, start_node, None, return_score_fn)
    # return_leg = a_star(first_end, None, 0, explore_score_fn)

    # for p in return_leg.get('path'):
    #     print (p.lat, p.lon)

    # Route info to return -- only needs return_leg info as everything is
    # calculated from node parents
    route = {}
    route['path'] = return_leg['path']
    route['distance'] = return_leg['distance']
    route['gain'] = return_leg['gain']

    return route


def explore_score_fn(start, end, current, route_distance):
    """
    Scores nodes for the "explore out" segment. Incentivizes going "away" by
    assigning lower costs to farther nodes (using inverse distance).
    """

    climb_score = abs(current.rel_climb+current.elev_diff)
    # TODO: Tweak scoring. Elevation-related options:
    # current.rel_climb
    # current.elev_diff
    # current.abs_climb
    # current.grade
    # current.elev_diff

    distance_score = 20000 * current.i_value(start) + 2*current.distance
    # TODO: Tweak scoring.

    # Try to make it not double back on the other side of a divided street
    # by assigning high score to doubled-back routes.
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
        """
        Uses more traditional A* scoring on return leg, as it now has an end
        point. Takes into account elevation, distance to current node, distance
        from node to end.
        """

        # more traditional A* scoring coming back
        score = abs(current.rel_climb + current.elev_diff) + \
            current.distance + current.h_value(end)
        # TODO: Tweak scoring. Options:
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

        # Encourages staying away from path already taken.
        path_ids = [n.id for n in path_to_avoid]
        nearest = dbs.session.query(
            dbs.GIntersection).filter(dbs.GIntersection.id.in_(path_ids)).\
            order_by(
                dbs.func.ST_Distance(dbs.GIntersection.loc, current.loc)
            ).first()
        dist_to_path = dist(current, nearest)

        # Encourages staying away from the path already taken
        # by assigning a higher score to closer nodes.
        if dist_to_path != 0:
            score_from_avoiding = 1/dist_to_path

        # If this happens to be the first node (so distance = 0), just give it
        # a high score.
        else:
            score_from_avoiding = 100

        # Multiply score from avoiding by heuristic cost to the endpoint, so
        # that the closer it gets to the end, the closer it may get to the path
        # already taken.
        return score + (10 * current.h_value(end) * score_from_avoiding)

    return actual_loop_score_fn


def a_star(start, end, route_distance, score_fn):
    """
    Modeled after traditional A* pathfinding.  Keeps sets of nodes searched and
    to search, in order to find the best route.
    """

    global total_route_distance
    if end is None:
        endpoint = start
    else:
        endpoint = end

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

        # End of this route leg:
        if (end is not None and current.distance > (.95 * total_route_distance)
                and current.id == end.id) or \
                (route_distance is not None and current.distance >
                 route_distance):
            # Add all nodes in path to route data
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
            if dist(neighbor, endpoint) < (total_route_distance / 2):
                neighbor.parent = current
                if end:    # for return route
                    neighbor.elev_diff = abs(neighbor.elev - end.elev)
                else:    # for exploring out
                    neighbor.elev_diff = abs(neighbor.elev - start.elev)

                # Assigns score to node based on given score function
                score = score_fn(start, end, neighbor, route_distance)

                if neighbor.is_in(closed_set):
                    continue

                # Removes from open set to be replaced if new score to node is
                # better than that already found.
                found = None
                for n in open_set:
                    if n.id == neighbor.id:
                        if score < n.score:
                            found = n
                if found:
                    open_set.remove(found)

                # Adds neighbor nodes (if not already searched) to open set.
                if not neighbor.is_in(open_set) and not neighbor.is_in(closed_set):
                    neighbor.score = score
                    open_set.add(neighbor)
    return None

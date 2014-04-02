from finding_fns import find_miles as dist

def pathfind(current, leg_distance, end=None):
    # make a bunch of path things global
    # wayfind, modifying heuristics

    pass


"""
#TODO elev heuristic should include diff between current 
and last, because if start=10, curr=15, next being 13 is way 
more preferable than next being 17 even though they are
the same diff from current
"""


def a_star(start, route_distance):
    open_set = set()
    closed_set = set()
    current = start
    open_set.add(current)
    path = []
    route_info = {}
    distance = 0
    gain = 0
    edge_route = []
    half_dist = float(route_distance) / 2

    while open_set:
        if current.distance < half_dist:
            current = min(open_set, key=lambda f:f.g + f.i_value(start))
            closed_set.add(current)
            open_set.remove(current)


            for neighbor in current.ends:
                cost = current.g + neighbor.move_cost(current)
                neighbor.distance = current.distance + dist(neighbor, current)

                if neighbor.is_in(closed_set):
                    continue

                if neighbor.is_in(open_set):
                    if cost < neighbor.g:
                        open_set.remove(neighbor)
                if not neighbor.is_in(open_set) and not neighbor.is_in(closed_set):
                    neighbor.g = cost
                    open_set.add(neighbor)
                    neighbor.parent = current
                    neighbor.from_way = neighbor.find_from_way(neighbor.parent)
        else:
            closed_set = set()
            open_set = set()
            open_set.add(current)
            break

    while open_set:
        current = min(open_set, key=lambda f:f.g + f.h_value(start))
        closed_set.add(current)
        open_set.remove(current)

        if current.id == start.id:
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
            cost = current.g + neighbor.move_cost(current)
            neighbor.distance = current.distance + dist(neighbor, current)

            if neighbor.is_in(closed_set):
                continue

            if neighbor.is_in(open_set):
                if cost < neighbor.g:
                    open_set.remove(neighbor)
            if not neighbor.is_in(open_set) and not neighbor.is_in(closed_set):
                neighbor.g = cost
                open_set.add(neighbor)
                neighbor.parent = current
                neighbor.from_way = neighbor.find_from_way(neighbor.parent)

    return None
from finding_fns import find_miles as dist

def a_star(start, route_distance, route_type, end=None):
    open_set = set()
    closed_set = set()
    current = start
    open_set.add(current)
    path = []
    route_info = {}
    # distance = 0
    gain = 0
    if route_type == "outandback" or route_type == "loop":
        end = start
    if route_type == "oneway":
        route_distance = 0


    ## RUN AWAY
    while open_set:
        current = min(open_set, key=lambda f:f.g + f.h_value(start))
        closed_set.add(current)
        open_set.remove(current)

        ## render at the end
        if current.distance > route_distance/2 and current.id == end.id:
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
from finding_fns import find_miles as dist

# path functions
path_away = lambda f: f.rel_climb(f.parent) + f.abs_climb(start) + (inv dist)
path_to_corner = lambda f: (rel climb) + (abs climb) + (???)
path_corner_home = lambda f: (rel climb) + (abs climb) + (???)
path_home = lambda f: f.g + f.abs_climb(start) + f.h_value(start)

def pathfind(path_function):
    global closed_set
    global open_set
    current = min(open_set, key=path_function)
    closed_set.add(current)
    open_set.remove(current)

    for neighbor in current.ends:
        cost = current.g + neighbor.move_cost(current)  #this has to be modified all around

        if neighbor.is_in(closed_set):
            continue

        if neighbor.is_in(open_set):
            if cost < neighbor.g:    #this has to be modified depending on leg
                open_set.remove(neighbor)
        if not neighbor.is_in(open_set) and not neighbor.is_in(closed_set):
            neighbor.distance = current.distance + dist(neighbor, current)
            # neighbor.g = cost
            neighbor.parent = current
            neighbor.from_way = neighbor.find_from_way(neighbor.parent)
            neighbor.rel_climb = neighbor.elev - current.elev
            neighbor.abs_climb = current.abs_climb + rel_climb
            open_set.add(neighbor)


# def pathfind(current, priority, end=None):
#     if priority == "away":
#     elif priority == "loop_leg_2":
#         pass
#     elif priority == "loop_leg_3":
#         pass
#     elif priority == "home":
#         pass
#     # make a bunch of path things global
#     # wayfind, modifying heuristics

#     pass


"""
#TODO elev heuristic should include diff between current 
and last, because if start=10, curr=15, next being 13 is way 
more preferable than next being 17 even though they are
the same diff from current
"""

"""
pseudocode

if loop:
    go out 1/4ish
        min relative gain
        min absolute gain
        max distance from start
    go out 1/4ish
        min relative gain
        min absolute gain
        max distance from quarter
        weakly, ratio of distance from quarter to distance from start ???
    check dist from start:
        if ~1/2 running distance:
            go home
        else:
            go another leg, getting closer to start
            then go home

elif outandback:
    go away
    retrace route

elif ow:
    go away


more pythonic

while open_set:
    if current.distance < 1/4:
            *** IF outandback OR ow: do this only
                IF outandback: return twice the route
        pick best for that heuristic
    elif 1/4 < current.distance < 1/2:
        pick best for that heuristic
    elif 1/2 < current.distance < 3/4:
        pick best
    else:
        pick best to go home






"""


def a_star(start, route_distance, route_type):
    open_set = set()
    closed_set = set()
    current = start
    open_set.add(current)
    path = []
    route_info = {}
    distance = 0
    cumulative_gain = 0
    edge_route = []
    half_dist = route_distance / 2
    if route_type == "loop":
        first_leg = route_distance / 4
    elif route_type == "outandback":
        first_leg = route_distance / 2
    elif route_type == "oneway":
        # FIX THIS -- traditional pathfinding
        pass


    while open_set:





        if current.distance < first_leg:
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
                cumulative_gain += abs(current.elev - current.parent.elev)
                current = current.parent
            path.append(current)
            route_info['path'] = path[::-1]
            route_info['distance'] = path[0].distance
            route_info['gain'] = cumulative_gain
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
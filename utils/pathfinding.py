from save_data import Edge, Intersection

def a_star(start, end):
    open_set = set()
    closed_set = set()
    current = start
    open_set.add(current)
    path = []

    while open_set:
        current = min(open_set, key=lambda f:f.g + f.h_value(end))
        closed_set.add(current)
        open_set.remove(current)

        if current.id == end.id:
            while current.parent:
                path.append(current)
                current = current.parent
            return path[::-1]

        for neighbor in current.ends:
            cost = current.g + neighbor.move_cost(current)

            if neighbor.is_in(closed_set):
                continue

            if neighbor.is_in(open_set):
                if cost < neighbor.g:
                    open_set.remove(neighbor)
            if not neighbor.is_in(open_set) and not neighbor.is_in(closed_set):
                neighbor.g = cost
                open_set.add(neighbor)
                neighbor.parent = current
    return None
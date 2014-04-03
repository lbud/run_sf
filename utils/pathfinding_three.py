from finding_fns import find_miles as dist
from finding_fns import find_dist as dist_feet


class AStar(object):
    def __init__(self, start, route_distance, route_type, end=None):
        self.start = start
        self.route_distance = route_distance
        self.route_type = route_type
        if end is not None:
            self.end = end
        else:
            self.end = start
        self.open_set = set()
        self.closed_set = set()
        self.path = []
        self.route_info = {}
        self.current = start
        self.corner_one = None
        self.corner_two = None

        #TODO weight these 
        self.path_away = lambda f: f.rel_climb + f.abs_climb + f.elev_diff + pow(f.i_value(self.start),2)
        self.path_to_corner = lambda f: f.rel_climb + f.abs_climb + f.elev_diff + f.i_value(self.corner_one)
        self.path_corner_home = lambda f: f.rel_climb + f.abs_climb + f.elev_diff + f.distance + f.h_value(self.start)
        self.path_home = lambda f: f.rel_climb + f.abs_climb + f.elev_diff + f.distance + pow(f.h_value(self.start),2)

    def find_route(self, route_type):
        while self.open_set:
            if route_type == "outandback":
                if self.distance < self.route_distance/2:           #while?
                    self.find_leg(self.path_away)
                self.end_route("outandback")
            if route_type == "loop":
                if current.distance < self.route_distance / 4:      #while?
                    self.find_leg(self.path_away)
                if current.distance < self.route_distance / 2:      #while?
                    if not self.corner_one:
                        self.corner_one = current
                    self.find_leg(self.path_to_corner)
                if current.distance < self.route_distance * (3/4):  #while?
                    if not self.corner_two:
                        self.corner_two = current
                    self.find_leg(self.path_corner_home)
                if self.current.id == self.end.id:
                    self.end_route("loop")
                self.find_leg(self.path_home)
        return self.route_info


    def find_leg(self, leg_type):
        self.current = min(open_set, key=leg_type)
        self.closed_set.add(self.current)
        self.open_set.remove(self.current)

        for neighbor in self.current.ends:
            # //TODO #cost = current.g + neighbor.move_cost(current)
            # //TODO #neighbor.distance = current.distance + dist(neighbor, current)

            if neighbor.is_in(closed_set):
                continue

            # if neighbor.is_in(open_set):
            #     if cost < neighbor.g:
            #         open_set.remove(neighbor)
            if not neighbor.is_in(open_set) and not neighbor.is_in(closed_set):
                # neighbor.g = cost
                neighbor.parent = current
                neighbor.from_way = neighbor.find_from_way(neighbor.parent)
                neighbor.rel_distance = dist(neighbor, current)
                neighbor.distance = current.distance + neighbor.rel_distance
                neighbor.rel_climb = neighbor.elev - current.elev
                neighbor.abs_climb = current.abs_climb + neighbor.rel_climb
                neighbor.grade = neighbor.rel_climb / dist_feed(neighbor, current)
                neighbor.elev_diff = neighbor.elev - self.start.elev
                self.open_set.add(neighbor)

        return self.current


    def end_route(self, route_type):
        while self.current.parent:
            self.path.append(self.current)
            self.gain += abs(self.current.elev - self.current.parent.elev)
            self.current = self.current.parent
        self.path.append(self.current)
        self.route_info['path'] = self.path[::-1]
        self.route_info['distance'] = self.path[0].distance
        self.route_info['gain'] = self.gain
        if self.route_type == "outandback":
            self.route_info['path'] += path[1:]
            self.route_info['distance'] *= 2
            self.route_info['gain'] *= 2
        return self.route_info
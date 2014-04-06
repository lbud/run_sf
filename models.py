from utils.dbs import GIntersection
import utils.dbs as dbs
from math import sqrt, pow
from utils.finding_fns import find_dist, vert_climb, find_miles, vincenty, radials, gen_radii, nearest_intersection
from utils.pathfinding import find_route
import json


class Route(object):
    def __init__(self, start, route_distance, end=None): #, route_type="loop"
        self.start = start
        # self.route_type = route_type
        self.end = end
        self.first = Node(nearest_intersection(self.start).id)
        self.route_distance = float(route_distance)
        self.path = find_route(self.first, route_distance)

        self.distance = self.path.get('distance')
        self.gain = self.path.get('gain')
        self.clean = self.clean_path


    @property
    def possible_ends(self):
        # TODO: find a set of possible end points
        # for now, just return one
        ##
        # return [Node()s]
        pass

    @property
    def clean_path(self):
        full_path = self.path.get('path')
        clean_path = [full_path[0]]
        for i in range(1, len(full_path)-1):
            if full_path[i].way_name == full_path[i-1].way_name and full_path[i].way_name == full_path[i+1].way_name:
                continue
            else:
                clean_path.append(full_path[i])
        clean_path.append(full_path[-1])
        return clean_path

    @property
    def render(self):
        start = [[self.start[0], self.start[1]]]
        # FOR DEBUGGING: return all
        # coord_list = start + [[n.lat, n.lon] for n in self.path.get('path')[1:-1]] + start
        coord_list = start + [[n.lat, n.lon] for n in self.clean[1:-1]] + start
        coords = json.dumps({"coords":[c for c in coord_list]})
        return coords

class Node(object):
    def __init__(self, id):
        self.id = id
        this = dbs.session.query(dbs.GIntersection).get(id)
        self.loc = this.loc
        self.lat = this.lat
        self.lon = this.lon
        self.elev = this.elev
        self.edges = this.edges
        self.parent = None
        self.elev_diff = 0.0
        self.score = 0

    @property
    def ends(self):
        ends = []
        for edge in self.edges:
            for end in edge.ends:
                if end.id != self.id:
                    ends.append(Node(end.id))
        return ends

    @property
    def rel_climb(self):
        if self.parent:
            return self.elev - self.parent.elev
        return 0.0

    @property
    def abs_climb(self):
        if self.parent:
            return abs(self.rel_climb) + self.parent.abs_climb
        return 0.0

    @property
    def distance(self):
        """ returns distance in miles """
        if self.parent:
            return find_miles(self, self.parent) + self.parent.distance
        return 0.0

    @property
    def grade(self):
        if self.parent:
            return 100 * self.rel_climb / find_dist(self, self.parent)
        return 0.0

    @property # for use in the following two properties, to minimize DB queries
    def shared_edge(self):
        if self.parent:
            shared_edge = filter(lambda x: x in self.edges, self.parent.edges)
            if shared_edge:
                return shared_edge[0]
        return None

    @property
    def way_name(self):
        if self.shared_edge:
            return self.shared_edge.way_name
        return None

    @property
    def from_way(self):
        if self.shared_edge:
            return self.shared_edge.way_id
        return None

    # @property
    # def from_way(self):
    #     if self.parent:
    #         shared_edge = filter(lambda x: x in self.edges, self.parent.edges)
    #         if shared_edge:
    #             return shared_edge[0].way_id
    #     return None



    def h_value(self, end):
        miles_to_end = find_miles(self,end)
        return miles_to_end

    def i_value(self, start):
        inverse_distance = find_dist(self, start)
        if inverse_distance != 0:
            inverse_distance = 1 / inverse_distance
        return inverse_distance

    def is_in(self, other_set):
        if True in {self.id == o.id for o in other_set}:
            return True
        return False



h = Node(65314183)   # gough & post                                         elev=63
n = Node(65303561)   # gough & sutter                                       elev=70
le = Node(65319011)     # laguna & ellis -- .3 mi away (geodesic)           elev=36
vl = Node(295191529)    # van ness & lombard -- 1 mi away (geodesic)        elev=30
ocean = Node(65304540)  # great highway & lincoln -- 4.9 mi away (geodesic) elev=7
mp = Node(1723739266)   # market & pine -- 1.6 mi (geodesic)                elev=3
em = Node(65345229)     # green & embarcadero -- 1.7m                       elev=2.5
ll = Node(65336684)     # lombard & lyon -- 1.5m                            elev=23
ap = Node(65315754)     # pacific & arguello -- 1.87m                       elev=91
fg = Node(65336114)     # greenwich & fillmore -- 1.06m                     elev=18
gs = Node(258759451)    # geary & scott --                                  elev=45 

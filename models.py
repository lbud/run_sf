from utils.dbs import GIntersection
import utils.dbs as dbs
from math import sqrt, pow
from utils.finding_fns import find_dist, vert_climb, find_miles, vincenty, radials, gen_radii, nearest_intersection
from utils.pathfinding import a_star
import json

class Route(object):
    def __init__(self, start, end):
        self.start = start
        self.first = Node(nearest_intersection(self.start).id)
        # self.route_distance = float(route_distance)
        self.end = end
        self.path = a_star(self.first, end)
        self.gain = self.path.get('gain')
        self.distance = self.path.get('distance')
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
            if full_path[i].from_way == full_path[i-1].from_way and full_path[i].from_way == full_path[i+1].from_way:
                continue
            else:
                clean_path.append(full_path[i])
        clean_path.append(full_path[-1])
        return clean_path

    @property
    def render(self):
        start = [[self.start[0], self.start[1]]]
        coord_list = start + [[n.lat, n.lon] for n in self.clean[1:]]
        coords = json.dumps({"coords":[c for c in coord_list]})
        return coords



class Node(object):
    def __init__(self, id):
        self.id = id
        this = dbs.session.query(dbs.GIntersection).get(id)
        self.loc = this.loc
        loc_tup = dbs.coords_tuple(self)
        self.lat = this.lat
        self.lon = this.lon
        self.elev = this.elev
        self.edges = this.edges
        self.parent = None
        self.from_way = None
        self.g = 0

    @property
    def ends(self):
        ends = []
        for edge in self.edges:
            for end in edge.ends:
                if end.id != self.id:
                    ends.append(Node(end.id))
        return ends

    def find_from_way(self, parent):
        shared_edge = filter(lambda x: x in self.edges, parent.edges)
        if shared_edge:
            return shared_edge[0].way_id

    def move_cost(self, last): # for computing g-scores
        if not last:
            return 0
        geodesic = find_dist(last, self)
        climb = vert_climb(last,self)
        return geodesic + pow(abs(climb),3)
        # TODO: tweak this so it's not such arbitrary guessing
        # return geodesic       # keeping this here to uncomment when comparing test routes

    def h_value(self, end):
        # climb = vert_climb(self, end)
        geodesic = find_dist(self,end)
        return geodesic

    def is_in(self, other_set):
        if True in {self.id == o.id for o in other_set}:
            return True
        return False

    def render(self):
        #return json(self.lon, self.lat)
        pass

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



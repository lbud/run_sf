from utils.dbs import Edge, Intersection
import utils.dbs as dbs
from math import sqrt, pow
from utils.finding_fns import find_dist, vert_climb, find_miles, vincenty, radials, gen_radii
from utils.pathfinding import a_star

class Route(object):
    def __init__(self, start, distance):
        self.start = starting_point
        self.distance = distance

    @property
    def possible_ends(self):
        # TODO: find a set of possible end points
        # for now, just return one
        ##
        # return [Node()s]
        pass

    @property
    def path(self):
        # call run_astar() for each start/end combo
        # for now, just calculate path without elev heuristic
        ##
        # return [Node()s]
        pass

    #@property?
    def render_path(self):
        # for each node:
            # node.render()
        pass

class Node(object):
    def __init__(self, id):
        self.id = id
        this = dbs.session.query(dbs.Intersection).get(id)
        self.lat = this.lat
        self.lon = this.lon
        self.elev = this.elev
        self.edges = this.edges
        self.parent = None
        self.g = 0

    @property
    def ends(self):
        ends = []
        for edge in self.edges:
            for end in edge.ends:
                if end.id != self.id:
                    ends.append(Node(end.id))
        return ends

    def move_cost(self, last): # for computing g-scores
        if not last:
            return 0
        geodesic = find_dist(last, self)
        climb = vert_climb(last,self)
        return geodesic + pow(abs(climb),4.5)
        # TODO: tweak this so it's not such arbitrary guessing
        # return geodesic       # keeping this here to uncomment when comparing test routes

    def h_value(self, end):
        climb = vert_climb(self, end)
        geodesic = find_dist(self,end)
        return sqrt(pow(climb,2) + pow(geodesic,2))

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

def print_coords(a, b):
    """ for ruote testing purposes """
    rt = a_star(a,b)
    for p in rt.get('path'):
        print "%r,%r" % (p.lat, p.lon)
    return rt

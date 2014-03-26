from utils.dbs import Edge, Intersection
import utils.dbs as dbs
from math import sqrt, pow
from utils.finding_fns import find_dist, vert_climb, find_miles, vincenty, radials, gen_radii
from utils.pathfinding import a_star

class Route(object):
    # def __init__(self, start, distance):
    def __init__(self, start, end):
        self.start = start
        # self.distance = distance
        self.end = end
        self.path = a_star(start, end)
        self.clean = None

    @property
    def possible_ends(self):
        # TODO: find a set of possible end points
        # for now, just return one
        ##
        # return [Node()s]
        pass

    @property
    def clean_path(self):
        if not self.clean:
            full_path = self.path.get('path')
            clean_path = [full_path[0]]
            for i in range(1, len(full_path)-1):
                if full_path[i].from_way == full_path[i-1].from_way and full_path[i].from_way == full_path[i+1].from_way:
                    continue
                else:
                    clean_path.append(full_path[i])
            clean_path.append(full_path[-1])
            self.clean = clean_path
            return self.clean
        return self.clean

    @property
    def render(self):
        render_locs = []
        for c in self.clean_path:
            render_locs.append(c.loc)
        return render_locs

class Node(object):
    def __init__(self, id):
        self.id = id
        this = dbs.mdb.nodes.find_one({'node_id': id})
        self.loc = this.get('loc')
        self.lat = self.loc[0]
        self.lon = self.loc[1]
        self.elev = this.get('elev')
        self.end_ids = this.get('ends')
        self.edges = this.get('edges')
        self.ways = this.get('ways')
        self.parent = None
        self.from_way = None
        self.g = 0

    @property
    def ends(self):
        ends = [Node(e) for e in self.end_ids]
        # for edge in self.edges:
        #     for end in edge.ends:
        #         if end.id != self.id:
        #             ends.append(Node(end.id))
        return ends

    def find_from_way(self, parent):
        # for edge in self.edges:
        shared_edge = filter(lambda x: x in self.ways, parent.ways)
        return shared_edge[0]

    def move_cost(self, last): # for computing g-scores
        if not last:
            return 0
        geodesic = find_dist(last, self)
        climb = vert_climb(last,self)
        return geodesic + pow(abs(climb),3)
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
    """ for route testing purposes """
    rt = a_star(a,b)
    for p in rt.get('path'):
        print "%r,%r" % (p.lat, p.lon)
    return rt

import json

from utils.finding_fns import find_dist, find_miles, nearest_intersection
from utils.pathfinding import find_route
import utils.dbs as dbs


class Route(object):
    def __init__(self, start, route_distance, route_type, end=None):
        self.start = start
        # self.route_type = route_type
        self.end = end
        self.first = Node(nearest_intersection(self.start).id)
        self.route_distance = float(route_distance)
        self.route_type = route_type
        self.path = find_route(self.first, route_distance, route_type)
        self.full_path = self.path.get('path')
        self.distance = self.path.get('distance')
        self.gain = self.path.get('gain')
        self.clean = self.clean_path
        self.full_node_path = self.all_nodes

    @property
    def clean_path(self):
        """ Returns path stripped of redundancies along the same street,
        for minimizing waypoints so as to comply better
        with Google DirectionsService API limits.

        Not currently used.
        """
        full_path = self.path.get('path')
        clean_path = [full_path[0]]
        for i in range(1, len(full_path)-1):
            if full_path[i].way_name == full_path[i-1].way_name and \
                    full_path[i].way_name == full_path[i+1].way_name:
                continue
            else:
                clean_path.append(full_path[i])
        clean_path.append(full_path[-1])
        return clean_path

    @property
    def all_nodes(self):
        """ Returns list of intersection nodes found through pathfinding
        algorithm, plus all nodes contained between intersections (for better
        rendering), in order.
        """
        node_list = []
        for i in self.full_path:
            if i.parent:
                for n in range(len(i.way_nodes)):
                    node_list.append(i.way_nodes[n])
            node_list.append(i)
        if self.route_type == "outandback":
            node_list += node_list[-2::-1]
        return node_list

    @property
    def render(self):
        """ Returns a JSON object of coordinates, for rendering on a map,
        plus other relevant data.
        """
        start = [[self.start[0], self.start[1]]]
        coord_list = start + [
            [n.lat, n.lon] for n in self.full_node_path if n is not None
        ] + start
        data = json.dumps({"coords": [c for c in coord_list], \
            "distance": round(self.distance, 2), "gain": round(self.gain, 2)})
        return data


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
        """ Returns the nodes at the end of each edge connected to this node.
        """
        ends = []
        for edge in self.edges:
            for end in edge.ends:
                if end.id != self.id:
                    ends.append(Node(end.id))
        return ends

    @property
    def rel_climb(self):
        """ Returns the relative climb from this node's parent to this node.
        """
        if self.parent:
            return self.elev - self.parent.elev
        return 0.0

    @property
    def abs_climb(self):
        """ Returns the sum of this node's relative climb and all climbs before
        it. For aggregating climb.
        """
        if self.parent:
            return abs(self.rel_climb) + self.parent.abs_climb
        return 0.0

    @property
    def distance(self):
        """ Returns the distance, in miles, between this node and its parent.
        """
        if self.parent:
            return find_miles(self, self.parent) + self.parent.distance
        return 0.0

    @property
    def grade(self):
        """ Returns the grade of the climb between this node and its parent.
        """
        if self.parent:
            return 100 * self.rel_climb / find_dist(self, self.parent)
        return 0.0

    # For use in the following two properties, to minimize DB queries
    @property
    def shared_edge(self):
        """ Returns the edge shared between this node and its parent.
        """
        if self.parent:
            shared_edge = filter(lambda x: x in self.edges, self.parent.edges)
            if shared_edge:
                return shared_edge[0]
        return None

    @property
    def way_name(self):
        """ Returns street name from whence this node came,
        given that it has been assigned a parent node.
        """
        if self.shared_edge:
            return self.shared_edge.way_name
        return None

    @property
    def from_way(self):
        """ Returns ID of the way from whence this node came,
        given that it has been assigned a parent node.
        """
        if self.shared_edge:
            return self.shared_edge.way_id
        return None

    @property
    def way_nodes(self):
        """ Returns all the nodes along the way between this node
        and its parent node, given that it has been assigned a parent node.
        """
        mid_nodes = []
        if self.shared_edge:
            mid_node_list = self.shared_edge.edge_nodes
            for i in range(len(mid_node_list)):
                mid_nodes.append(
                    dbs.session.query(dbs.GNode).get(mid_node_list[i])
                )
            if self.shared_edge.end_b_id == self.id:
                # mid_node_list.reverse()
                mid_node_list = mid_node_list[::-1]
        return mid_nodes

    def h_value(self, end):
        """ Returns heuristic cost (distance) from here to the end, for A*.
        """
        miles_to_end = find_miles(self, end)
        return miles_to_end

    def i_value(self, start):
        """ Returns the inverse of the distance from start node to here,
        for the purposes of sending the pathfinder away from the beginning
        if it has not been assigned an end node to find.
        """
        inverse_distance = find_dist(self, start)
        if inverse_distance != 0:
            inverse_distance = 1 / inverse_distance
        return inverse_distance

    def is_in(self, other_set):
        """ Set comprehension, to quickly search for this node
        by original OSM ID (since two node objects could have been created
        from the same GIntersection from DB table) in a set.
        """
        if True in {self.id == o.id for o in other_set}:
            return True
        return False

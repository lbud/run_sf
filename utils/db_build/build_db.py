import xml.etree.ElementTree as ET

import sys
sys.path.append('..')
import dbs

# Parse initial input XML

file_to_parse = raw_input("file > ")
data_types = raw_input("nodes or ways? > ")

tree = ET.parse(file_to_parse)
root = tree.getroot()

def check_amenity(node):
    if node.findall('./tag[@k="amenity"]'):
        return True
    return False

def is_highway(way):
    return way.findall('./tag[@k="highway"]')

def foot_restricted(way):
    """
    Flags all ways I don't want to include
    """
    foot_rest = way.findall('./tag[@k="foot"][@v="no"]')    # foot-restricted
    is_motorway = way.findall('./tag[@k="highway"][@v="motorway"]')    # cars only
    is_motorway_link = way.findall('./tag[@k="highway"][@v="motorway_link"]')    # onramps
    is_service = way.findall('./tag[@k="highway"][@v="service"]')    # service roads
    service_2 = way.findall('./tag[@k="service"]')    # another service road tag
    access_no = way.findall('./tag[@k="access"][@v="no"]')    # no access
    access_private = way.findall('./tag[@k="access"][@v="private"]')    # private access
    is_sidewalk = way.findall('./tag[@k="footway"][@v="sidewalk"]')    # sidewalks -- proved problematic in testing
    is_steps = way.findall('./tag[@k="highway"][@v="steps"]')    # steps -- not ideal + typically connect to sidewalks
    no_sidewalk = way.findall('./tag[@k="sidewalk"][@v="no"]')    # steps -- not ideal + typically connect to sidewalks
    if (foot_rest or 
        is_motorway or 
        is_motorway_link or 
        is_service or 
        service_2 or
        access_no or 
        access_private or 
        is_sidewalk or 
        is_steps):
        return True
    return False

# To parse node files:
# Find all nodes;
# Check to see that they aren't amenity-tagged;
# Store nodes in nodes table.

if data_types == "nodes":
    node_list = root.findall('node')

    amenity_count = 0
    node_count = 0
    accepted_nodes = 0

    for node in node_list:
        node_count += 1
        if not check_amenity(node):
            accepted_nodes += 1
            n_id = node.attrib.get('id')
            n_lat = node.attrib.get('lat')
            n_lon = node.attrib.get('lon')
            n_elev = None
            dbs.store_node(n_id, n_lat, n_lon, n_elev)
        else:
            amenity_count += 1
    dbs.session.commit()

    print "amenities: ", amenity_count
    print "total nodes: ", node_count
    print "nodes added to db: ", accepted_nodes


# To parse way files:

if data_types == "ways":

    # Find all ways;
    # Check to see that it is tagged "highway" (all roads) and isn't one of the tags to exclude 
    #     (see foot_restricted above);
    # Find all the nodes the way contains;
    # Store all nodes therein in a dictionary in order to count node instances (to find intersections);

    intersections = {}
    for way in root.findall('way'):
        if is_highway(way) and not foot_restricted(way):
            for node in way.findall('./nd'):
                n_ref = node.attrib.get('ref')
                if not intersections.get(n_ref):
                    intersections[n_ref] = 1
                else:
                    intersections[n_ref] += 1

    # Iterate through the dictionary:
    # for those nodes that are seen more than once, consider them intersections, 
    # and store in intersections table;

    valid_ints = []

    for intersection in intersections.items():
        if intersection[1] > 1:
            valid_ints.append(intersection[0])
            i_id = intersection[0]
            i_ints = intersection[1]
            ## find intersection location from nodes table
            i_lat, i_lon = dbs.find_intersection(i_id)
            i_elev = None
            dbs.store_intersection(i_id, i_ints, i_lat, i_lon, i_elev)

    print "number of ints:", len(valid_ints)
    commit_1 = raw_input("commit ints? y/n >")
    if commit_1 == "y":
        dbs.session.commit()


    # To store edges:
    # Iterate over all ways;
    # If a way is indeed a highway and not one of the ways to exclude,
    # read street name and way ID,
    # build a dictionary with each way ID as key
    # and list of nodes it contains + its name as values;

    ways = {}
    for way in root.findall('way'):
        if is_highway(way) and not foot_restricted(way):
            w_id = way.attrib.get('id')
            nametag = way.find('./tag[@k="name"]')
            if nametag is not None:
                name = nametag.get('v')
            else:
                name = "None"
            ways[w_id] = []
            for node in way.findall('./nd'):
                ways[w_id].append(node.attrib.get('ref'))
            ways[w_id].append(name)

    # Keep unfinished_edges list to check later, just in case.
    # Read through nodes in each way in 'ways' dictionary;
    # For segments between each node contained that's considered an 'intersection,'
    # store this edge and relevant data (including contained nodes, for rendering) in edges table.

    unfinished_edges = []
    for way in ways.items():
        this_edge = []
        between_nodes = []
        way_id = way[0]
        intersections = way[1][:-1]
        way_name = way[1][-1]
        if way_name == "None":
            way_name = None

        for i in range(len(intersections)):

            if len(this_edge) == 1:
                if len(intersections[i]) > 0:
                    between_nodes.append(int(intersections[i]))

            if intersections[i] in valid_ints:
                this_edge.append(int(intersections[i]))
                if len(this_edge) == 2:
                    end_a = this_edge[0]
                    end_b = this_edge[-1]
                    between_nodes = between_nodes[:-1]
                    dbs.store_edge(way_id, way_name, end_a, end_b, between_nodes)
                    this_edge = this_edge[1:]
                    between_nodes = []

            if i == len(intersections) - 1 and not (intersections[i] in valid_ints):
                this_edge.append(intersections[i])
                unfinished_edges.append(this_edge)

    commit_2 = raw_input("commit edges? y/n >")
    if commit_2 == "y":
        dbs.session.commit()

import xml.etree.ElementTree as ET
import dbs

## parse initial input XML

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

############ NEW

def fix_oneway(something):
    pass




############ /endnew

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



if data_types == "ways":

    ## to get intersections
    intersections = {}
    for way in root.findall('way'):
        if is_highway(way) and not foot_restricted(way):
            for node in way.findall('./nd'):
                n_ref = node.attrib.get('ref')
                if not intersections.get(n_ref):
                    intersections[n_ref] = 1
                else:
                    intersections[n_ref] += 1

    valid_ints = []

    for intersection in intersections.items():
        if intersection[1] > 1:
            valid_ints.append(intersection[0])
            i_id = intersection[0]
            print i_id
            i_ints = intersection[1]
            ## find intersection location from nodes table
            i_lat, i_lon = dbs.find_intersection(i_id)
            i_elev = None
            dbs.store_intersection(i_id, i_ints, i_lat, i_lon, i_elev)
    dbs.session.commit()


    ## to get all ways with nodes
    ways = {}
    for way in root.findall('way'):
        if is_highway(way) and not foot_restricted(way):
            w_id = way.attrib.get('id')
            ways[w_id] = []
            for node in way.findall('./nd'):
                ways[w_id].append(node.attrib.get('ref'))


    unfinished_edges = []
    for way in ways.items():
        this_edge = []
        way_id = way[0]
        intersections = way[1]
        for i in range(len(intersections)):
            if intersections[i] in valid_ints:
                this_edge.append(intersections[i])
                if len(this_edge) == 2:
                    end_a = this_edge[0]
                    end_b = this_edge[1]
                    dbs.store_edge(way_id, end_a, end_b)
                    this_edge = this_edge[1:]
            if i == len(intersections) - 1 and not (intersections[i] in valid_ints):
                this_edge.append(intersections[i])
                unfinished_edges.append(this_edge)
    dbs.session.commit()
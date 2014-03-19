import xml.etree.ElementTree as ET
import urllib2
import save_data

loc_string = ""
url = ""
## parse initial input XML

# tree = ET.parse('map_full.osm')
# root = tree.getroot()

# ## initialize counters to check expected behavior

# result_count = 0
# node_count = len(root.findall('node'))
# amenity_count = len(root.findall('.//tag[@k="amenity"]'))
# num_locations = 0
# http_request_count = 0

# print "root nodes: ", node_count
# print "amenity nodes: ", amenity_count
# print "should have %d results" % (node_count - amenity_count)


## function definitions for HTTP requests

def encode_location(lat, lon):
    location = lat + "," + lon + "|"
    return location

def build_url(encoded_string):
    url_string = "http://maps.googleapis.com/maps/api/elevation/xml?locations=%s&sensor=false"
    return url_string % encoded_string

def get_elevations(url):
    response = urllib2.urlopen(url)
    xml = response.read()
    return xml

def parse_results(result_xml):
    r_root = ET.fromstring(result_xml)
    return r_root

def assign_elevations(orig_root, nodes, xml_root, result_count):
    this_index = 0
    for result in xml_root.iter('result'):
        result_count += 1
        elev = result.find('elevation').text
        this_node = orig_root.find("./node[@id=%r]"%nodes[this_index])
        this_node.set('elev', elev)
        this_index += 1
    return orig_root, result_count





## new

def build_loc_string(elem, xmap):
    global loc_string
    global result_count
    lat = elem.attrib.get('lat')
    lon = elem.attrib.get('lon')
    url_elem = encode_location(lat, lon)
    loc_string += url_elem
    if len(loc_string) > 1500:
        url = build_url(loc_string[:-1])
        r_xml = get_elevations(url)
        r_root = parse_results(r_xml)
        result_count = set_elevations(r_root, result_count)

def set_elevations(xml_root, result_count):
    global xmlmap
    this_index = 0
    for result in xml_root.iter('result'):
        result_count += 1
        elev = result.find('elevation').text
        this_node = xmlmap.get(this_index)
        this_node.set('elev', elev)
        this_index += 1
    xmlmap = {}
    return result_count
## parse XML

## containers for each HTTP request
# locations = ""
# these_ids = []



## iterate over each node
xmlmap = {}
nodes = 0
not_amenity = 0
yes_amenity = 0
result_count = 0

this_index = 0
for event, elem in ET.iterparse('map_sample.osm', events=('start', 'start-ns', 'end-ns')):
    if elem.tag == 'node':
        nodes += 1
        children = elem.getchildren()
        if not elem.findall('./tag[@k="amenity"]'):
            not_amenity += 1
            xmlmap[this_index] = elem
            this_index += 1
            build_loc_string(elem, xmlmap)
            # set_elevations(r_root, result_count)
        else:
            pass
    # elem.clear()

print "all nodes:", nodes
print "good nodes:", not_amenity
print "amenity nodes:", yes_amenity



    # tag = elem.tag
    # id = elem.attrib.get('id')
    # lat = elem.attrib.get('lat')
    # lon = elem.attrib.get('lon')
    # if not xmlmap.get(tag):
    #     xmlmap[tag] = {id: (lat, lon)}
    # else:
    #     xmlmap[tag][id] = (lat, lon)





# node_list = root.findall('node')

# print "getting elevation data....."
# for i in range(len(node_list)):

#     node = node_list[i]
    
#     ## encode locations
#     lat = node.attrib.get('lat')
#     lon = node.attrib.get('lon')
#     next = encode_location(lat, lon)
    
#     ## amenity nodes won't be referenced in ways
#     found_amenity = node.findall('./tag[@k="amenity"]')
    
#     if not found_amenity:

#         ## building encoded query strings
#         these_ids.append(node.attrib.get('id'))
#         locations += next
#         num_locations += 1

#         ## at length, stop building
#         if len(locations) + len(next) > 1500 or i == len(node_list)-1:
#             ## HTTP request
#             url = build_url(locations[:-1])
#             r_xml = get_elevations(url)
#             r_root = parse_results(r_xml)

#             http_request_count += 1

#             ## append elevations to root
#             root, result_count = assign_elevations(root, these_ids, r_root, result_count)
            
#             ## reset HTTP request containers for next batch
#             these_ids = []
#             locations = ""

# ## check final results against original expected counts
# print "num of locations given: ", num_locations
# print "num of results: ", result_count

# if num_locations == result_count:
#     for node in node_list:
#         n_id = node.attrib.get('id')
#         n_lat = node.attrib.get('lat')
#         n_lon = node.attrib.get('lon')
#         n_elev = node.attrib.get('elev')
#         save_data.store_node(n_id, n_lat, n_lon, n_elev)
#     save_data.session.commit()
# else:
#     print "result count does not match expected count. something might be wrong here"





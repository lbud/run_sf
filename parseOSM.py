import xml.etree.ElementTree as ET
import urllib2

## parse initial input XML

tree = ET.parse('map_sample.osm')
root = tree.getroot()


## initialize counters to check expected behavior

result_count = 0
node_count = len(root.findall('node'))
amenity_count = len(root.findall('.//tag[@k="amenity"]'))
num_locations = 0
http_request_count = 0

print "root nodes: ", node_count
print "amenity nodes: ", amenity_count
print "should have %d results" % (node_count - amenity_count)


## function definitions for HTTP requests

def encode_location(lat, long):
    location = lat + "," + long + "|"
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


## parse XML

## containers for each HTTP request
locations = ""
these_ids = []

node_list = root.findall('node')

print "getting elevation data....."
for i in range(len(node_list)):

    node = node_list[i]
    
    ## encode locations
    lat = node.attrib.get('lat')
    lon = node.attrib.get('lon')
    next = encode_location(lat, lon)
    
    ## amenity nodes won't be referenced in ways
    found_amenity = node.findall('./tag[@k="amenity"]')
    
    if not found_amenity:

        ## building encoded query strings
        these_ids.append(node.attrib.get('id'))
        locations += next
        num_locations += 1

        ## at length, stop building
        if len(locations) + len(next) > 1500 or i == len(node_list)-1:
            ## HTTP request
            url = build_url(locations[:-1])
            r_xml = get_elevations(url)
            r_root = parse_results(r_xml)

            http_request_count += 1

            ## append elevations to root
            root, result_count = assign_elevations(root, these_ids, r_root, result_count)
            
            ## reset HTTP request containers for next batch
            these_ids = []
            locations = ""

## check final results against original expected counts
print "num of locations given: ", num_locations
print "num of results: ", result_count

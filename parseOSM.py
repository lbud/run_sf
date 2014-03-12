import xml.etree.ElementTree as ET
import urllib2

tree = ET.parse('map_sample.osm')
root = tree.getroot()

# for node in root.iter('node'):
    # points[(node.attrib.get('lon'), node.attrib.get('lat'))] = 0


## setting an elevation attribute
# for node in root.iter('node'):
#     node.set('elev', 0)
#     print node.attrib.get('lon'), node.attrib.get('lat'), node.attrib.get('elev')
#     print node.attrib

loc_strings = []
locations = ""
# loc_str_lengths = []
# loc_count = 0 # can del later

## function definitions for building HTTP requests

def encode_location(lat, long):
    location = lat + "," + long + "|"
    return location

def build_urls(encoded_strings):
    url_list = []
    url_string = "http://maps.googleapis.com/maps/api/elevation/xml?locations=%s&sensor=false"
    for enc_str in encoded_strings:
        url_list.append(url_string % enc_str)
    return url_list



## parse XML

for node in root.iter('node'):
    next = encode_location(node.attrib.get('lat'), node.attrib.get('lon'))
    # print root.findall("./[@tag=")
    found_amenity = node.findall('.//tag[@k="amenity"]')
    if not found_amenity:
        if len(locations) + len(next) < 1800:
            locations += next
            # loc_count += 1 # can del later
        else:
            # loc_str_lengths.append(len(locations))
            loc_strings.append(locations[:-1])
            locations = ""

# print loc_count # can del later
# print loc_strings

url_strings = build_urls(loc_strings)

for u_s in url_strings:
    print u_s

print len(url_strings)

# response = urllib2.urlopen(url_strings[0])
# html = response.read()

# r_tree = ET.parse(html)
# r_root = r_tree.getroot()
# print "r_root", r_root

# for result in r_root.iter('result'):
#     print result.attrib.get('lat')
#     print result.attrib.get('lng')
#     print result.attrib.get('elevation')

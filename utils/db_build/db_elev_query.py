import urllib2
import xml.etree.ElementTree as ET

import sys
sys.path.append('..')
import dbs

intersections = dbs.session.query(dbs.GIntersection).all()


## function definitions for HTTP calls

# encode locations for urls
def encode_location(lat, lon):
    location = str(lat) + "," + str(lon) + "|"
    return location

# google elevation API requests
def build_url(encoded_string):
    url_string = "http://maps.googleapis.com/maps/api/elevation/xml?locations=%s&sensor=false"
    return url_string % encoded_string

# read XML response
def get_elevations(url):
    response = urllib2.urlopen(url)
    xml = response.read()
    return xml

# parse data into readable xml from root
def parse_results(result_xml):
    r_root = ET.fromstring(result_xml)
    return r_root

# assign elevations from parsed XML to sqlalchemy objects
def assign_elevations(xml_root, i_data):
    this_index = 0
    for result in xml_root.iter('result'):
        elev = result.find('elevation').text
        i_data[this_index].elev = elev
        this_index += 1
    return i_data


## initialize empty containers for HTTP requests

locations = ""
query_set = []

for i in range(len(intersections)):
    x = intersections[i]
    next = encode_location(x.lat, x.lon)
    locations += next
    query_set.append(x)

    ## construct HTTP request for strings approaching max length
    if len(locations) + len(next) > 1500 or i == len(intersections)-1:

        ## build URLs, get XML data
        url = build_url(locations[:-1])
        r_xml = get_elevations(url)
        r_root = parse_results(r_xml)

        ## assign elevations back Intersection objects
        assign_elevations(r_root, query_set)

        ## reset containers for next request
        query_set = []
        locations = ""

committing = raw_input("commit? y/n > ")
if committing == "y":
    dbs.session.commit()
import urllib2
import xml.etree.ElementTree as ET

if __name__ == '__main__' and __package__ is None:
    from os import path
    import sys
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import dbs

# This file only requests elevation data for intersections, not all nodes, due
# to Google API limit.

intersections = dbs.session.query(dbs.GIntersection).all()


# Function definitions for HTTP calls:

def encode_location(lat, lon):
    """ Encode locations for URLs """
    location = str(lat) + "," + str(lon) + "|"
    return location


def build_url(encoded_string):
    """ Google Elevation API request strings """
    url_string = (
        "http://maps.googleapis.com/maps/api/elevation/xml?"
        "locations=%s&sensor=false"
    )
    return url_string % encoded_string


def get_elevations(url):
    """ Read XML response from elevation request """
    response = urllib2.urlopen(url)
    xml = response.read()
    return xml


def parse_results(result_xml):
    """ Parse data into readable XML from root """
    r_root = ET.fromstring(result_xml)
    return r_root


def assign_elevations(xml_root, i_data):
    """
    For assigning elevations from parsed XML to SQLAlchemy intersection objects
    """
    this_index = 0
    for result in xml_root.iter('result'):
        elev = result.find('elevation').text
        i_data[this_index].elev = elev
        this_index += 1
    return i_data


# Initialize empty containers for HTTP requests

locations = ""
query_set = []

for i in range(len(intersections)):
    x = intersections[i]
    next = encode_location(x.lat, x.lon)
    locations += next
    query_set.append(x)

    # Construct HTTP request for strings approaching max length
    if len(locations) + len(next) > 1500 or i == len(intersections)-1:

        # Build URLs, get XML data
        url = build_url(locations[:-1])
        r_xml = get_elevations(url)
        r_root = parse_results(r_xml)

        # Assign elevations back to intersection objects
        assign_elevations(r_root, query_set)

        # Reset containers for next request
        query_set = []
        locations = ""

committing = raw_input("commit? y/n > ")
if committing == "y":
    dbs.session.commit()

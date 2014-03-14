import xml.etree.ElementTree as ET
import save_data

## parse initial input XML

file_to_parse = raw_input("file > ")

tree = ET.parse(file_to_parse)
root = tree.getroot()

def check_amenity(node):
    if node.findall('./tag[@k="amenity"]'):
        return True
    else:
        return False

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
        # n_elev = node.attrib.get('elev')
        n_elev = None
        save_data.store_node(n_id, n_lat, n_lon, n_elev)
    else:
        amenity_count += 1
save_data.session.commit()

print "amenities: ", amenity_count
print "total nodes: ", node_count
print "nodes added to db: ", accepted_nodes
import pytest
from models import Node, Route
import utils.dbs as dbs

@pytest.fixture
def route(start_loc, dist):
    route = Route(start_loc, dist)
    return route

route = route((37.785805, -122.424427), 2)

def test_route_init():
    assert route is not None

def test_route_exists():
    assert route.path is not None

def test_starts_and_ends():
    assert route.full_node_path[0].lat == route.full_node_path[-1].lat
    assert route.full_node_path[0].lon == route.full_node_path[-1].lon    

def test_route_moves():
    for i in range(1,len(route.full_node_path)):
        assert route.full_node_path[i].lat != route.full_node_path[i-1].lat
        assert route.full_node_path[i].lon != route.full_node_path[i-1].lon

def test_route_length():
    route_distance = route.route_distance
    acceptable_range = [(route_distance - (route_distance * .4)),
                        (route_distance + (route_distance * .4))]
    assert route.distance > acceptable_range[0]
    assert route.distance < acceptable_range[1]

def test_route_data_types():
    assert type(route) == Route
    for n in route.full_node_path:
        assert type(n) == Node or type(n) == dbs.GNode

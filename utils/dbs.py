from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, ForeignKey, func
from sqlalchemy import Column, Integer, Float, BigInteger, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import sessionmaker, scoped_session, relationship, backref
from geoalchemy2 import Geometry, WKTElement
# from config import DB_URI



ENGINE = create_engine("postgres://lbudorick@localhost/run", echo=False)
session = scoped_session(sessionmaker(bind=ENGINE,
                                      autocommit=False,
                                      autoflush=False))

Base = declarative_base()
Base.query = session.query_property()

class GNode(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True)
    lat = Column(Float)
    lon = Column(Float)
    elev = Column(Float, nullable=True)


class GEdge(Base):
    __tablename__ = "edges"

    id = Column(Integer, primary_key=True)
    way_id = Column(BigInteger)
    way_name = Column(String(50))
    end_a_id = Column(BigInteger)#, ForeignKey('intersections.id'))
    end_b_id = Column(BigInteger)#, ForeignKey('intersections.id'))
    edge_nodes = Column(ARRAY(BigInteger))

    # ends = relationship("GIntersection", uselist=True, primaryjoin="or_(GEdge.end_a_id==GIntersection.id, "
    #                                                 "GEdge.end_b_id==GIntersection.id)",
    #                             backref="ends" )


class GIntersection(Base):
    __tablename__ = "intersections"
    id = Column(BigInteger, primary_key=True)
    ints = Column(Integer)
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)
    loc = Column(Geometry(geometry_type='POINT', srid=4326))
    elev = Column(Float, nullable=True)

    # edges = relationship("GEdge", primaryjoin="or_(GIntersection.id==GEdge.end_a_id, "
    #                                         "GIntersection.id==GEdge.end_b_id)",
    #                              backref="edges" )

def coords_tuple(n):
    location = session.query(func.ST_AsLatLonText(n.loc,'D.DDDDDDD')).first()[0].split()
    tup = ( float(location[0]), float(location[1]) )
    return tup

def store_node(id, lat, lon, elev):
    n = GNode(id=id, lat=lat, lon=lon, elev=elev)
    session.add(n)
    return None

def store_intersection(id, ints, lat, lon, elev):
    loc = 'POINT(%r %r)' % (lon,lat)
    i = GIntersection(id=id, ints=ints, lat=lat, lon=lon, loc=WKTElement(loc,srid=4326), elev=elev)
    session.add(i)
    return None

def store_edge(way_id, way_name, end_a, end_b, edge_nodes):
    e = GEdge(way_id=way_id, way_name=way_name, end_a_id=end_a, end_b_id=end_b, edge_nodes=edge_nodes)
    session.add(e)
    return None

def find_intersection(id):
    node = session.query(GNode).get(id)
    if node:
        return node.lat, node.lon
    return None

def base_make(en):
    if en=="postgres":
        Base.metadata.create_all(ENGINE)
    else:
        print "no"
    return None

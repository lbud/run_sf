from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Integer, Float, BigInteger
from sqlalchemy.orm import sessionmaker, scoped_session, relationship, backref
from geoalchemy2 import Geometry, Geography, WKTElement
from pymongo import MongoClient, GEO2D
from bson.objectid import ObjectId
from bson.son import SON
import config

###
### SQLITE
###

ENGINE = create_engine("sqlite:///mapdata.db", echo=False) #, connect_args={'check_same_thread':False})
session = scoped_session(sessionmaker(bind=ENGINE,
                                      autocommit=False,
                                      autoflush=False))

pg_engine = create_engine("postgres://lbudorick@localhost/run_sf", echo=False)
pg_session = scoped_session(sessionmaker(bind=pg_engine,
                                        autocommit=False,
                                        autoflush=False))

Base = declarative_base()
Base.query = session.query_property()

Base2 = declarative_base()
Base2.query = pg_session.query_property()


class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True)
    lat = Column(Float)
    lon = Column(Float)
    elev = Column(Float, nullable=True)


class Edge(Base):
    __tablename__ = "edges"

    id = Column(Integer, primary_key=True)
    way_id = Column(Integer)
    end_a_id = Column(BigInteger, ForeignKey('intersections.id'))
    end_b_id = Column(BigInteger, ForeignKey('intersections.id'))

    ends = relationship("Intersection", uselist=True, primaryjoin="or_(Edge.end_a_id==Intersection.id, "
                                                    "Edge.end_b_id==Intersection.id)",
                                backref="ends" )


class Intersection(Base):
    __tablename__ = "intersections"
    id = Column(BigInteger, primary_key=True)
    ints = Column(Integer)
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)
    elev = Column(Float, nullable=True)

    edges = relationship("Edge", primaryjoin="or_(Intersection.id==Edge.end_a_id, "
                                            "Intersection.id==Edge.end_b_id)",
                                 backref="edges" )



class GNode(Base2):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True)
    loc = Column(Geography(geometry_type='POINT', srid=4326))
    elev = Column(Float, nullable=True)


class GEdge(Base2):
    __tablename__ = "edges"

    id = Column(Integer, primary_key=True)
    way_id = Column(Integer)
    end_a_id = Column(BigInteger, ForeignKey('intersections.id'))
    end_b_id = Column(BigInteger, ForeignKey('intersections.id'))

    ends = relationship("GIntersection", uselist=True, primaryjoin="or_(GEdge.end_a_id==GIntersection.id, "
                                                    "GEdge.end_b_id==GIntersection.id)",
                                backref="ends" )


class GIntersection(Base2):
    __tablename__ = "intersections"
    id = Column(BigInteger, primary_key=True)
    ints = Column(Integer)
    loc = Column(Geometry(geometry_type='POINT', srid=4326))
    elev = Column(Float, nullable=True)

    edges = relationship("GEdge", primaryjoin="or_(GIntersection.id==GEdge.end_a_id, "
                                            "GIntersection.id==GEdge.end_b_id)",
                                 backref="edges" )





def store_node(id, lat, lon, elev):
    n = Node(id=id, lat=lat, lon=lon, elev=elev)
    pg_session.add(n)
    ## not committing here so as to be able to add entire list at once
    return None

def store_intersection(id, ints, lat, lon, elev):
    i = Intersection(id=id, ints=ints, lat=lat, lon=lon, elev=elev)
    pg_session.add(i)
    return None

def store_edge(way_id, end_a, end_b):
    e = Edge(way_id=way_id, end_a_id=end_a, end_b_id=end_b)
    pg_session.add(e)
    return None

def base_make(en):
    if en=="sqlite":
        Base.metadata.create_all(ENGINE)
    if en=="postgres":
        Base2.metadata.create_all(pg_engine)
    else:
        print "no"
    return None


###
### MONGODB
###

mdb = MongoClient().intersections

mdb.nodes.create_index([("loc", GEO2D)])

nodes = mdb["nodes"]

def mongo_migrate():
    """ Stores intersections from sqlite db in mongodb """
    int_query = session.query(Intersection).all()
    ints = []
    for i in int_query:
        node_id = i.id
        lat = i.lat
        lon = i.lon
        ints.append({"node_id": node_id, "loc": [lat, lon]})
    dbs.nodes.insert(ints)

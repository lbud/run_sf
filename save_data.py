from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Integer, Float
from sqlalchemy.orm import sessionmaker, scoped_session, relationship, backref

ENGINE = create_engine("sqlite:///mapdata.db", echo=False)
session = scoped_session(sessionmaker(bind=ENGINE,
                                      autocommit=False,
                                      autoflush=False))

Base = declarative_base()
Base.query = session.query_property()


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
    end_a_id = Column(Integer, ForeignKey('intersections.id'))
    end_b_id = Column(Integer, ForeignKey('intersections.id'))

    ends = relationship("Intersection", uselist=True, primaryjoin="or_(Edge.end_a_id==Intersection.id, "
                                                    "Edge.end_b_id==Intersection.id)",
                                backref="ends" )


class Intersection(Base):
    __tablename__ = "intersections"
    id = Column(Integer, primary_key=True)
    ints = Column(Integer)
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)
    elev = Column(Float, nullable=True)

    edges = relationship("Edge", primaryjoin="or_(Intersection.id==Edge.end_a_id, "
                                            "Intersection.id==Edge.end_b_id)",
                                 backref="edges" )



def store_node(id, lat, lon, elev):
    n = Node(id=id, lat=lat, lon=lon, elev=elev)
    session.add(n)
    ## not committing here so as to be able to add entire list at once
    return None

def store_intersection(id, ints, lat, lon, elev):
    i = Intersection(id=id, ints=ints, lat=lat, lon=lon, elev=elev)
    session.add(i)
    return None

def store_edge(way_id, end_a, end_b):
    e = Edge(way_id=way_id, end_a=end_a, end_b=end_b)
    session.add(e)
    return None

def find_intersection(id):
    node = session.query(Node).get(id)
    lat = node.lat
    lon = node.lon
    return lat, lon

def base_make():
    Base.metadata.create_all(ENGINE)
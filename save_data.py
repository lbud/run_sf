from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, scoped_session, relationship, backref
from operator import itemgetter

ENGINE = create_engine("sqlite:///mapdata.db", echo=False)
session = scoped_session(sessionmaker(bind=ENGINE,
                                      autocommit=False,
                                      autoflush=False))

Base = declarative_base()
Base.query = session.query_property()
# Base.metadata.create_all(ENGINE)

class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True)
    lat = Column(Float)
    lon = Column(Float)
    elev = Column(Float, nullable=True)

# class Way(Base):
#     __tablename__ = "ways"

#     ## 
#     ## finish defining way cols
#     ##

def store_node(id, lat, lon, elev):
    n = Node(id=id, lat=lat, lon=lon, elev=elev)
    session.add(n)
    ## not committing here so as to be able to add entire list at once
    return None


def store_ways():
    pass
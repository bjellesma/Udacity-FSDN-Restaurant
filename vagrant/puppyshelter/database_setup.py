import sys
#for data types
from sqlalchemy import Column, ForeignKey, Integer, String, Date, Enum, Numeric
#for connecting
from sqlalchemy.ext.declarative import declarative_base
#for ForeignKey relationships
from sqlalchemy.orm import relationship
#for use at the end of the configuration file
from sqlalchemy import create_engine

Base = declarative_base()

"""
The restaurant class is designed to inherit from Base
"""
class Shelter(Base):
    #__tablename__ is special in sqlalchemy to let python know the variablename we will use for tables
    __tablename__ = 'shelter'
    id = Column(Integer, primary_key = True)
    name = Column(String(80), nullable = False)
    address = Column(String(250))
    city = Column(String(80))
    state = Column(String(20))
    zipCode = Column(String(10))
    website = Column(String)

"""
The MenuItem class is designed to inherit from Base
"""
class Puppy(Base):
    __tablename__ = 'puppy'
    id = Column(Integer, primary_key = True)
    name = Column(String(250), nullable = False)
    dateOfBirth = Column(Date)
    gender = Column(Enum('male', 'female'))
    weight = Column(Numeric(10))
    picture = Column(String)
    shelter_id = Column(Integer, ForeignKey('shelter.id'))
    #creating the reference for the ForeignKey to use
    shelter = relationship(Shelter)

#end of file wrap up
engine = create_engine('sqlite:///puppyshelter.db')
#adds the class to the db
Base.metadata.create_all(engine)

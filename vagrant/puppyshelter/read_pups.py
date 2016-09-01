from sqlalchemy import create_engine, asc
#we need sessionmaker in order to perform queries
from sqlalchemy.orm import sessionmaker
#importing previously made files
from database_setup import Base, Shelter, Puppy
#creating sqlite3 engine
engine = create_engine('sqlite:///puppyshelter.db')
#connecting to db file
Base.metadata.bind = engine
#starting session with engine
DBSession = sessionmaker(bind = engine)
#creating instance of DBsession
session = DBSession()

puppys = session.query(Puppy).order_by(asc('name')).all()
print ''
print 'All puppies sorted alphabetically'
print '______'
for puppy in puppys:
    print puppy.name

puppys = session.query(Puppy).order_by(asc('dateOfBirth')).filter('dateOfBirth' > 2016-01-01).all()
print ''
print 'All puppies less than 6 months old'
print '______'
for puppy in puppys:
    print puppy.name

puppys = session.query(Puppy).order_by(asc('weight')).all()
print ''
print 'All puppies sorted by weight'
print '______'
for puppy in puppys:
    print puppy.name

puppys = session.query(Puppy).group_by('shelter_id').all()
print ''
print 'All puppies grouped by shelter'
print '______'
for puppy in puppys:
    print puppy.name

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///student.db', echo=True)
Base = declarative_base()
_SessionFactory = sessionmaker(bind=engine)

def session_factory():
    Base.metadata.create_all(engine)
    return _SessionFactory()
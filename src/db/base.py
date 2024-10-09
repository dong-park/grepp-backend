from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

def import_models():
    from src.models import User, Reservation
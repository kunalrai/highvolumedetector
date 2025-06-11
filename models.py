import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv()

# Create base class for declarative models
Base = declarative_base()

class FuturesPair(Base):
    __tablename__ = 'futures_pairs'

    pair = Column(String, primary_key=True)
    kind = Column(String)
    status = Column(String)
    tick_size = Column(Float)
    price_band_upper = Column(String)

    def __repr__(self):
        return f"<FuturesPair(pair='{self.pair}', kind='{self.kind}', status='{self.status}')>"

# Create database engine using environment variable
engine = create_engine(os.getenv('DATABASE_URL', 'sqlite:///futures.db'))

# Create tables
Base.metadata.create_all(engine)

# Create session factory
Session = sessionmaker(bind=engine)

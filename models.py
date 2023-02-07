from sqlalchemy import create_engine, Column, Integer, String, Date, update, table
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_engine('sqlite:///inventory.db', echo=False)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


def __repr__(self):
    return f'<Product Name: {self.product_name} Price: {self.product_price} Quantity: {self.product_quantity} Date Updated: {self.date_updated}>'


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    product_name = Column('Product Name', String, unique=True)
    product_price = Column('Price', Integer)
    product_quantity = Column('Quantity', Integer)
    date_updated = Column('Date Updated', Date)

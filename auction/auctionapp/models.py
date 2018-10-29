from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Integer, String, Text, Binary, Column, Float
from zope.sqlalchemy import ZopeTransactionExtension

# DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
DB_URI = 'sqlite:///stuff2.db'

Session = sessionmaker(autocommit=False,
                       autoflush=False,
                       bind=create_engine(DB_URI))
session = scoped_session(Session)
Base = declarative_base()


class Bid(Base):

    __tablename__ = 'bid'

    id      	 = Column(Integer, primary_key=True)
    code 		 = Column(String(50))
    created_at   = Column(String(50))
    created_by   = Column(String(50))
    quantity     = Column(Float(precision=4, asdecimal=True))
    price 		 = Column(Float(precision=4, asdecimal=True))

    def __init__(self, code, created_at ,created_by, quantity, price):

        self.code = code
        self.created_at = created_at
        self.created_by = created_by
        self.quantity = quantity
        self.price = price

    @classmethod
    def from_json(cls, data):
        return cls(**data)

    def to_json(self):
        to_serialize = ['id', 'code', 'created_at', 'created_by', 'quantity', 'price']
        d = {}
        for attr_name in to_serialize:
            d[attr_name] = getattr(self, attr_name)
        return d


# creates database
if __name__ == "__main__":
    print('in main', DB_URI)
    engine = create_engine(DB_URI)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
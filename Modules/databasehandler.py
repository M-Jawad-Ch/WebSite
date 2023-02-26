from sqlalchemy import create_engine, Column, String, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
from re import sub

Base = declarative_base()
engine = None

def title_parser(title:str) -> str:
    s = sub(r'[^a-z\s]','',title.lower())
    return sub(r'\s','-',s)

class Post(Base):
    __tablename__ = 'posts'

    url = Column('url', String, primary_key=True)
    title = Column("title", String)
    body = Column("body", String)
    owner = Column('owner', String)

    def __init__(self, title, body, owner) -> None:
        self.url = title_parser(title)
        self.title = title
        self.body = body
        self.owner = owner
    
    def __repr__(self):
        return f'({self.title}) {self.body}'

class User(Base):
    __tablename__ = 'users'

    uname = Column('uname', String, primary_key=True)
    name = Column('name', String)
    password = Column('password', String)
    admin = Column('admin', Boolean)

    def __init__(self, uname, name, password, isAdmin = False) -> None:
        self.uname = uname
        self.name = name
        self.password = password
        self.admin = isAdmin
    
    def __repr__(self):
        return f'({self.uname}) {self.name}'

def get_session(dbname):
    engine = create_engine(f"sqlite:///{dbname}")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    return Session()

class DbHandler():
    def __init__(self, dbname) -> None:
        self.sess = get_session(dbname)
    
    def insert(self, val) -> None:
        self.sess.add(val)
        self.sess.commit()
    
    def delete(self, key:str, type) -> None:
        val = self.get(key, type)
        
        self.sess.delete(val)
        self.sess.commit()
    
    def update(self, key:str, val, type) -> None:
        prev = self.get(key, type)

        self.sess.delete(prev)
        self.sess.add(val)
        self.sess.commit()
    
    def get(self, key:str, type) -> type:
        return self.sess.get(type, key)
    
    def get_all(self, type) -> list:
        return self.sess.query(type).all()
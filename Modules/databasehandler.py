from sqlalchemy import create_engine, Column, String
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

    def __init__(self, title, body) -> None:
        self.url = title_parser(title)
        self.title = title
        self.body = body
    
    def __repr__(self):
        return f'({self.title}) {self.body}'

def get_session(dbname):
    engine = create_engine(f"sqlite:///{dbname}")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    return Session()

class DbHandler():
    def __init__(self, dbname) -> None:
        self.sess = get_session(dbname)
    
    def insert(self, post:Post) -> None:
        self.sess.add(post)
        self.sess.commit()
    
    def delete(self, key:str) -> None:
        post = self.get(key)
        self.sess.delete(post)
        self.sess.commit()
    
    def update(self, key:str, post:Post) -> None:
        prev = self.get(key)
        self.sess.delete(prev)
        self.sess.add(post)
        self.sess.commit()
    
    def get(self, key:str) -> Post:
        return self.sess.get(Post, key)
    
    def get_all(self) -> list:
        return self.sess.query(Post).all()
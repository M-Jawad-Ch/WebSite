from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = None

class Post(Base):
    __tablename__ = 'posts'

    title = Column("title", String, key=True, unique=True)
    body = Column("body", String)

    def __init__(self, title, body) -> None:
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
        q = self.sess.query(Post).filter(Post.title == key)
        return [ x for x in q ][0]
    
    def update_title(self, key:str, new_title:str) -> None:
        post = self.get(key)
        post.title = new_title
        self.update(key, post)
    
    def get_all(self) -> list:
        return self.sess.query(Post).all()
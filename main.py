import os
import cherrypy
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('templates'))

cherrypy.config.update({'server.socket_host': '0.0.0.0',
                        'server.socket_port': 8080,
                       })
                    
engine = create_engine('mysql+pymysql://root:abc@172.20.0.2/fifa_players')

Session = sessionmaker(bind=engine)

Base = declarative_base()

class Author(Base):
    __tablename__ = "author"
    author_id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)

    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name

    def __repr__(self):
      return "fname=%s,lname=%s" %(self.first_name, self.last_name)


class Root(object):

    @cherrypy.expose
    def index(self):
      session = Session()
      authors = session.query(Author).all()
      print(authors)
      tmpl = env.get_template('index.html')
      return tmpl.render()
    
    @cherrypy.expose
    def search(self, q=None):
      if q:
        return 'Working'
      else:
        return 'Not Working'

    @cherrypy.expose
    def build_team(self, budget=None):
      if budget:
        return 'Working'
      else:
        return 'Not Working'

if __name__ == '__main__':
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './static'
        }
    }
    cherrypy.quickstart(Root(), '/', conf)
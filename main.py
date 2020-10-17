import os
import cherrypy
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('templates'))

cherrypy.config.update({'server.socket_host': '0.0.0.0',
                        'server.socket_port': 8080,
                       })

Base = automap_base()

engine = create_engine('mysql+pymysql://root:abc@172.20.0.2/fifa_players')

Base.prepare(engine, reflect=True)

Player = Base.classes.task

session = Session(engine)

class Root(object):

    @cherrypy.expose
    def index(self, q=None, budget=None):
      page_index=1
      page_size=session.query(func.count(Player.ID)).scalar()
      print("Page SIZE = ",page_size)
      players = session.query(Player.Name, Player.Age, Player.Nationality, Player.Club, Player.Photo, Player.Overall, Player.Value).filter().order_by(Player.ID).offset((page_index-1) *page_size).limit(page_size).all()
      # print(players[0].Name)
      tmpl = env.get_template('index.html')
      return tmpl.render(players=players)
    
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
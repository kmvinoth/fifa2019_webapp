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
    def index(self, Name=None, Club=None, Nationality=None, budget=None):

      request_params = cherrypy.request.params

      if not request_params:
        page_index=1
        page_size=100
        # players = session.query(Player.Name, Player.Age, Player.Nationality, Player.Club, Player.Photo, Player.Overall, Player.Value).filter().order_by(Player.ID).offset((page_index-1) *page_size).limit(page_size).all()
        players = session.query(Player).order_by(Player.ID).offset((page_index-1) *page_size).limit(page_size).all()
        tmpl = env.get_template('index.html')
        return tmpl.render(players=players)
      else:
        query = session.query(Player)
        for attr,value in request_params.items():
          # print(attr,value)
          if value is not '':
            query = query.filter( getattr(Player,attr).like("%%%s%%" % value))
        players = query.all()
        # print("PLAYERS=", players)
        tmpl = env.get_template('index.html')
        return tmpl.render(players=players,search=True)

      # players = session.query().filter_by(Name=name,Club=club,Nationality=nationality).all()

      # print("Player Name = ",players)

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
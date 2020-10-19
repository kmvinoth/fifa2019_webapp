import os
import cherrypy
# from sqlalchemy import Column, Integer, String, create_engine
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from decouple import config

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import secure
from secure import SecureHeaders
import team_build
import traceback
import re

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

    # @cherrypy.expose
    # def set_secure_cookie(self):
    #     response_headers = cherrypy.response.headers
    #     SecureCookie.cherrypy(response_headers, name="cherrypy", value="ABC123", samesite=False)
    #     return "Secure"

    @cherrypy.expose
    def index(self, Name=None, Club=None, Nationality=None, Budget=None):

      # response_headers = cherrypy.response.headers
      # secure.SecureCookie.cherrypy(response_headers, name="cherrypy", value="ABC123", samesite=False, secure=True)

      request_params = cherrypy.request.params
      query = session.query(Player)

      if not request_params:
        page_index=1
        page_size=5
        # players = session.query(Player.Name, Player.Age, Player.Nationality, Player.Club, Player.Photo, Player.Overall, Player.Value).filter().order_by(Player.ID).offset((page_index-1) *page_size).limit(page_size).all()
        players = query.order_by(Player.ID).offset((page_index-1) *page_size).limit(page_size).all()
        tmpl = env.get_template('index.html')
        return tmpl.render(players=players)
      
      if 'Budget' in request_params.keys():
        
        budget_tmpl = env.get_template('index.html')
        
        budget = request_params.get('Budget')
        
        if not budget:
          return budget_tmpl.render(message_error="message_error",team_builder=True)
        try:

            budget = re.sub("[^0-9]", "", budget)

            budget = int(budget)

            min_budget = 1000000

            max_budget = 1000000000

            if budget > min_budget and budget < max_budget: 

              team_builder = team_build.team_builder(budget, FB=2, HB=3, FR=5, GK_coef=0.05, FB_coef=0.15, HB_coef=0.30, FR_coef=0.50 )

              if team_builder is not None:

                team = team_builder['team']

                best_team_ids = [player.get('ID') for player in team]

                query_results = query.filter(Player.ID.in_(best_team_ids))
            
                team = query_results.all()
                print("TEAM = ", team_builder)
                return budget_tmpl.render(players=team, budget=budget, team_builder=True)
              else:
                return budget_tmpl.render(message_none = "message_none", budget=budget, team_builder=True)
            else:
              return budget_tmpl.render(message_budget = "message_budget" , budget=budget, team_builder=True)
        except :
          traceback.print_exc() 
          return budget_tmpl.render(message_traceback="message_traceback",team_builder=True)
      else:

        for attr,value in request_params.items():
          # print(attr,value)
          if value is not '':
            query = query.filter( getattr(Player,attr).like("%%%s%%" % value))
        players = query.all()
        # print("PLAYERS=", players)
        tmpl = env.get_template('index.html')
        return tmpl.render(players=players,search=True)

if __name__ == '__main__':
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd()),
            'tools.response_headers.on': True,
            'tools.response_headers.headers': SecureHeaders.cherrypy()
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './static'
        }
    }
    cherrypy.quickstart(Root(), '/', conf)
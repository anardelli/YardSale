import decimal
import logging
import os

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required
from google.appengine.ext.webapp.util import run_wsgi_app

import model
import paypal

class Home(webapp.RequestHandler):
  def get(self):
    data = { 'items': model.Item.all() }
    path = os.path.join(os.path.dirname(__file__), 'templates/main.htm')
    self.response.out.write(template.render(path, data))

class JSON(webapp.RequestHandler):
  def get(self, key):
    data = { 'item': model.Item.get( key ) }
    path = os.path.join(os.path.dirname(__file__), 'templates/get.json')
    self.response.out.write(template.render(path, data))

class Edit(webapp.RequestHandler):
  def get(self, key):
    data = { 'item': model.Item.get( key ) }
    path = os.path.join(os.path.dirname(__file__), 'templates/edit.htm')
    self.response.out.write(template.render(path, data))

  def post(self, key):
    item = model.Item.get( key )
    item.name=self.request.get("name")
    item.description=self.request.get("description")
    item.seller=self.request.get("seller")
    item.price=int( float( self.request.get("price") ) * 100 )
    item.available=int( self.request.get("available") )
    item.save()
    data = { 'item': item, 'message': 'The item was updated' }
    path = os.path.join(os.path.dirname(__file__), 'templates/edit.htm')
    self.response.out.write(template.render(path, data))

class Add(webapp.RequestHandler):
  def get(self):
    data = {}
    path = os.path.join(os.path.dirname(__file__), 'templates/add.htm')
    self.response.out.write(template.render(path, data))

  def post(self):
    # add item
    item = model.Item(
      name=self.request.get("name"),
      description=self.request.get("description"),
      seller=self.request.get("seller"),
      price=int( float( self.request.get("price") ) * 100 ),
      available=int( self.request.get("available") )
    )
    item.save()

    # back home
    data = { 'items': model.Item.all(), 'message': 'The item was added'  }
    path = os.path.join(os.path.dirname(__file__), 'templates/main.htm')
    self.response.out.write(template.render(path, data))

class IPN (webapp.RequestHandler):
  def post(self, key):
    '''incoming post from paypal'''
    logging.debug( "IPN received for %s" % key )
    ipn = paypal.IPN( self.request )
    if ipn.success():
      # request is paypal's
      item = model.Item.get( key )
      # confirm amount
      if item.price_decimal() != ipn.amount:
        logging.info( "IPN amounts didn't match. Item price %f. Payment made %f" % ( item.price_dollars(), ipn.amount ) )
      else:
        item.available -= 1 # success
        item.save()
        logging.info( "Item %s was purchased" % item.name )
    else:
      logging.info( "PayPal IPN verify failed: %s" % ipn.error )
      logging.debug( "Request was: %s" % self.request.body )


application = webapp.WSGIApplication( [
    ('/', Home),
    ('/add/', Add),
    ('/get/(.*)', JSON),
    ('/edit/(.*)', Edit),
    ('/ipn/(.*)', IPN),
  ],
  debug=True)

def main():
  logging.getLogger().setLevel(logging.DEBUG)
  run_wsgi_app(application)

if __name__ == "__main__":
  main()


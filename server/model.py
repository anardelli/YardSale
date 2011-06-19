import decimal
import hashlib
import urllib

from google.appengine.ext import db

class Item(db.Model):
  '''an item for sale'''
  created = db.DateTimeProperty(auto_now_add=True)
  name = db.StringProperty()
  description = db.StringProperty()
  seller = db.StringProperty()
  price = db.IntegerProperty() # cents
  available = db.IntegerProperty()

  def price_dollars( self ):
    return self.price / 100.0

  def price_decimal( self ):
    return decimal.Decimal( str( self.price / 100.0 ) )
  
  def qr_code( self ):
    return "https://chart.googleapis.com/chart?chs=300x300&cht=qr&chl=%s&choe=UTF-8" % self.key()

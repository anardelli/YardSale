import decimal
import logging
import urllib
import urllib2

from google.appengine.api import urlfetch

# hack to enable urllib to work with Python
import os
os.environ['foo_proxy'] = 'bar'

from django.utils import simplejson as json

PAYPAL_PAYMENT_HOST = 'https://www.sandbox.paypal.com/au/cgi-bin/webscr' # sandbox

class IPN( object ):
  def __init__( self, request ):
    # verify that the request is paypal's
    self.error = None
    verify_response = url_request( "%s?cmd=_notify-validate" % PAYPAL_PAYMENT_HOST, data=urllib.urlencode( request.POST.copy() ) )
    # check code
    if verify_response.code() != 200:
      self.error = 'PayPal response code was %i' % verify_response.code()
      return
    # check response
    raw_response = verify_response.content()
    if raw_response != 'VERIFIED':
      self.error = 'PayPal response was "%s"' % raw_response
      return
    # check payment status
    if request.get('payment_status') != 'Completed':
      self.error = 'PayPal status was "%s"' % request.get('payment_status')
      return

    amount = request.get( "mc_gross" )
    self.amount = decimal.Decimal(amount)

  def success( self ):
    return self.error == None

class url_request( object ):
  '''wrapper for urlfetch'''
  def __init__( self, url, data=None, headers={} ):
    # urlfetch - validated
    self.response = urlfetch.fetch( url, payload=data, headers=headers, method=urlfetch.POST, validate_certificate=True )
    # urllib - not validated
    #request = urllib2.Request(url, data=data, headers=headers) 
    #self.response = urllib2.urlopen( https_request )

  def content( self ):
    return self.response.content

  def code( self ):
    return self.response.status_code


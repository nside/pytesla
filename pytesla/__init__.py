__version__ = "0.1"
__date__ = "02-06-2013"
__author__ = "Denis Laprise - dlaprise@gmail.com"

import urllib2, urllib, re, json, sys

class CookieJar:

    def __init__(self):
        self._cookies = {}

    def extractCookies(self, response, nameFilter = None):
        for cookie in response.headers.getheaders('Set-Cookie'):
            name, value = (cookie.split("=", 1) + [""])[:2]
            if not nameFilter or name in nameFilter:
                self._cookies[name] = value.split(";")[0]


    def addCookie(self, name, value):
        self._cookies[name] = value

    def hasCookie(self, name):
        return self._cookies.has_key(name)

    def setCookies(self, request):
        request.add_header('Cookie',
                           "; ".join(["%s=%s" % (k,v)
                                     for k,v in self._cookies.items()]))

    def __repr__(self):
	return str(self._cookies)

class GHTTPCookieProcessor(urllib2.BaseHandler):
    def __init__(self, cookieJar):
        self.cookies = cookieJar
        
    def https_response(self, request, response):
        self.cookies.extractCookies(response)
        return response

    def https_request(self, request):
        self.cookies.setCookies(request)
        return request

GHTTPCookieProcessor.http_request = GHTTPCookieProcessor.https_request
GHTTPCookieProcessor.http_response = GHTTPCookieProcessor.https_response

class Session:
	def __init__(self):
		self._cookies = CookieJar()

	def read_url(self, url, post_data = None):
		"""
		Gets the url URL with cookies enabled. Posts post_data.
		"""
		req = urllib2.build_opener(GHTTPCookieProcessor(self._cookies))
		req.addheaders = [('User-agent', "pytesla %s" % __version__)]
		if post_data.__class__ == dict:
			post = urllib.urlencode(post_data)
		else:
			post = post_data
		f = req.open(self._encode(url), data=post)
		if f.headers.dict.has_key('set-cookie'):
			self._cookies.extractCookies(f)
		return f	

	def read_json(self, url, post_data = None):
		data = self.read_url( url, post_data ).read()
		return json.loads( data )

	def _encode(self, value):
		if isinstance(value, unicode):
			value = value.encode("utf-8")
		return value
_ENDPOINT = 'https://portal.vn.teslamotors.com/'

class ErrorInvalidCredentials(Exception):
	pass

class Connection(Session):
	def __init__(self, email, passwd):
		Session.__init__(self)
		self.login(email, passwd)

	def login(self, email, passwd):
		self.read_url(_ENDPOINT + 'login')
		self.read_url(_ENDPOINT + 'login', {'user_session[email]' : email, 'user_session[password]' : passwd } )
		if not self._cookies.hasCookie('user_credentials'):
			raise ErrorInvalidCredentials()


	def vehicle(self, vin):
		return Vehicle(vin, self)

	def vehicles(self):
		payload = self.read_json(_ENDPOINT + 'vehicles')
		v = []
		for p in payload:
			v.append( Vehicle( p['vin'], self, p) )
		return v

class Vehicle:
	
	def __init__(self, vin, conn, payload = None):
		self._conn = conn
		self._vin = vin
		self._id = None
		if payload:
			self.update(payload)
		
		
	def update(self, p=None):
		if not p:
			p = filter(lambda x: x['vin'] == vin, self.read_json(_ENDPOINT + 'vehicles'))[0]
			
		assert p['vin'] == self.vin
		self._id = p['id']
		self._options = p['option_codes'].split(',')
		self._state = p['state']
		self._color = p['color']
		return self

	@property
	def vin(self):
		return self._vin

	@property
	def id(self):
		return self._id

	@property
	def mobile_enabled(self):
		p = self._conn.read_json(_ENDPOINT + 'vehicles/%s/mobile_enabled' % (self.id,))
		return p['result']

	@property
	def charge_state(self):
		return self._command('charge_state')

	@property
	def climate_state(self):
		return self._command('climate_state')
	
	@property
	def drive_state(self):
		return self._command('drive_state')

	@property
	def gui_settings(self):
		return self._command('gui_settings')

	@property
	def vehicle_state(self):
		return self._command('vehicle_state')

	def _command(self, verb, **kwargs):
		get = ''
		if kwargs:
			get = '?' + urllib.urlencode(kwargs)
		return self._conn.read_json(_ENDPOINT + ('vehicles/%s/command/%s' + get) % (self.id, verb))

	def door_lock(self):
		p = self._command('door_lock')
		return p['result']

	def door_unlock(self):
		p = self._command('door_unlock')
		return p['result']
	
	def charge_standard(self):
		p = self._command('charge_standard')
		return p['result']

	def charge_max_range(self):
		p = self._command('charge_max_range')
		return p['result']

	def charge_start(self):
		p = self._command('charge_start')
		return p['result']

	def charge_stop(self):
		p = self._command('charge_stop')
		return p['result']

	def flash_lights(self):
		p = self._command('flash_lights')
		return p['result']
	
	def honk_horn(self):
		p = self._command('honk_horn')
		return p['result']

	def set_temps(self, driver, passenger):
		p = self._command('set_temps', driver_degC = driver, pasenger_temp = passenger)
		return p['result']
	
	def auto_conditioning_start(self):
		p = self._command('auto_conditioning_start')
		return p['result']

	def auto_conditioning_stop(self):
		p = self._command('auto_conditioning_stop')
		return p['result']

	def sun_roof_control(self, state):
		if not state in ('open', 'close', 'comfort', 'vent'):
			raise Exception('Invalid sunroof state')
		p = self._command('sun_roof_control', state = state)
	
	def __repr__(self):
		return "<Vehicle %s>" % self.vin	



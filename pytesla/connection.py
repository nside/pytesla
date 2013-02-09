import urllib2, urllib, re, json, sys
from vehicle import Vehicle

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
		req.addheaders = [('User-agent', "pytesla")]
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

	def read_json_path(self, path, post_data = None):
		return Session.read_json(self, _ENDPOINT + path, post_data)


	def vehicle(self, vin):
		return Vehicle(vin, self)

	def vehicles(self):
		payload = self.read_json_path('vehicles')
		v = []
		for p in payload:
			v.append( Vehicle( p['vin'], self, p) )
		return v


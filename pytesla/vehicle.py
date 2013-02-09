import urllib

class Vehicle:
	
	def __init__(self, vin, conn, payload = None):
		self._conn = conn
		self._vin = vin
		self._id = None
		self.update(payload)
		
		
	def update(self, p=None):
		if not p:
			p = filter(lambda x: x['vin'] == self._vin, self._conn.read_json_path('vehicles'))[0]
			
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
		p = self._conn.read_json_path('vehicles/%s/mobile_enabled' % (self.id,))
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
		return self._conn.read_json_path(('vehicles/%s/command/%s' + get) % (self.id, verb))

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



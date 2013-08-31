import urllib

class CommandError(Exception):
    """Tesla Model S vehicle command returned failure"""
    pass

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
        return self._request('charge_state')

    @property
    def climate_state(self):
        return self._request('climate_state')

    @property
    def drive_state(self):
        return self._request('drive_state')

    @property
    def gui_settings(self):
        return self._request('gui_settings')

    @property
    def vehicle_state(self):
        return self._request('vehicle_state')

    def _request(self, verb, command=False, **kwargs):
        get = ''
        if kwargs:
            get = '?' + urllib.urlencode(kwargs)
        p = self._conn.read_json_path(('vehicles/%s/command/%s' + get) % (self.id, verb))
        if command and not p['result']:
            # Command returned failure, raise exception
            raise CommandError(p['reason'])
        return p

    def door_lock(self):
        self._request('door_lock', command=True)

    def door_unlock(self):
        self._request('door_unlock', command=True)

    def charge_port_door_open(self):
        self._request('charge_port_door_open', command=True)

    def charge_standard(self):
        self._request('charge_standard', command=True)

    def charge_max_range(self):
        self._request('charge_max_range', command=True)

    def charge_start(self):
        self._request('charge_start', command=True)

    def charge_stop(self):
        self._request('charge_stop', command=True)

    def flash_lights(self):
        self._request('flash_lights', command=True)

    def honk_horn(self):
        self._request('honk_horn', command=True)

    def set_temps(self, driver, passenger):
        self._request('set_temps', command=True, driver_temp=driver, passenger_temp=passenger)

    def auto_conditioning_start(self):
        self._request('auto_conditioning_start', command=True)

    def auto_conditioning_stop(self):
        self._request('auto_conditioning_stop', command=True)

    def sun_roof_control(self, state, percent=None):
        if state == 'move' and percent:
            self._request('sun_roof_control', command=True, state=state, percent=percent)
        elif state in ('open', 'close', 'comfort', 'vent'):
            self._request('sun_roof_control', command=True, state=state)
        else:
            raise ValueError("Invalid sunroof state")

    def wake_up(self):
        self._request('wake_up', command=True)

    def __repr__(self):
        return "<Vehicle %s>" % self.vin

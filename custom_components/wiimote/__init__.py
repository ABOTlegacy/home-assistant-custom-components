#!/srv/wiimote/bin/python3.4
###
### --> configuration.yaml
### wiimote:
###
### Install Wiimote
### http://www.raspberrypi-spy.co.uk/2013/02/nintendo-wii-remote-python-and-the-raspberry-pi/
### https://github.com/azzra/python3-wiimote
###
import threading
import time
import logging
import asyncio
from asyncio.futures import CancelledError
import logging
import async_timeout
import cwiid

from homeassistant.const import (EVENT_STATE_CHANGED, EVENT_HOMEASSISTANT_START, EVENT_HOMEASSISTANT_STOP, CONF_API_KEY)
from homeassistant.core import callback
from homeassistant.helpers.discovery import load_platform

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = []
DOMAIN = 'wiimote'
EVENT_IR_COMMAND_RECEIVED = 'ir_command_received'
BUTTON_NAME = 'button_name'
BUTTON_DELAY = 0.5


@asyncio.coroutine
def async_setup(hass, config):
    """Set up the Wiimote platform."""
    load_platform(hass, 'switch', 'wiimote')
    
    @callback
    def _stateChanged(event):
        """Start the bot."""
        if event.data.get('entity_id') in ('switch.wiimote'):
            _LOGGER.debug(event.data.get('new_state').state)
            wiimote_interface = WiimoteInterface(hass)
            if event.data.get('new_state').state is 'on':
                wiimote_interface = WiimoteInterface(hass)
                wiimote_interface.start()
            if event.data.get('new_state').state is 'off':
                if wiimote_interface.is_alive():
                    wiimote_interface.stopped.set()
    hass.bus.async_listen(EVENT_STATE_CHANGED, _stateChanged)
    return True

class WiimoteInterface(threading.Thread):

    def __init__(self, hass):
        """Construct a Wiimote interface object."""
        threading.Thread.__init__(self)
        self.daemon = True
        self.stopped = threading.Event()
        self.hass = hass
    
    def run(self):
        """Run the loop of the Wiimote interface thread."""
        _LOGGER.debug("Wiimote: Interface Thread Started")
        time.sleep(0.5)
        try:
            self.stopped = threading.Event()
            self.wii = cwiid.Wiimote()
            self.wii.rpt_mode = cwiid.RPT_BTN
            _LOGGER.debug("Wiimote: Connected")
            _LOGGER.debug(self.stopped.isSet())
        except RuntimeError:
            _LOGGER.debug("Wiimote: Error opening connection")
        while not self.stopped.isSet():
            buttons = self.wii.state['buttons']
            # If Plus and Minus buttons pressed
            # together then rumble and quit.
            if (buttons - cwiid.BTN_PLUS - cwiid.BTN_MINUS == 0):
                _LOGGER.debug("Wiimote: Closing Connection")
                self.wii.rumble = 1
                time.sleep(1)
                self.wii.rumble = 0
                exit(self.wii)
            # Check if other buttons are pressed by
            # doing a bitwise AND of the buttons number
            # and the predefined constant for that button.
            if (buttons & cwiid.BTN_LEFT):
                _LOGGER.debug("Wiimote: LEFT")
                time.sleep(BUTTON_DELAY)
                self.hass.bus.fire(EVENT_IR_COMMAND_RECEIVED, {BUTTON_NAME: '/left'})
            if (buttons & cwiid.BTN_RIGHT):
                _LOGGER.debug("Wiimote: RIGHT")
                time.sleep(BUTTON_DELAY)
                self.hass.bus.fire(EVENT_IR_COMMAND_RECEIVED, {BUTTON_NAME: '/right'})
            if (buttons & cwiid.BTN_UP):
                _LOGGER.debug("Wiimote: UP")
                time.sleep(BUTTON_DELAY)
                self.hass.bus.fire(EVENT_IR_COMMAND_RECEIVED, {BUTTON_NAME: '/up'})
            if (buttons & cwiid.BTN_DOWN):
                _LOGGER.debug("Wiimote: DOWN")
                time.sleep(BUTTON_DELAY)
                self.hass.bus.fire(EVENT_IR_COMMAND_RECEIVED, {BUTTON_NAME: '/down'})
            if (buttons & cwiid.BTN_1):
                _LOGGER.debug("Wiimote: BTN 1")
                time.sleep(BUTTON_DELAY)
                self.hass.bus.fire(EVENT_IR_COMMAND_RECEIVED, {BUTTON_NAME: '/1'})
            if (buttons & cwiid.BTN_2):
                _LOGGER.debug("Wiimote: BTN 2")
                time.sleep(BUTTON_DELAY)
                self.hass.bus.fire(EVENT_IR_COMMAND_RECEIVED, {BUTTON_NAME: '/2'})
            if (buttons & cwiid.BTN_A):
                _LOGGER.debug("Wiimote: BTN A")
                time.sleep(BUTTON_DELAY)
                self.hass.bus.fire(EVENT_IR_COMMAND_RECEIVED, {BUTTON_NAME: '/a'})
            if (buttons & cwiid.BTN_B):
                _LOGGER.debug("Wiimote: BTN B")
                time.sleep(BUTTON_DELAY)
                self.hass.bus.fire(EVENT_IR_COMMAND_RECEIVED, {BUTTON_NAME: '/b'})
            if (buttons & cwiid.BTN_HOME):
                _LOGGER.debug("Wiimote: HOME")
                time.sleep(BUTTON_DELAY)
                self.hass.bus.fire(EVENT_IR_COMMAND_RECEIVED, {BUTTON_NAME: '/home'})
            if (buttons & cwiid.BTN_MINUS):
                _LOGGER.debug("Wiimote: MINUS")
                time.sleep(BUTTON_DELAY)
                self.hass.bus.fire(EVENT_IR_COMMAND_RECEIVED, {BUTTON_NAME: '/minus'})
            if (buttons & cwiid.BTN_PLUS):
                _LOGGER.debug("Wiimote: PLUS")
                time.sleep(BUTTON_DELAY)
                self.hass.bus.fire(EVENT_IR_COMMAND_RECEIVED, {BUTTON_NAME: '/plus'})
            else:
                time.sleep(0.5)
        self.stopped.set()
        _LOGGER.debug('Wiimote: Interface Thread Stopped')
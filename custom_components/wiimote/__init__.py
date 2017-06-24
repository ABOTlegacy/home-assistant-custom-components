#!/srv/telebot/bin/python3.4
###
### --> configuration.yaml
### remote :
###     platform: wiimote
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

@asyncio.coroutine
def async_setup(hass, config):
    """Set up the Wiimote platform."""
    load_platform(hass, 'switch', 'wiimote')
    wiimote_interface = WiimoteInterface(hass)
    
    @callback
    def _stateChanged(event):
        """Start the bot."""
        if event.data.get('entity_id') in ('switch.wiimote'):
            #_LOGGER.info('Wiimote State Has Batman')
            _LOGGER.info(event.data.get('new_state').state)
            if event.data.get('new_state').state is 'on':
                wiimote_interface.start()
                #wiimote_interface.run()
            if event.data.get('new_state').state is 'off':
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
        _LOGGER.debug("BATMAN: Wiimote interface thread started")
        time.sleep(1)
        try:
            self.wii = cwiid.Wiimote()
            _LOGGER.debug("BATMAN: Wiimote Connected")
        except RuntimeError:
            _LOGGER.debug("BATMAN: Error opening wiimote connection")
        while not self.stopped.isSet():
            buttons = self.wii.state['buttons']
            # If Plus and Minus buttons pressed
            # together then rumble and quit.
            if (buttons - cwiid.BTN_PLUS - cwiid.BTN_MINUS == 0):
                _LOGGER.debug("Wiimote is Closing connection ...")
            self.wii.rumble = 1
            time.sleep(1)
            self.wii.rumble = 0
            exit(self.wii)
            # Check if other buttons are pressed by
            # doing a bitwise AND of the buttons number
            # and the predefined constant for that button.
            if (buttons & cwiid.BTN_LEFT):
                time.sleep(BUTTON_DELAY)
                self.hass.bus.fire(EVENT_IR_COMMAND_RECEIVED, {BUTTON_NAME: '/left'})
            if(buttons & cwiid.BTN_RIGHT):
                time.sleep(BUTTON_DELAY)
                self.hass.bus.fire(EVENT_IR_COMMAND_RECEIVED, {BUTTON_NAME: '/right'})
            if (buttons & cwiid.BTN_UP):
                time.sleep(BUTTON_DELAY)
                self.hass.bus.fire(EVENT_IR_COMMAND_RECEIVED, {BUTTON_NAME: '/up'})
            if (buttons & cwiid.BTN_DOWN):
                time.sleep(BUTTON_DELAY)
                self.hass.bus.fire(EVENT_IR_COMMAND_RECEIVED, {BUTTON_NAME: '/down'})
            if (buttons & cwiid.BTN_1):
                time.sleep(BUTTON_DELAY)
                self.hass.bus.fire(EVENT_IR_COMMAND_RECEIVED, {BUTTON_NAME: '/1'})
            if (buttons & cwiid.BTN_2):
                time.sleep(BUTTON_DELAY)
                self.hass.bus.fire(EVENT_IR_COMMAND_RECEIVED, {BUTTON_NAME: '/2'})
            if (buttons & cwiid.BTN_A):
                time.sleep(BUTTON_DELAY)
                self.hass.bus.fire(EVENT_IR_COMMAND_RECEIVED, {BUTTON_NAME: '/a'})
            if (buttons & cwiid.BTN_B):
                time.sleep(BUTTON_DELAY)
                self.hass.bus.fire(EVENT_IR_COMMAND_RECEIVED, {BUTTON_NAME: '/b'})
            if (buttons & cwiid.BTN_HOME):
                time.sleep(BUTTON_DELAY)
                self.hass.bus.fire(EVENT_IR_COMMAND_RECEIVED, {BUTTON_NAME: '/home'})
            if (buttons & cwiid.BTN_MINUS):
                time.sleep(BUTTON_DELAY)
                self.hass.bus.fire(EVENT_IR_COMMAND_RECEIVED, {BUTTON_NAME: '/minus'})
            if (buttons & cwiid.BTN_PLUS):
                time.sleep(BUTTON_DELAY)
                self.hass.bus.fire(EVENT_IR_COMMAND_RECEIVED, {BUTTON_NAME: '/plus'})
            else:
                time.sleep(0.2)
        _LOGGER.debug('Wiimote interface thread stopped')
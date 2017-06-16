#!/srv/telebot/bin/python3.4
###
### --> configuration.yaml
### remote :
###     platform: wiimote
###
### Install Wiimote
### http://www.raspberrypi-spy.co.uk/2013/02/nintendo-wii-remote-python-and-the-raspberry-pi/
###
import threading
import time
import logging
from homeassistant.const import (EVENT_HOMEASSISTANT_STOP, EVENT_HOMEASSISTANT_START)

_LOGGER = logging.getLogger(__name__)

REQUIREMENTS = ['cwiid']
BUTTON_NAME = 'button_name'
BUTTON_DELAY = 0.1
DOMAIN = 'wiimote'
EVENT_IR_COMMAND_RECEIVED = 'ir_command_received'
ICON = 'mdi:remote'
def setup(hass, config):
    """Set up the Wiimote capability."""
    import cwiid
    time.sleep(1)
    try:
        wii=cwiid.Wiimote()
        wiimote_interface = WiimoteInterface(hass)
    except RuntimeError:
        _LOGGER.debug("Error opening wiimote connection")
        quit()

    def _start_wiimote(_event):
        wiimote_interface.start()

    def _stop_wiimote(_event):
        wiimote_interface.stopped.set()

    hass.bus.listen_once(EVENT_HOMEASSISTANT_START, _start_wiimote)
    hass.bus.listen_once(EVENT_HOMEASSISTANT_STOP, _stop_wiimote)
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
        import cwiid
        _LOGGER.debug("Wiimote interface thread started")
        while not self.stopped.isSet():
            buttons = wii.state['buttons']
            # If Plus and Minus buttons pressed
            # together then rumble and quit.
            if (buttons - cwiid.BTN_PLUS - cwiid.BTN_MINUS == 0):
            print '\nClosing connection ...'
            wii.rumble = 1
            time.sleep(1)
            wii.rumble = 0
            exit(wii)
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
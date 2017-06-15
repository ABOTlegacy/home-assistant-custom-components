#!/srv/telebot/bin/python3.4
import sys
import subprocess
import time
import platform
import argparse
import logging
from homeassistant.components.media_player import (MediaPlayerDevice, SUPPORT_SELECT_SOURCE, PLATFORM_SCHEMA)

_LOGGER = logging.getLogger(__name__)


# Protocol command bytes
DEVICE = None
DEVICE_TYPE = None
REQUIREMENTS = []
DOMAIN = 'missile_launcher'
ICON = 'mdi:rocket'
DEFAULT_NAME = 'Missile Launcher'
SUPPORT_MISSILE = SUPPORT_SELECT_SOURCE

# Set Up At Custom Component
def setup_platform(hass, config, add_devices, discovery_info=None):
    name = config.get('name', DEFAULT_NAME)
    # Initialize Device
    add_devices([IMissileSensor(name)])

# Missile Launcher Device
class IMissileSensor(MediaPlayerDevice):
    """Implementation of a Missile Launcher"""
    def __init__(self, name):
        """Initialize the sensor."""
        self._name = name
        self._source = '/none'
        self._source_list = ['/none', '/right', '/left', '/up', '/down', '/fire']
        # Lastly Do An Update
        self.update()

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def icon(self):
        """Return the icon for the frontend."""
        return ICON

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        return SUPPORT_MISSILE
        
    @property
    def source(self):
        """Return the current input source."""
        return self._source

    @property
    def source_list(self):
        """List of available input sources."""
        return self._source_list
    
    @property
    def media_image_url(self):
        """Return the image URL of current playing media."""
        # MAKE SURE THIS FILE HAS WRITE ACCESS
        subprocess.Popen(['fswebcam', '/home/homeassistant/.homeassistant/www/missile_launcher.jpg'], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        return 'http://127.0.0.1:8123/local/missile_launcher.jpg?1=1&t=%s' % (time.time())
    
    @property
    def state(self):
        """Return the date of the next event."""
        return '/none'

    def update(self):
        """Get the latest update and set the state."""
        self._source = '/none'

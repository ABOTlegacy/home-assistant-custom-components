"""
Local list platform.
Forked From: https://github.com/Tommatheussen

For more details about this platform, please refer to the documentation
https://home-assistant.io/components/list.local/
"""
import asyncio
import logging
import os
import json
import voluptuous as vol
from custom_components.list import (ListEntity, ATTR_ITEMS)
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (ATTR_ENTITY_ID, CONF_NAME)

DOMAIN = 'list'
LOCAL_LISTS_FILE = 'local_lists.conf'
SERVICE_NEW_LIST = 'new_list'

_LOGGER = logging.getLogger(__name__)

NEW_LIST_SCHEMA = vol.Schema({
    vol.Required(CONF_NAME): cv.string,
    vol.Optional(ATTR_ITEMS, default=[]): cv.ensure_list
})


def write_list(filename, list_name, list_items):
    """Update a single list in file."""
    all_lists = config_from_file(filename)

    for list in all_lists:
        if list['name'] == list_name:
            list['items'] = list_items

    config_from_file(filename, all_lists)


def config_from_file(filename, config=None):
    """Small configuration file management function."""
    if config:
        # We're writing configuration
        try:
            with open(filename, 'w') as fdesc:
                fdesc.write(json.dumps(config))
        except IOError as error:
            _LOGGER.error('Saving local list failed: %s', error)
            return False
        return True
    else:
        if os.path.isfile(filename):
            try:
                with open(filename, 'r') as fdesc:
                    return json.loads(fdesc.read())
            except IOError as error:
                _LOGGER.error('Reading local list failed: %s', error)
                return False
        else:
            return []


@asyncio.coroutine
def async_setup_platform(hass, config, async_add_devices, discovery_info=None):
    """Setup the Local list platform."""
    existing_lists = config_from_file(hass.config.path(LOCAL_LISTS_FILE))

    if len(existing_lists):
        yield from async_add_devices([
            LocalList(hass, list['name'], list['items'])
            for list in existing_lists
        ])
    else:
        _LOGGER.info('No list exists yet, creating default list')
        new_list = create_list(hass, 'default list')
        yield from async_add_devices([
            LocalList(hass, new_list['name'], new_list['items'])
        ])

    @asyncio.coroutine
    def async_handle_new_list_service(service):
        params = service.data.copy()

        new_list = create_list(hass, params['name'], params['items'])

        yield from async_add_devices([
            LocalList(hass, new_list['name'], new_list['items'])
        ])

    hass.services.async_register(
            DOMAIN, SERVICE_NEW_LIST, async_handle_new_list_service,
            schema=NEW_LIST_SCHEMA)

    return True


def create_list(hass, name, items=[]):
    """Create a new list in file."""
    new_list = {}
    new_list['name'] = name
    new_list['items'] = items

    current_lists = config_from_file(hass.config.path(LOCAL_LISTS_FILE))
    current_lists.append(new_list)
    config_from_file(hass.config.path(LOCAL_LISTS_FILE), current_lists)
    return new_list


class LocalList(ListEntity):
    """Representation of a local list."""

    def __init__(self, hass, name, items=[], supported_features=None):
        """Initialize the list."""
        self._hass = hass
        self._name = name
        self._items = items
        self._supported_features = supported_features

    @property
    def name(self):
        """Return the name of the list if any."""
        return self._name

    @property
    def items(self):
        """Return true if lock is locked."""
        return self._items

    @property
    def supported_features(self):
        """Flag supported features."""
        if self._supported_features is not None:
            return self._supported_features
        else:
            return super().supported_features

    def add_item(self, item, **kwargs):
        """Add item to list."""
        self._items.append(item)
        self.update_file()

    def remove_item(self, item, **kwargs):
        """Remove item from list."""
        if item in self._items:
            self._items.remove(item)
            self.update_file()

    def clear_list(self, **kwargs):
        """Clear all items from list."""
        self._items = []
        self.update_file()

    def update_file(self):
        """Write list to file."""
        write_list(self._hass.config.path(LOCAL_LISTS_FILE),
                   self._name, self._items)
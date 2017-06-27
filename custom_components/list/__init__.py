"""
Provides functionality to manage lists.
Forked From: https://github.com/Tommatheussen

For more details about this component, please refer to the documentation at
https://home-assistant.io/components/list/
"""
import asyncio
import functools as ft
import logging
import os

import voluptuous as vol

from homeassistant.config import load_yaml_config_file
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_component import EntityComponent

from homeassistant.const import (ATTR_ENTITY_ID)

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'list'

ATTR_ITEM = 'item'
ATTR_ITEMS = 'items'

SERVICE_ADD_ITEM = 'add_item'
SERVICE_REMOVE_ITEM = 'remove_item'
SERVICE_CLEAR_LIST = 'clear_list'

SUPPORT_ADD = 1
SUPPORT_REMOVE = 2

LIST_SERVICE_SCHEMA = vol.Schema({
    vol.Optional(ATTR_ENTITY_ID): cv.entity_ids
})

LIST_ADD_ITEM_SCHEMA = LIST_SERVICE_SCHEMA.extend({
    vol.Required(ATTR_ITEM): cv.string
})

LIST_REMOVE_ITEM_SCHEMA = vol.Schema({
    vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
    vol.Required(ATTR_ITEM): cv.string
})

SERVICE_TO_METHOD = {
    SERVICE_ADD_ITEM: {
        'method': 'async_add_item',
        'schema': LIST_ADD_ITEM_SCHEMA
    },
    SERVICE_REMOVE_ITEM: {
        'method': 'async_remove_item',
        'schema': LIST_REMOVE_ITEM_SCHEMA
    },
    SERVICE_CLEAR_LIST: {
        'method': 'async_clear_list'
    }
}


def add_item(hass, item, entity_id=None):
    """Add item to list."""
    data = {ATTR_ENTITY_ID: entity_id} if entity_id else {}
    data[ATTR_ITEM] = item
    hass.services.call(DOMAIN, SERVICE_ADD_ITEM, data)


def remove_item(hass, item, entity_id=None):
    """Remove item from list."""
    data = {ATTR_ENTITY_ID: entity_id}
    data[ATTR_ITEM] = item
    hass.services.call(DOMAIN, SERVICE_REMOVE_ITEM, data)


def clear_list(hass, entity_id):
    """Clear all items from list."""
    data = {ATTR_ENTITY_ID: entity_id}
    hass.services.call(DOMAIN, SERVICE_CLEAR_LIST, data)


@asyncio.coroutine
def async_setup(hass, config):
    """Setup the list component."""
    component = EntityComponent(_LOGGER, DOMAIN, hass)

    yield from component.async_setup(config)

    @asyncio.coroutine
    def async_handle_list_service(service):
        target_lists = component.async_extract_from_service(service)
        method = SERVICE_TO_METHOD.get(service.service)
        params = service.data.copy()

        for list in target_lists:
            yield from getattr(list, method['method'])(**params)

        for list in target_lists:
            yield from hass.loop.create_task(
                list.async_update_ha_state(True))

    descriptions = yield from hass.loop.run_in_executor(
        None, load_yaml_config_file, os.path.join(
            os.path.dirname(__file__), 'services.yaml'))

    for service_name in SERVICE_TO_METHOD:
        schema = SERVICE_TO_METHOD[service_name].get(
            'schema', LIST_SERVICE_SCHEMA)
        hass.services.async_register(
            DOMAIN, service_name, async_handle_list_service,
            descriptions.get(service_name), schema=schema)

    return True


# pylint: disable=no-member, no-self-use
class ListEntity(Entity):
    """Representation of a list."""

    @property
    def items(self):
        """Return the configured items."""
        return None

    @property
    def state_attributes(self):
        """Return the state attributes."""
        data = {
            'items': self.items
        }

        return data

    @property
    def state(self):
        """Return the amount of items."""
        return len(self.items)

    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_ADD | SUPPORT_REMOVE

    def async_add_item(self, **kwargs):
        """Add an item.

        This method must be run in the event loop and returns a coroutine.
        """
        return self.hass.loop.run_in_executor(None, ft.partial(self.add_item, **kwargs))

    def async_remove_item(self, **kwargs):
        """Remove an item.

        This method must be run in the event loop and returns a coroutine.
        """
        return self.hass.loop.run_in_executor(None, ft.partial(self.remove_item, **kwargs))

    def async_clear_list(self, **kwargs):
        """Clear a list.

        This method must be run in the event loop and returns a coroutine.
        """
        return self.hass.loop.run_in_executor(None, ft.partial(self.clear_list, **kwargs))
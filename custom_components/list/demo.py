"""
Demo list platform that has two fake lists.
Forked From: https://github.com/Tommatheussen

For more details about this platform, please refer to the documentation
https://home-assistant.io/components/demo/

== configuration.yaml ==
list:
  - platform: demo

"""
import asyncio
import logging
from custom_components.list import (ListEntity, SUPPORT_REMOVE, SUPPORT_ADD)

_LOGGER = logging.getLogger(__name__)

@asyncio.coroutine
def async_setup_platform(hass, config, async_add_devices, discovery_info=None):
    """Setup the Demo lock platform."""
    async_add_devices([
        DemoList('Shopping List', ["Milk"], supported_features=(SUPPORT_ADD | SUPPORT_REMOVE))
    ])
    return True

class DemoList(ListEntity):
    """Representation of a Demo list."""

    def __init__(self, name, items, supported_features=None):
        """Initialize the list."""
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

    def remove_item(self, item, **kwargs):
        """Remove item from list."""
        if item in self._items:
            self._items.remove(item)
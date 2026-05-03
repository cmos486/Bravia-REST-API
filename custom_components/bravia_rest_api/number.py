"""Number entities for Bravia REST API."""

from __future__ import annotations

import logging

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .bravia_client import BraviaError
from .const import DOMAIN
from .coordinator import BraviaCoordinator
from .entity import BraviaEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Bravia REST API number entities."""
    coordinator: BraviaCoordinator = hass.data[DOMAIN][entry.entry_id]
    if coordinator.brightness_supported:
        async_add_entities([BraviaBrightnessNumber(coordinator, entry)])


class BraviaBrightnessNumber(BraviaEntity, NumberEntity):
    """Number entity for TV picture brightness."""

    _attr_translation_key = "brightness"
    _attr_icon = "mdi:brightness-6"
    _attr_mode = NumberMode.SLIDER
    _attr_native_step = 1.0

    def __init__(
        self,
        coordinator: BraviaCoordinator,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.unique_id}_brightness"
        self._attr_native_min_value = float(coordinator.brightness_min)
        self._attr_native_max_value = float(coordinator.brightness_max)

    @property
    def native_value(self) -> float | None:
        """Return the current brightness value."""
        data = self.coordinator.data
        if not data or data.brightness is None:
            return None
        return float(data.brightness)

    async def async_set_native_value(self, value: float) -> None:
        """Set the brightness value."""
        try:
            await self.coordinator.client.set_brightness(int(value))
        except BraviaError as err:
            _LOGGER.error("Failed to set brightness: %s", err)
        await self.coordinator.async_request_refresh()

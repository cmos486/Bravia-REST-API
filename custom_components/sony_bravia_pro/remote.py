"""Remote entity for Sony Bravia Pro (IRCC commands)."""

from __future__ import annotations

import asyncio
from collections.abc import Iterable
import logging
from typing import Any

from homeassistant.components.remote import RemoteEntity, RemoteEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .bravia_client import BraviaError
from .const import DOMAIN, IRCC_CODES
from .coordinator import BraviaCoordinator
from .entity import BraviaEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Sony Bravia Pro remote."""
    coordinator: BraviaCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([BraviaRemote(coordinator, entry)])


class BraviaRemote(BraviaEntity, RemoteEntity):
    """Sony Bravia Pro remote control entity.

    This entity is always on — it represents the command sender,
    not the TV power state. Power control is handled by the media_player.
    """

    _attr_translation_key = "remote"
    _attr_name = "Remote"
    _attr_supported_features = RemoteEntityFeature(0)

    def __init__(
        self,
        coordinator: BraviaCoordinator,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.unique_id}_remote"

    @property
    def is_on(self) -> bool:
        """Always on — the remote is a command sender, not a power toggle."""
        return True

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return available IRCC commands as an attribute."""
        all_commands = set(IRCC_CODES.keys()) | set(self.coordinator.ircc_codes.keys())
        return {
            "available_commands": sorted(all_commands),
            "tv_discovered_commands": sorted(self.coordinator.ircc_codes.keys()),
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        """No-op — remote is always on."""

    async def async_turn_off(self, **kwargs: Any) -> None:
        """No-op — remote is always on."""

    async def async_send_command(
        self,
        command: Iterable[str],
        **kwargs: Any,
    ) -> None:
        """Send IRCC commands to the TV.

        Accepts both command names (e.g., 'VolumeUp') and raw IRCC codes
        (base64 strings ending in '==').
        """
        num_repeats = kwargs.get("num_repeats", 1)
        delay_secs = kwargs.get("delay_secs", 0.0)

        for _ in range(num_repeats):
            for cmd in command:
                try:
                    if cmd.endswith("==") or cmd.endswith("Aw=="):
                        await self.coordinator.client.send_ircc(cmd)
                    else:
                        code = (
                            self.coordinator.ircc_codes.get(cmd)
                            or IRCC_CODES.get(cmd)
                        )
                        if code is None:
                            _LOGGER.error(
                                "Unknown IRCC command '%s'. Check available_commands attribute.",
                                cmd,
                            )
                            continue
                        await self.coordinator.client.send_ircc(code)
                except BraviaError as err:
                    _LOGGER.error("Failed to send IRCC command '%s': %s", cmd, err)

            if delay_secs > 0 and num_repeats > 1:
                await asyncio.sleep(delay_secs)

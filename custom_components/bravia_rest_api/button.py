"""Button entities for Bravia REST API."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .bravia_client import BraviaClient, BraviaError
from .const import DOMAIN, POWER_SAVING_OFF, POWER_SAVING_PICTURE_OFF
from .coordinator import BraviaCoordinator
from .entity import BraviaEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class BraviaButtonDescription(ButtonEntityDescription):
    """Describe a Bravia button entity."""

    press_fn: Callable[[BraviaClient], Coroutine[Any, Any, None]] | None = None
    ircc_command: str | None = None


# --- System action buttons ---

SYSTEM_BUTTONS: tuple[BraviaButtonDescription, ...] = (
    BraviaButtonDescription(
        key="reboot",
        translation_key="reboot",
        name="Reboot",
        icon="mdi:restart",
        press_fn=lambda client: client.request_reboot(),
    ),
    BraviaButtonDescription(
        key="terminate_apps",
        translation_key="terminate_apps",
        name="Terminate Apps",
        icon="mdi:close-box-multiple",
        press_fn=lambda client: client.terminate_apps(),
    ),
    BraviaButtonDescription(
        key="picture_off",
        translation_key="picture_off",
        name="Picture Off",
        icon="mdi:monitor-off",
        press_fn=lambda client: client.set_power_saving_mode(
            POWER_SAVING_PICTURE_OFF
        ),
    ),
    BraviaButtonDescription(
        key="picture_on",
        translation_key="picture_on",
        name="Picture On",
        icon="mdi:monitor",
        press_fn=lambda client: client.set_power_saving_mode(POWER_SAVING_OFF),
    ),
)


# --- IRCC remote command buttons ---


IRCC_BUTTONS: tuple[BraviaButtonDescription, ...] = (
    # Navigation
    BraviaButtonDescription(
        key="ircc_home",
        name="Remote: Home",
        icon="mdi:home",
        ircc_command="Home",
    ),
    BraviaButtonDescription(
        key="ircc_back",
        name="Remote: Back",
        icon="mdi:arrow-left",
        ircc_command="Return",
    ),
    BraviaButtonDescription(
        key="ircc_up",
        name="Remote: Up",
        icon="mdi:chevron-up",
        ircc_command="Up",
    ),
    BraviaButtonDescription(
        key="ircc_down",
        name="Remote: Down",
        icon="mdi:chevron-down",
        ircc_command="Down",
    ),
    BraviaButtonDescription(
        key="ircc_left",
        name="Remote: Left",
        icon="mdi:chevron-left",
        ircc_command="Left",
    ),
    BraviaButtonDescription(
        key="ircc_right",
        name="Remote: Right",
        icon="mdi:chevron-right",
        ircc_command="Right",
    ),
    BraviaButtonDescription(
        key="ircc_confirm",
        name="Remote: OK",
        icon="mdi:checkbox-marked-circle",
        ircc_command="Confirm",
    ),
    BraviaButtonDescription(
        key="ircc_options",
        name="Remote: Options",
        icon="mdi:dots-vertical",
        ircc_command="Options",
    ),
    # Volume
    BraviaButtonDescription(
        key="ircc_volume_up",
        name="Remote: Volume Up",
        icon="mdi:volume-plus",
        ircc_command="VolumeUp",
    ),
    BraviaButtonDescription(
        key="ircc_volume_down",
        name="Remote: Volume Down",
        icon="mdi:volume-minus",
        ircc_command="VolumeDown",
    ),
    BraviaButtonDescription(
        key="ircc_mute",
        name="Remote: Mute",
        icon="mdi:volume-mute",
        ircc_command="Mute",
    ),
    # Channels
    BraviaButtonDescription(
        key="ircc_channel_up",
        name="Remote: Channel Up",
        icon="mdi:arrow-up-bold",
        ircc_command="ChannelUp",
    ),
    BraviaButtonDescription(
        key="ircc_channel_down",
        name="Remote: Channel Down",
        icon="mdi:arrow-down-bold",
        ircc_command="ChannelDown",
    ),
    # Apps
    BraviaButtonDescription(
        key="ircc_netflix",
        name="Remote: Netflix",
        icon="mdi:netflix",
        ircc_command="Netflix",
    ),
    # Playback
    BraviaButtonDescription(
        key="ircc_play",
        name="Remote: Play",
        icon="mdi:play",
        ircc_command="Play",
    ),
    BraviaButtonDescription(
        key="ircc_pause",
        name="Remote: Pause",
        icon="mdi:pause",
        ircc_command="Pause",
    ),
    BraviaButtonDescription(
        key="ircc_stop",
        name="Remote: Stop",
        icon="mdi:stop",
        ircc_command="Stop",
    ),
    # Input
    BraviaButtonDescription(
        key="ircc_input",
        name="Remote: Input",
        icon="mdi:import",
        ircc_command="Input",
    ),
)

ALL_BUTTONS = SYSTEM_BUTTONS + IRCC_BUTTONS


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Bravia REST API buttons."""
    coordinator: BraviaCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        BraviaButton(coordinator, entry, desc) for desc in ALL_BUTTONS
    )


class BraviaButton(BraviaEntity, ButtonEntity):
    """A Bravia REST API button entity."""

    entity_description: BraviaButtonDescription

    def __init__(
        self,
        coordinator: BraviaCoordinator,
        entry: ConfigEntry,
        description: BraviaButtonDescription,
    ) -> None:
        super().__init__(coordinator, entry)
        self.entity_description = description
        self._attr_unique_id = f"{entry.unique_id}_{description.key}"

    async def async_press(self) -> None:
        """Handle the button press."""
        try:
            if self.entity_description.ircc_command:
                code = self.coordinator.resolve_ircc_code(
                    self.entity_description.ircc_command
                )
                if code is None:
                    _LOGGER.error(
                        "Unknown IRCC command '%s'",
                        self.entity_description.ircc_command,
                    )
                    return
                await self.coordinator.client.send_ircc(code)
            else:
                await self.entity_description.press_fn(self.coordinator.client)
        except BraviaError as err:
            _LOGGER.error(
                "Failed to execute %s: %s",
                self.entity_description.key,
                err,
            )

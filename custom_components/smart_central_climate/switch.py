"""Switch platform for Smart Central Climate (Vacation Mode toggle)."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Vacation Mode switch entity."""
    entity = SmartCentralVacationSwitch(hass, entry)
    async_add_entities([entity])


class SmartCentralVacationSwitch(SwitchEntity):
    """Switch entity to toggle Vacation Mode on/off."""

    _attr_has_entity_name = True
    _attr_device_class = SwitchDeviceClass.SWITCH
    _attr_icon = "mdi:airplane"

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the switch."""
        self.hass = hass
        self.entry = entry
        name = entry.data.get(CONF_NAME, "Smart Central A/C")
        self._attr_name = "Vacation Mode"
        self._attr_unique_id = f"{entry.entry_id}_vacation_mode"
        self._is_on = False

    @property
    def is_on(self) -> bool:
        """Return True if Vacation Mode is active."""
        # Query climate entity state directly if available
        climate_entity_id = f"climate.{self.entry.title.lower().replace(' ', '_')}"
        state = self.hass.states.get(climate_entity_id)
        if state and state.attributes.get("preset_mode") == "vacation":
            return True
        return self._is_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on Vacation Mode."""
        self._is_on = True
        self.async_write_ha_state()

        # Call climate.set_preset_mode vacation
        climate_entity_id = f"climate.{self.entry.title.lower().replace(' ', '_')}"
        await self.hass.services.async_call(
            "climate",
            "set_preset_mode",
            {"entity_id": climate_entity_id, "preset_mode": "vacation"},
            blocking=False,
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off Vacation Mode and resume normal schedule."""
        self._is_on = False
        self.async_write_ha_state()

        climate_entity_id = f"climate.{self.entry.title.lower().replace(' ', '_')}"
        await self.hass.services.async_call(
            "climate",
            "set_preset_mode",
            {"entity_id": climate_entity_id, "preset_mode": "comfort"},
            blocking=False,
        )

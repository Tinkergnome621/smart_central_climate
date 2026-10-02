import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import (
    CONF_NOTIFY_PRESET,
    CONF_NOTIFY_SERVICE,
    CONF_VACATION_HEAT,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.CLIMATE, Platform.SWITCH]


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old entry to new version automatically."""
    _LOGGER.info(
        "Migrating Smart Central Climate config entry '%s' from Version %s to Version 2",
        config_entry.title,
        config_entry.version,
    )

    if config_entry.version == 1:
        new_data = dict(config_entry.data)
        new_options = dict(config_entry.options)
        migrated = False

        # 1. Migrate Vacation Heat default if below the 60.0°F safety floor
        if new_data.get(CONF_VACATION_HEAT, 0) < 60.0:
            new_data[CONF_VACATION_HEAT] = 60.0
            migrated = True
        if CONF_VACATION_HEAT in new_options and new_options.get(CONF_VACATION_HEAT, 0) < 60.0:
            new_options[CONF_VACATION_HEAT] = 60.0
            migrated = True

        # 2. Disable noisy preset change notifications if still enabled from v1 defaults
        if new_data.get(CONF_NOTIFY_PRESET, False) is True:
            new_data[CONF_NOTIFY_PRESET] = False
            migrated = True
        if new_options.get(CONF_NOTIFY_PRESET, False) is True:
            new_options[CONF_NOTIFY_PRESET] = False
            migrated = True

        # 3. Ensure notify service has 'notify.' domain prefix if present
        data_svc = str(new_data.get(CONF_NOTIFY_SERVICE, "")).strip()
        if data_svc and "." not in data_svc:
            new_data[CONF_NOTIFY_SERVICE] = f"notify.{data_svc}"
            migrated = True

        opt_svc = str(new_options.get(CONF_NOTIFY_SERVICE, "")).strip()
        if opt_svc and "." not in opt_svc:
            new_options[CONF_NOTIFY_SERVICE] = f"notify.{opt_svc}"
            migrated = True

        hass.config_entries.async_update_entry(
            config_entry,
            data=new_data,
            options=new_options,
            version=2,
        )
        _LOGGER.info(
            "Smart Central Climate config entry '%s' successfully migrated to Version 2 (Changes applied: %s).",
            config_entry.title,
            migrated,
        )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Smart Central Climate from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {}

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_update_options))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok and entry.entry_id in hass.data.get(DOMAIN, {}):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload when options are updated in the UI."""
    await hass.config_entries.async_reload(entry.entry_id)

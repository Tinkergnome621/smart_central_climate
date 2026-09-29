"""Config flow for Smart Central Climate integration."""
from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_TARGET_CLIMATE,
    CONF_FAN_ENTITY,
    CONF_TEMP_SENSOR,
    CONF_PRESENCE_SENSOR,
    CONF_COOLING_SWING,
    CONF_HEATING_SWING,
    CONF_ERRAND_DELAY,
    CONF_IMMUNITY_DURATION,
    CONF_COMFORT_COOL,
    CONF_COMFORT_HEAT,
    CONF_ECO_COOL,
    CONF_ECO_HEAT,
    CONF_AWAY_COOL,
    CONF_AWAY_HEAT,
    CONF_SLEEP_COOL,
    CONF_SLEEP_HEAT,
    CONF_BOOST_COOL,
    CONF_BOOST_HEAT,
    CONF_VACATION_COOL,
    CONF_VACATION_HEAT,
    CONF_ENABLE_SCHEDULE,
    CONF_WD_P1_TIME,
    CONF_WD_P1_PRESET,
    CONF_WD_P2_TIME,
    CONF_WD_P2_PRESET,
    CONF_WD_P3_TIME,
    CONF_WD_P3_PRESET,
    CONF_WD_P4_TIME,
    CONF_WD_P4_PRESET,
    CONF_WE_P1_TIME,
    CONF_WE_P1_PRESET,
    CONF_WE_P2_TIME,
    CONF_WE_P2_PRESET,
    CONF_WE_P3_TIME,
    CONF_WE_P3_PRESET,
    CONF_WE_P4_TIME,
    CONF_WE_P4_PRESET,
    DEFAULT_COOLING_SWING,
    DEFAULT_HEATING_SWING,
    DEFAULT_ERRAND_DELAY,
    DEFAULT_IMMUNITY_DURATION,
    DEFAULT_COMFORT_COOL,
    DEFAULT_COMFORT_HEAT,
    DEFAULT_ECO_COOL,
    DEFAULT_ECO_HEAT,
    DEFAULT_AWAY_COOL,
    DEFAULT_AWAY_HEAT,
    DEFAULT_SLEEP_COOL,
    DEFAULT_SLEEP_HEAT,
    DEFAULT_BOOST_COOL,
    DEFAULT_BOOST_HEAT,
    DEFAULT_VACATION_COOL,
    DEFAULT_VACATION_HEAT,
    DEFAULT_ENABLE_SCHEDULE,
    DEFAULT_WD_P1_TIME,
    DEFAULT_WD_P1_PRESET,
    DEFAULT_WD_P2_TIME,
    DEFAULT_WD_P2_PRESET,
    DEFAULT_WD_P3_TIME,
    DEFAULT_WD_P3_PRESET,
    DEFAULT_WD_P4_TIME,
    DEFAULT_WD_P4_PRESET,
    DEFAULT_WE_P1_TIME,
    DEFAULT_WE_P1_PRESET,
    DEFAULT_WE_P2_TIME,
    DEFAULT_WE_P2_PRESET,
    DEFAULT_WE_P3_TIME,
    DEFAULT_WE_P3_PRESET,
    DEFAULT_WE_P4_TIME,
    DEFAULT_WE_P4_PRESET,
)

PRESET_OPTIONS = [
    selector.SelectOptionDict(value="comfort", label="Comfort"),
    selector.SelectOptionDict(value="eco", label="Eco"),
    selector.SelectOptionDict(value="away", label="Away"),
    selector.SelectOptionDict(value="sleep", label="Sleep"),
    selector.SelectOptionDict(value="boost", label="Boost"),
]


class SmartCentralClimateConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Smart Central Climate."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize flow."""
        self._data: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Step 1: Select entities."""
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_presets()

        schema = vol.Schema(
            {
                vol.Required("name", default="Smart Central A/C"): str,
                vol.Required(CONF_TARGET_CLIMATE): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="climate")
                ),
                vol.Optional(CONF_FAN_ENTITY): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="fan")
                ),
                vol.Required(CONF_TEMP_SENSOR): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=["sensor", "input_number"])
                ),
                vol.Optional(CONF_PRESENCE_SENSOR): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain=["person", "device_tracker", "binary_sensor", "zone"])
                ),
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema)

    async def async_step_presets(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Step 2: Base temperature setpoints and swings."""
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_schedules()

        schema = vol.Schema(
            {
                vol.Required(CONF_COOLING_SWING, default=DEFAULT_COOLING_SWING): vol.Coerce(float),
                vol.Required(CONF_HEATING_SWING, default=DEFAULT_HEATING_SWING): vol.Coerce(float),
                vol.Required(CONF_ERRAND_DELAY, default=DEFAULT_ERRAND_DELAY): vol.Coerce(int),
                vol.Required(CONF_IMMUNITY_DURATION, default=DEFAULT_IMMUNITY_DURATION): vol.Coerce(int),
                vol.Required(CONF_COMFORT_COOL, default=DEFAULT_COMFORT_COOL): vol.Coerce(float),
                vol.Required(CONF_COMFORT_HEAT, default=DEFAULT_COMFORT_HEAT): vol.Coerce(float),
                vol.Required(CONF_ECO_COOL, default=DEFAULT_ECO_COOL): vol.Coerce(float),
                vol.Required(CONF_ECO_HEAT, default=DEFAULT_ECO_HEAT): vol.Coerce(float),
                vol.Required(CONF_AWAY_COOL, default=DEFAULT_AWAY_COOL): vol.Coerce(float),
                vol.Required(CONF_AWAY_HEAT, default=DEFAULT_AWAY_HEAT): vol.Coerce(float),
                vol.Required(CONF_SLEEP_COOL, default=DEFAULT_SLEEP_COOL): vol.Coerce(float),
                vol.Required(CONF_SLEEP_HEAT, default=DEFAULT_SLEEP_HEAT): vol.Coerce(float),
                vol.Required(CONF_VACATION_COOL, default=DEFAULT_VACATION_COOL): vol.Coerce(float),
                vol.Required(CONF_VACATION_HEAT, default=DEFAULT_VACATION_HEAT): vol.Coerce(float),
            }
        )

        return self.async_show_form(step_id="presets", data_schema=schema)

    async def async_step_schedules(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Step 3: Weekday and Weekend 4-Slot Schedules."""
        if user_input is not None:
            self._data.update(user_input)
            return self.async_create_entry(
                title=self._data.get("name", "Smart Central A/C"), data=self._data
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_ENABLE_SCHEDULE, default=DEFAULT_ENABLE_SCHEDULE): bool,
                # Weekday slots (Mon-Fri)
                vol.Required(CONF_WD_P1_TIME, default=DEFAULT_WD_P1_TIME): selector.TimeSelector(),
                vol.Required(CONF_WD_P1_PRESET, default=DEFAULT_WD_P1_PRESET): selector.SelectSelector(
                    selector.SelectSelectorConfig(options=PRESET_OPTIONS)
                ),
                vol.Required(CONF_WD_P2_TIME, default=DEFAULT_WD_P2_TIME): selector.TimeSelector(),
                vol.Required(CONF_WD_P2_PRESET, default=DEFAULT_WD_P2_PRESET): selector.SelectSelector(
                    selector.SelectSelectorConfig(options=PRESET_OPTIONS)
                ),
                vol.Required(CONF_WD_P3_TIME, default=DEFAULT_WD_P3_TIME): selector.TimeSelector(),
                vol.Required(CONF_WD_P3_PRESET, default=DEFAULT_WD_P3_PRESET): selector.SelectSelector(
                    selector.SelectSelectorConfig(options=PRESET_OPTIONS)
                ),
                vol.Required(CONF_WD_P4_TIME, default=DEFAULT_WD_P4_TIME): selector.TimeSelector(),
                vol.Required(CONF_WD_P4_PRESET, default=DEFAULT_WD_P4_PRESET): selector.SelectSelector(
                    selector.SelectSelectorConfig(options=PRESET_OPTIONS)
                ),
                # Weekend slots (Sat-Sun)
                vol.Required(CONF_WE_P1_TIME, default=DEFAULT_WE_P1_TIME): selector.TimeSelector(),
                vol.Required(CONF_WE_P1_PRESET, default=DEFAULT_WE_P1_PRESET): selector.SelectSelector(
                    selector.SelectSelectorConfig(options=PRESET_OPTIONS)
                ),
                vol.Required(CONF_WE_P2_TIME, default=DEFAULT_WE_P2_TIME): selector.TimeSelector(),
                vol.Required(CONF_WE_P2_PRESET, default=DEFAULT_WE_P2_PRESET): selector.SelectSelector(
                    selector.SelectSelectorConfig(options=PRESET_OPTIONS)
                ),
                vol.Required(CONF_WE_P3_TIME, default=DEFAULT_WE_P3_TIME): selector.TimeSelector(),
                vol.Required(CONF_WE_P3_PRESET, default=DEFAULT_WE_P3_PRESET): selector.SelectSelector(
                    selector.SelectSelectorConfig(options=PRESET_OPTIONS)
                ),
                vol.Required(CONF_WE_P4_TIME, default=DEFAULT_WE_P4_TIME): selector.TimeSelector(),
                vol.Required(CONF_WE_P4_PRESET, default=DEFAULT_WE_P4_PRESET): selector.SelectSelector(
                    selector.SelectSelectorConfig(options=PRESET_OPTIONS)
                ),
            }
        )

        return self.async_show_form(step_id="schedules", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow to modify settings anytime."""
        return SmartCentralClimateOptionsFlow(config_entry)


class SmartCentralClimateOptionsFlow(config_entries.OptionsFlow):
    """Handle options menu to modify temperatures, schedules, and delays anytime."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        self._options: dict[str, Any] = {**config_entry.data, **config_entry.options}

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Menu for options."""
        return self.async_show_menu(
            step_id="init",
            menu_options=["temperatures", "weekday_schedule", "weekend_schedule", "presence_timers"],
        )

    async def async_step_temperatures(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Modify temperature setpoints, swings, and vacation temperatures."""
        if user_input is not None:
            self._options.update(user_input)
            return self.async_create_entry(title="", data=self._options)

        cfg = self._options
        schema = vol.Schema(
            {
                vol.Required(CONF_COOLING_SWING, default=cfg.get(CONF_COOLING_SWING, DEFAULT_COOLING_SWING)): vol.Coerce(float),
                vol.Required(CONF_HEATING_SWING, default=cfg.get(CONF_HEATING_SWING, DEFAULT_HEATING_SWING)): vol.Coerce(float),
                vol.Required(CONF_COMFORT_COOL, default=cfg.get(CONF_COMFORT_COOL, DEFAULT_COMFORT_COOL)): vol.Coerce(float),
                vol.Required(CONF_COMFORT_HEAT, default=cfg.get(CONF_COMFORT_HEAT, DEFAULT_COMFORT_HEAT)): vol.Coerce(float),
                vol.Required(CONF_ECO_COOL, default=cfg.get(CONF_ECO_COOL, DEFAULT_ECO_COOL)): vol.Coerce(float),
                vol.Required(CONF_ECO_HEAT, default=cfg.get(CONF_ECO_HEAT, DEFAULT_ECO_HEAT)): vol.Coerce(float),
                vol.Required(CONF_AWAY_COOL, default=cfg.get(CONF_AWAY_COOL, DEFAULT_AWAY_COOL)): vol.Coerce(float),
                vol.Required(CONF_AWAY_HEAT, default=cfg.get(CONF_AWAY_HEAT, DEFAULT_AWAY_HEAT)): vol.Coerce(float),
                vol.Required(CONF_SLEEP_COOL, default=cfg.get(CONF_SLEEP_COOL, DEFAULT_SLEEP_COOL)): vol.Coerce(float),
                vol.Required(CONF_SLEEP_HEAT, default=cfg.get(CONF_SLEEP_HEAT, DEFAULT_SLEEP_HEAT)): vol.Coerce(float),
                vol.Required(CONF_VACATION_COOL, default=cfg.get(CONF_VACATION_COOL, DEFAULT_VACATION_COOL)): vol.Coerce(float),
                vol.Required(CONF_VACATION_HEAT, default=cfg.get(CONF_VACATION_HEAT, DEFAULT_VACATION_HEAT)): vol.Coerce(float),
            }
        )
        return self.async_show_form(step_id="temperatures", data_schema=schema)

    async def async_step_weekday_schedule(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Modify Monday - Friday 4-Slot Schedule."""
        if user_input is not None:
            self._options.update(user_input)
            return self.async_create_entry(title="", data=self._options)

        cfg = self._options
        schema = vol.Schema(
            {
                vol.Required(CONF_ENABLE_SCHEDULE, default=cfg.get(CONF_ENABLE_SCHEDULE, DEFAULT_ENABLE_SCHEDULE)): bool,
                vol.Required(CONF_WD_P1_TIME, default=cfg.get(CONF_WD_P1_TIME, DEFAULT_WD_P1_TIME)): selector.TimeSelector(),
                vol.Required(CONF_WD_P1_PRESET, default=cfg.get(CONF_WD_P1_PRESET, DEFAULT_WD_P1_PRESET)): selector.SelectSelector(
                    selector.SelectSelectorConfig(options=PRESET_OPTIONS)
                ),
                vol.Required(CONF_WD_P2_TIME, default=cfg.get(CONF_WD_P2_TIME, DEFAULT_WD_P2_TIME)): selector.TimeSelector(),
                vol.Required(CONF_WD_P2_PRESET, default=cfg.get(CONF_WD_P2_PRESET, DEFAULT_WD_P2_PRESET)): selector.SelectSelector(
                    selector.SelectSelectorConfig(options=PRESET_OPTIONS)
                ),
                vol.Required(CONF_WD_P3_TIME, default=cfg.get(CONF_WD_P3_TIME, DEFAULT_WD_P3_TIME)): selector.TimeSelector(),
                vol.Required(CONF_WD_P3_PRESET, default=cfg.get(CONF_WD_P3_PRESET, DEFAULT_WD_P3_PRESET)): selector.SelectSelector(
                    selector.SelectSelectorConfig(options=PRESET_OPTIONS)
                ),
                vol.Required(CONF_WD_P4_TIME, default=cfg.get(CONF_WD_P4_TIME, DEFAULT_WD_P4_TIME)): selector.TimeSelector(),
                vol.Required(CONF_WD_P4_PRESET, default=cfg.get(CONF_WD_P4_PRESET, DEFAULT_WD_P4_PRESET)): selector.SelectSelector(
                    selector.SelectSelectorConfig(options=PRESET_OPTIONS)
                ),
            }
        )
        return self.async_show_form(step_id="weekday_schedule", data_schema=schema)

    async def async_step_weekend_schedule(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Modify Saturday - Sunday 4-Slot Schedule."""
        if user_input is not None:
            self._options.update(user_input)
            return self.async_create_entry(title="", data=self._options)

        cfg = self._options
        schema = vol.Schema(
            {
                vol.Required(CONF_WE_P1_TIME, default=cfg.get(CONF_WE_P1_TIME, DEFAULT_WE_P1_TIME)): selector.TimeSelector(),
                vol.Required(CONF_WE_P1_PRESET, default=cfg.get(CONF_WE_P1_PRESET, DEFAULT_WE_P1_PRESET)): selector.SelectSelector(
                    selector.SelectSelectorConfig(options=PRESET_OPTIONS)
                ),
                vol.Required(CONF_WE_P2_TIME, default=cfg.get(CONF_WE_P2_TIME, DEFAULT_WE_P2_TIME)): selector.TimeSelector(),
                vol.Required(CONF_WE_P2_PRESET, default=cfg.get(CONF_WE_P2_PRESET, DEFAULT_WE_P2_PRESET)): selector.SelectSelector(
                    selector.SelectSelectorConfig(options=PRESET_OPTIONS)
                ),
                vol.Required(CONF_WE_P3_TIME, default=cfg.get(CONF_WE_P3_TIME, DEFAULT_WE_P3_TIME)): selector.TimeSelector(),
                vol.Required(CONF_WE_P3_PRESET, default=cfg.get(CONF_WE_P3_PRESET, DEFAULT_WE_P3_PRESET)): selector.SelectSelector(
                    selector.SelectSelectorConfig(options=PRESET_OPTIONS)
                ),
                vol.Required(CONF_WE_P4_TIME, default=cfg.get(CONF_WE_P4_TIME, DEFAULT_WE_P4_TIME)): selector.TimeSelector(),
                vol.Required(CONF_WE_P4_PRESET, default=cfg.get(CONF_WE_P4_PRESET, DEFAULT_WE_P4_PRESET)): selector.SelectSelector(
                    selector.SelectSelectorConfig(options=PRESET_OPTIONS)
                ),
            }
        )
        return self.async_show_form(step_id="weekend_schedule", data_schema=schema)

    async def async_step_presence_timers(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Modify Errand Grace Delay and Away Immunity Window."""
        if user_input is not None:
            self._options.update(user_input)
            return self.async_create_entry(title="", data=self._options)

        cfg = self._options
        schema = vol.Schema(
            {
                vol.Required(CONF_ERRAND_DELAY, default=cfg.get(CONF_ERRAND_DELAY, DEFAULT_ERRAND_DELAY)): vol.Coerce(int),
                vol.Required(CONF_IMMUNITY_DURATION, default=cfg.get(CONF_IMMUNITY_DURATION, DEFAULT_IMMUNITY_DURATION)): vol.Coerce(int),
            }
        )
        return self.async_show_form(step_id="presence_timers", data_schema=schema)

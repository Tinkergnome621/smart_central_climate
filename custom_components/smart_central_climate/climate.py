"""Climate platform for Smart Central Climate with Built-in 4-Slot Scheduling and Vacation Mode."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.components.climate.const import (
    PRESET_AWAY,
    PRESET_BOOST,
    PRESET_COMFORT,
    PRESET_ECO,
    PRESET_NONE,
    PRESET_SLEEP,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_ENTITY_ID,
    ATTR_TEMPERATURE,
    CONF_NAME,
    EVENT_HOMEASSISTANT_START,
    STATE_HOME,
    STATE_NOT_HOME,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
    UnitOfTemperature,
)
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.event import (
    async_call_later,
    async_track_state_change_event,
    async_track_time_change,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import (
    CONF_AWAY_COOL,
    CONF_AWAY_HEAT,
    CONF_BOOST_COOL,
    CONF_BOOST_HEAT,
    CONF_COMFORT_COOL,
    CONF_COMFORT_HEAT,
    CONF_COOLING_SWING,
    CONF_ECO_COOL,
    CONF_ECO_HEAT,
    CONF_ENABLE_SCHEDULE,
    CONF_ERRAND_DELAY,
    CONF_FAN_ENTITY,
    CONF_HEATING_SWING,
    CONF_IMMUNITY_DURATION,
    CONF_PRESENCE_SENSOR,
    CONF_SLEEP_COOL,
    CONF_SLEEP_HEAT,
    CONF_TARGET_CLIMATE,
    CONF_TEMP_SENSOR,
    CONF_VACATION_COOL,
    CONF_VACATION_HEAT,
    CONF_WD_P1_PRESET,
    CONF_WD_P1_TIME,
    CONF_WD_P2_PRESET,
    CONF_WD_P2_TIME,
    CONF_WD_P3_PRESET,
    CONF_WD_P3_TIME,
    CONF_WD_P4_PRESET,
    CONF_WD_P4_TIME,
    CONF_WE_P1_PRESET,
    CONF_WE_P1_TIME,
    CONF_WE_P2_PRESET,
    CONF_WE_P2_TIME,
    CONF_WE_P3_PRESET,
    CONF_WE_P3_TIME,
    CONF_WE_P4_PRESET,
    CONF_WE_P4_TIME,
    DEFAULT_AWAY_COOL,
    DEFAULT_AWAY_HEAT,
    DEFAULT_BOOST_COOL,
    DEFAULT_BOOST_HEAT,
    DEFAULT_COMFORT_COOL,
    DEFAULT_COMFORT_HEAT,
    DEFAULT_COOLING_SWING,
    DEFAULT_ECO_COOL,
    DEFAULT_ECO_HEAT,
    DEFAULT_ENABLE_SCHEDULE,
    DEFAULT_ERRAND_DELAY,
    DEFAULT_HEATING_SWING,
    DEFAULT_IMMUNITY_DURATION,
    DEFAULT_SLEEP_COOL,
    DEFAULT_SLEEP_HEAT,
    DEFAULT_VACATION_COOL,
    DEFAULT_VACATION_HEAT,
    DEFAULT_WD_P1_PRESET,
    DEFAULT_WD_P1_TIME,
    DEFAULT_WD_P2_PRESET,
    DEFAULT_WD_P2_TIME,
    DEFAULT_WD_P3_PRESET,
    DEFAULT_WD_P3_TIME,
    DEFAULT_WD_P4_PRESET,
    DEFAULT_WD_P4_TIME,
    DEFAULT_WE_P1_PRESET,
    DEFAULT_WE_P1_TIME,
    DEFAULT_WE_P2_PRESET,
    DEFAULT_WE_P2_TIME,
    DEFAULT_WE_P3_PRESET,
    DEFAULT_WE_P3_TIME,
    DEFAULT_WE_P4_PRESET,
    DEFAULT_WE_P4_TIME,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

PRESET_VACATION = "vacation"

SUPPORTED_PRESETS = [
    PRESET_COMFORT,
    PRESET_ECO,
    PRESET_AWAY,
    PRESET_SLEEP,
    PRESET_BOOST,
    PRESET_VACATION,
    PRESET_NONE,
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Smart Central Climate entity."""
    entity = SmartCentralClimate(hass, entry)
    async_add_entities([entity])


class SmartCentralClimate(ClimateEntity):
    """Unified smart central A/C and heating entity with safe compressor logic and scheduling."""

    _attr_has_entity_name = True
    _attr_temperature_unit = UnitOfTemperature.FAHRENHEIT

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the climate entity."""
        self.hass = hass
        self.entry = entry

        # Configuration & Options merged
        cfg = {**entry.data, **entry.options}
        self._name = cfg.get(CONF_NAME, "Smart Central A/C")
        self._attr_unique_id = f"{entry.entry_id}_climate"
        self._attr_name = self._name

        self._target_climate: str = cfg[CONF_TARGET_CLIMATE]
        self._fan_entity: str | None = cfg.get(CONF_FAN_ENTITY)
        self._temp_sensor: str = cfg[CONF_TEMP_SENSOR]
        self._presence_sensor: str | None = cfg.get(CONF_PRESENCE_SENSOR)

        # Swings & Timers
        self._cooling_swing: float = float(cfg.get(CONF_COOLING_SWING, DEFAULT_COOLING_SWING))
        self._heating_swing: float = float(cfg.get(CONF_HEATING_SWING, DEFAULT_HEATING_SWING))
        self._errand_delay: int = int(cfg.get(CONF_ERRAND_DELAY, DEFAULT_ERRAND_DELAY))
        self._immunity_duration: int = int(cfg.get(CONF_IMMUNITY_DURATION, DEFAULT_IMMUNITY_DURATION))

        # Presets mapping (mode -> preset -> target)
        self._preset_targets: dict[str, dict[str, float]] = {
            HVACMode.COOL: {
                PRESET_COMFORT: float(cfg.get(CONF_COMFORT_COOL, DEFAULT_COMFORT_COOL)),
                PRESET_ECO: float(cfg.get(CONF_ECO_COOL, DEFAULT_ECO_COOL)),
                PRESET_AWAY: float(cfg.get(CONF_AWAY_COOL, DEFAULT_AWAY_COOL)),
                PRESET_SLEEP: float(cfg.get(CONF_SLEEP_COOL, DEFAULT_SLEEP_COOL)),
                PRESET_BOOST: float(cfg.get(CONF_BOOST_COOL, DEFAULT_BOOST_COOL)),
                PRESET_VACATION: float(cfg.get(CONF_VACATION_COOL, DEFAULT_VACATION_COOL)),
            },
            HVACMode.HEAT: {
                PRESET_COMFORT: float(cfg.get(CONF_COMFORT_HEAT, DEFAULT_COMFORT_HEAT)),
                PRESET_ECO: float(cfg.get(CONF_ECO_HEAT, DEFAULT_ECO_HEAT)),
                PRESET_AWAY: float(cfg.get(CONF_AWAY_HEAT, DEFAULT_AWAY_HEAT)),
                PRESET_SLEEP: float(cfg.get(CONF_SLEEP_HEAT, DEFAULT_SLEEP_HEAT)),
                PRESET_BOOST: float(cfg.get(CONF_BOOST_HEAT, DEFAULT_BOOST_HEAT)),
                PRESET_VACATION: float(cfg.get(CONF_VACATION_HEAT, DEFAULT_VACATION_HEAT)),
            },
        }

        # Scheduling Configuration
        self._enable_schedule: bool = cfg.get(CONF_ENABLE_SCHEDULE, DEFAULT_ENABLE_SCHEDULE)
        self._wd_slots = [
            (cfg.get(CONF_WD_P1_TIME, DEFAULT_WD_P1_TIME), cfg.get(CONF_WD_P1_PRESET, DEFAULT_WD_P1_PRESET)),
            (cfg.get(CONF_WD_P2_TIME, DEFAULT_WD_P2_TIME), cfg.get(CONF_WD_P2_PRESET, DEFAULT_WD_P2_PRESET)),
            (cfg.get(CONF_WD_P3_TIME, DEFAULT_WD_P3_TIME), cfg.get(CONF_WD_P3_PRESET, DEFAULT_WD_P3_PRESET)),
            (cfg.get(CONF_WD_P4_TIME, DEFAULT_WD_P4_TIME), cfg.get(CONF_WD_P4_PRESET, DEFAULT_WD_P4_PRESET)),
        ]
        self._we_slots = [
            (cfg.get(CONF_WE_P1_TIME, DEFAULT_WE_P1_TIME), cfg.get(CONF_WE_P1_PRESET, DEFAULT_WE_P1_PRESET)),
            (cfg.get(CONF_WE_P2_TIME, DEFAULT_WE_P2_TIME), cfg.get(CONF_WE_P2_PRESET, DEFAULT_WE_P2_PRESET)),
            (cfg.get(CONF_WE_P3_TIME, DEFAULT_WE_P3_TIME), cfg.get(CONF_WE_P3_PRESET, DEFAULT_WE_P3_PRESET)),
            (cfg.get(CONF_WE_P4_TIME, DEFAULT_WE_P4_TIME), cfg.get(CONF_WE_P4_PRESET, DEFAULT_WE_P4_PRESET)),
        ]
        self._last_scheduled_slot: str | None = None

        # Internal State
        self._hvac_mode: HVACMode = HVACMode.COOL
        self._hvac_action: HVACAction = HVACAction.IDLE
        self._preset_mode: str = PRESET_COMFORT
        self._target_temperature: float = self._preset_targets[HVACMode.COOL][PRESET_COMFORT]
        self._current_temperature: float | None = None

        # Errand & Immunity Timers
        self._errand_timer_cancel: Any = None
        self._errand_timer_end: datetime | None = None
        self._immunity_timer_cancel: Any = None
        self._immunity_timer_end: datetime | None = None

        # Guard against recursive sync loops
        self._last_internal_command_time: datetime | None = None

    @property
    def supported_features(self) -> ClimateEntityFeature:
        """Supported features."""
        return (
            ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.PRESET_MODE
            | ClimateEntityFeature.TURN_ON
            | ClimateEntityFeature.TURN_OFF
        )

    @property
    def hvac_modes(self) -> list[HVACMode]:
        """Available HVAC modes."""
        return [HVACMode.OFF, HVACMode.COOL, HVACMode.HEAT]

    @property
    def preset_modes(self) -> list[str]:
        """Available preset modes."""
        return SUPPORTED_PRESETS

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current HVAC mode."""
        return self._hvac_mode

    @property
    def hvac_action(self) -> HVACAction:
        """Return current HVAC action."""
        return self._hvac_action

    @property
    def preset_mode(self) -> str:
        """Return current preset mode."""
        return self._preset_mode

    @property
    def current_temperature(self) -> float | None:
        """Return current temperature from the remote sensor helper."""
        return self._current_temperature

    @property
    def target_temperature(self) -> float:
        """Return target temperature."""
        return self._target_temperature

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra diagnostic, schedule, and timer attributes."""
        now = dt_util.utcnow()
        errand_remaining = 0
        if self._errand_timer_end and self._errand_timer_end > now:
            errand_remaining = int((self._errand_timer_end - now).total_seconds() / 60)

        immunity_remaining = 0
        if self._immunity_timer_end and self._immunity_timer_end > now:
            immunity_remaining = int((self._immunity_timer_end - now).total_seconds() / 60)

        return {
            "remote_sensor": self._temp_sensor,
            "target_climate": self._target_climate,
            "fan_entity": self._fan_entity,
            "schedule_enabled": self._enable_schedule,
            "last_schedule_slot": self._last_scheduled_slot,
            "vacation_mode": self._preset_mode == PRESET_VACATION,
            "errand_grace_active": self._errand_timer_cancel is not None,
            "errand_minutes_remaining": errand_remaining,
            "immunity_active": self._immunity_timer_cancel is not None,
            "immunity_minutes_remaining": immunity_remaining,
            "cooling_swing": self._cooling_swing,
            "heating_swing": self._heating_swing,
        }

    async def async_added_to_hass(self) -> None:
        """Register listeners when added to Home Assistant."""
        await super().async_added_to_hass()

        # Track temperature sensor changes
        self.async_on_remove(
            async_track_state_change_event(
                self.hass, [self._temp_sensor], self._async_temp_sensor_changed
            )
        )

        # Track physical thermostat changes (two-way sync)
        self.async_on_remove(
            async_track_state_change_event(
                self.hass, [self._target_climate], self._async_target_climate_changed
            )
        )

        # Track presence sensor changes (if configured)
        if self._presence_sensor:
            self.async_on_remove(
                async_track_state_change_event(
                    self.hass, [self._presence_sensor], self._async_presence_changed
                )
            )

        # Minute-by-minute schedule evaluation
        if self._enable_schedule:
            self.async_on_remove(
                async_track_time_change(self.hass, self._async_check_schedule, second=0)
            )

        # Read initial temperature
        state = self.hass.states.get(self._temp_sensor)
        if state and state.state not in (STATE_UNKNOWN, STATE_UNAVAILABLE):
            try:
                self._current_temperature = float(state.state)
            except ValueError:
                pass

        # Trigger initial regulation once HA is fully started
        @callback
        def _async_startup(_: Event) -> None:
            self.hass.async_create_task(self._async_evaluate_regulation())

        self.hass.bus.async_listen_once(EVENT_HOMEASSISTANT_START, _async_startup)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new HVAC mode."""
        if hvac_mode not in self.hvac_modes:
            return

        self._hvac_mode = hvac_mode

        if hvac_mode == HVACMode.OFF:
            self._hvac_action = HVACAction.OFF
            await self._async_call_physical_off()
        else:
            if self._preset_mode in self._preset_targets.get(hvac_mode, {}):
                self._target_temperature = self._preset_targets[hvac_mode][self._preset_mode]
            await self._async_evaluate_regulation()

        self.async_write_ha_state()

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature manually."""
        temp = kwargs.get(ATTR_TEMPERATURE)
        if temp is None:
            return

        self._target_temperature = float(temp)
        self._preset_mode = PRESET_NONE
        await self._async_evaluate_regulation()
        self.async_write_ha_state()

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""
        if preset_mode not in SUPPORTED_PRESETS:
            return

        self._preset_mode = preset_mode

        # If entering Comfort mode, start 60-minute Away Immunity Window
        if preset_mode == PRESET_COMFORT:
            self._async_start_immunity_window()

        # If entering Vacation mode, cancel any active errand timers
        if preset_mode == PRESET_VACATION:
            if self._errand_timer_cancel:
                self._errand_timer_cancel()
                self._errand_timer_cancel = None
                self._errand_timer_end = None

        # Update setpoint from preset if mode is Cool or Heat
        if self._hvac_mode in (HVACMode.COOL, HVACMode.HEAT):
            if preset_mode in self._preset_targets[self._hvac_mode]:
                self._target_temperature = self._preset_targets[self._hvac_mode][preset_mode]

        await self._async_evaluate_regulation()
        self.async_write_ha_state()

    # --------------------------------------------------------------------------
    # Scheduling Engine (4 Mon-Fri Slots, 4 Sat-Sun Slots)
    # --------------------------------------------------------------------------

    async def _async_check_schedule(self, now: datetime) -> None:
        """Evaluate schedules every minute."""
        # If schedule disabled, or in Vacation Mode, skip schedule!
        if not self._enable_schedule or self._preset_mode == PRESET_VACATION:
            return

        # Local time formatting HH:MM
        local_now = dt_util.as_local(now)
        current_time_str = local_now.strftime("%H:%M")
        weekday = local_now.weekday()  # 0=Mon, 4=Fri, 5=Sat, 6=Sun

        active_slots = self._wd_slots if weekday < 5 else self._we_slots
        day_type = "Weekday" if weekday < 5 else "Weekend"

        for idx, (slot_time, slot_preset) in enumerate(active_slots, start=1):
            if current_time_str == slot_time:
                slot_name = f"{day_type} Slot {idx} ({slot_time})"
                if self._last_scheduled_slot != slot_name:
                    _LOGGER.info("Schedule triggered: %s -> setting preset %s", slot_name, slot_preset)
                    self._last_scheduled_slot = slot_name
                    await self.async_set_preset_mode(slot_preset)
                break

    # --------------------------------------------------------------------------
    # Core Regulation Engine (Hysteresis & Blower Fan Control)
    # --------------------------------------------------------------------------

    async def _async_evaluate_regulation(self) -> None:
        """Evaluate temperature and control the physical thermostat and fan."""
        if self._hvac_mode == HVACMode.OFF or self._current_temperature is None:
            if self._hvac_mode == HVACMode.OFF:
                await self._async_call_physical_off()
            return

        now = dt_util.utcnow()
        self._last_internal_command_time = now

        # --- COOLING MODE ---
        if self._hvac_mode == HVACMode.COOL:
            activate_temp = self._target_temperature + self._cooling_swing
            deactivate_temp = self._target_temperature - self._cooling_swing

            if self._current_temperature >= activate_temp:
                # Cooling needed!
                self._hvac_action = HVACAction.COOLING
                await self._async_call_physical_cooling(self._target_temperature)
            elif self._current_temperature <= deactivate_temp:
                # Target achieved! Shut off compressor AND fan completely!
                self._hvac_action = HVACAction.IDLE
                await self._async_call_physical_off()

        # --- HEATING MODE ---
        elif self._hvac_mode == HVACMode.HEAT:
            activate_temp = self._target_temperature - self._heating_swing
            deactivate_temp = self._target_temperature + self._heating_swing

            if self._current_temperature <= activate_temp:
                # Heating needed!
                self._hvac_action = HVACAction.HEATING
                await self._async_call_physical_heating(self._target_temperature)
            elif self._current_temperature >= deactivate_temp:
                # Target achieved! Shut off furnace AND fan completely!
                self._hvac_action = HVACAction.IDLE
                await self._async_call_physical_off()

        self.async_write_ha_state()

    async def _async_call_physical_cooling(self, target_temp: float) -> None:
        """Command physical thermostat to Cool and ensure fan is active."""
        _LOGGER.debug("Calling physical thermostat %s for COOLING at %s°F", self._target_climate, target_temp)
        await self.hass.services.async_call(
            "climate",
            "set_hvac_mode",
            {ATTR_ENTITY_ID: self._target_climate, "hvac_mode": HVACMode.COOL},
            blocking=False,
        )
        await self.hass.services.async_call(
            "climate",
            "set_temperature",
            {ATTR_ENTITY_ID: self._target_climate, ATTR_TEMPERATURE: target_temp},
            blocking=False,
        )
        if self._fan_entity:
            await self.hass.services.async_call(
                "fan", "turn_on", {ATTR_ENTITY_ID: self._fan_entity}, blocking=False
            )

    async def _async_call_physical_heating(self, target_temp: float) -> None:
        """Command physical thermostat to Heat."""
        _LOGGER.debug("Calling physical thermostat %s for HEATING at %s°F", self._target_climate, target_temp)
        await self.hass.services.async_call(
            "climate",
            "set_hvac_mode",
            {ATTR_ENTITY_ID: self._target_climate, "hvac_mode": HVACMode.HEAT},
            blocking=False,
        )
        await self.hass.services.async_call(
            "climate",
            "set_temperature",
            {ATTR_ENTITY_ID: self._target_climate, ATTR_TEMPERATURE: target_temp},
            blocking=False,
        )

    async def _async_call_physical_off(self) -> None:
        """Shut off physical thermostat AND stop the fan completely."""
        _LOGGER.debug("Calling physical thermostat %s to turn OFF and stop fan", self._target_climate)
        await self.hass.services.async_call(
            "climate",
            "set_hvac_mode",
            {ATTR_ENTITY_ID: self._target_climate, "hvac_mode": HVACMode.OFF},
            blocking=False,
        )
        if self._fan_entity:
            await self.hass.services.async_call(
                "fan", "turn_off", {ATTR_ENTITY_ID: self._fan_entity}, blocking=False
            )

    # --------------------------------------------------------------------------
    # Event Listeners (Sensor, Physical Thermostat, Presence)
    # --------------------------------------------------------------------------

    async def _async_temp_sensor_changed(self, event: Event) -> None:
        """Handle temperature updates from remote sensor helper."""
        new_state = event.data.get("new_state")
        if not new_state or new_state.state in (STATE_UNKNOWN, STATE_UNAVAILABLE):
            return

        try:
            self._current_temperature = float(new_state.state)
            await self._async_evaluate_regulation()
        except ValueError:
            pass

    async def _async_target_climate_changed(self, event: Event) -> None:
        """Two-way sync: Handle physical thermostat dial turns."""
        now = dt_util.utcnow()
        if self._last_internal_command_time and (now - self._last_internal_command_time).total_seconds() < 10:
            return

        new_state = event.data.get("new_state")
        if not new_state or new_state.state in (STATE_UNKNOWN, STATE_UNAVAILABLE):
            return

        # If user turned off physical thermostat on the wall
        if new_state.state == HVACMode.OFF and self._hvac_mode != HVACMode.OFF:
            self._hvac_mode = HVACMode.OFF
            self._hvac_action = HVACAction.OFF
            self.async_write_ha_state()
            return

        # If user turned on dial or adjusted target temperature
        target_temp = new_state.attributes.get(ATTR_TEMPERATURE)
        if target_temp is not None:
            try:
                new_target = float(target_temp)
                if abs(new_target - self._target_temperature) >= 0.5:
                    _LOGGER.info("Physical thermostat dial adjusted to %s°F. Syncing.", new_target)
                    self._target_temperature = new_target
                    self._preset_mode = PRESET_NONE
                    await self._async_evaluate_regulation()
            except ValueError:
                pass

    async def _async_presence_changed(self, event: Event) -> None:
        """Smart Away: Handle 1-hour errand grace period and away transitions."""
        # If in Vacation Mode, presence does not alter thermostat!
        if self._preset_mode == PRESET_VACATION:
            return

        new_state = event.data.get("new_state")
        old_state = event.data.get("old_state")
        if not new_state or not old_state:
            return

        # User left home -> Start 1-Hour Errand Grace Timer
        if old_state.state == STATE_HOME and new_state.state != STATE_HOME:
            if self._immunity_timer_cancel is not None:
                _LOGGER.info("Pre-cooling immunity is active. Ignoring away transition.")
                return

            _LOGGER.info("User left home. Starting %d minute errand grace period.", self._errand_delay)
            self._errand_timer_end = dt_util.utcnow() + timedelta(minutes=self._errand_delay)

            @callback
            def _async_errand_expired(_: datetime) -> None:
                self._errand_timer_cancel = None
                self._errand_timer_end = None
                current_p = self.hass.states.get(self._presence_sensor) if self._presence_sensor else None
                if current_p and current_p.state != STATE_HOME:
                    _LOGGER.info("Errand timer expired. Applying Away preset.")
                    self.hass.async_create_task(self.async_set_preset_mode(PRESET_AWAY))

            self._errand_timer_cancel = async_call_later(
                self.hass, self._errand_delay * 60, _async_errand_expired
            )
            self.async_write_ha_state()

        # User returned home -> Cancel errand timer, restore Comfort
        elif new_state.state == STATE_HOME and old_state.state != STATE_HOME:
            if self._errand_timer_cancel:
                _LOGGER.info("User returned before errand timer expired. Canceling errand timer.")
                self._errand_timer_cancel()
                self._errand_timer_cancel = None
                self._errand_timer_end = None

            if self._preset_mode == PRESET_AWAY:
                _LOGGER.info("User returned home. Restoring Comfort preset.")
                await self.async_set_preset_mode(PRESET_COMFORT)

            self.async_write_ha_state()

    def _async_start_immunity_window(self) -> None:
        """Start 60-minute Away Immunity Window when entering Comfort mode."""
        if self._immunity_timer_cancel:
            self._immunity_timer_cancel()

        _LOGGER.info("Starting %d minute Away Immunity Window for Pre-Cooling.", self._immunity_duration)
        self._immunity_timer_end = dt_util.utcnow() + timedelta(minutes=self._immunity_duration)

        @callback
        def _async_immunity_expired(_: datetime) -> None:
            self._immunity_timer_cancel = None
            self._immunity_timer_end = None
            _LOGGER.info("Pre-cooling immunity window expired.")
            self.async_write_ha_state()

        self._immunity_timer_cancel = async_call_later(
            self.hass, self._immunity_duration * 60, _async_immunity_expired
        )

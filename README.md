# Smart Central Climate

A custom Home Assistant integration designed specifically for **Central A/C and Heat Pump Systems**. It wraps your physical smart thermostat (like Meross Matter, Nest, Ecobee, Honeywell, Z-Wave) and links it with remote room temperature sensors, smart presence grace periods, built-in 4-slot daily schedules, vacation mode, compressor protection, and 3-tier failsafe regulation.

---

## Key Features

* 🛡️ **3-Tier Sensor Safety & Hardware Failover:**
  * **Tier 1 (Normal):** Regulates HVAC based on your primary remote sensor (e.g. `sensor.average_house_temperature`).
  * **Tier 2 (Auto-Failover):** If your remote sensor ever goes `unavailable`, `unknown`, or stops reporting for >45 minutes, the integration automatically falls back to reading ambient temperature directly from your physical thermostat's built-in probe.
  * **Tier 3 (Graceful Degradation):** If both sensors fail, control is handed over to the physical thermostat at your exact target setpoint with 0°F offset. Your heating or cooling will **never** freeze or shut down unexpectedly.
* ⚡ **Decoupled Offsets & Heat Pump Aux Protection:**
  * **Cooling Dynamic Offset (Default: 3.0°F):** Ensures your hallway thermostat doesn't shut off before the rest of your house reaches target temperature. Completely safe with zero Aux heat risk.
  * **Heating Dynamic Offset (Default: 1.0°F):** Limits the heating offset so the delta to your heat pump stays below 3.0°F, **preventing expensive auxiliary electric resistance heat strips** from engaging.
* 🛡️ **Compressor Protection (Short-Cycle Prevention):** Enforces a configurable 5-minute minimum cycle run-time and off-time (`min_cycle_duration`). Protects compressor motors against premature wear and high head-pressure starts.
* 🌡️ **True 1-Sided A/C Hysteresis:** Unlike generic dual-sided swings that freeze your home, cooling activates at `Target + Swing` (e.g. 74°F) and turns off at the exact target setpoint (72°F).
* 🛑 **Native HVAC Fan Management (Auto by Default):** Allows the HVAC air handler / furnace board to cycle the blower automatically with the compressor over the Y wire. When idle, ensures any separate fan entity (`fan.*`) is switched off so the blower is never stuck running 24/7.
* 📅 **Built-in 4-Slot Daily Schedules:**
  * **Monday – Friday (4 Periods):** e.g., Wake (06:30), Work/Day (08:30), Return/Pre-Cool (17:00), Night/Sleep (22:30).
  * **Saturday – Sunday (4 Periods):** e.g., Wake (08:00), Day (11:00), Evening (17:30), Night/Sleep (23:00).
  * Automatically catches up to the correct slot on startup, respects manual holds and away states, and safely wraps around across midnight.
* ✈️ **Dedicated Vacation Mode:**
  * One-tap Vacation preset and dedicated toggle switch (`switch.<integration_name>_vacation_mode`).
  * Suspends all schedules, presence triggers, and errand timers while maintaining deep energy-saving vacation hold temperatures (e.g. Cool: 82°F / Heat: 58°F). Turning the switch off automatically resumes the schedule slot for the current time of day.
* 🤝 **Two-Way Wall Dial Sync & Season Changeover:** If someone physically turns the dial on the wall unit or flips the wall switch between Heat and Cool, `smart_central_climate` catches the change and syncs its state cleanly without fighting back.
* ⏱️ **Smart Away (Errand Grace Period):** Leaving home starts a configurable grace timer (default: 60 minutes). Quick trips to the grocery store will not disrupt your A/C; only if you remain away does it shift to Away setpoints.
* 🛡️ **Pre-Cooling Schedule Immunity:** When your schedule triggers Comfort mode (e.g. at 17:00 / 5 PM), cooling engages and activates an Away Immunity Window (default: 60 minutes). Away presence checks are locked out so your home is chilled before you arrive.
* 🔔 **Configurable Notification Triggers & Alerts (v1.4.0):**
  * Individually toggle notifications on or off for:
    * **HVAC Mode Changes:** Switched between Cool, Heat, or Off (including manual switchovers at the wall).
    * **Preset Changes:** Shifts to Comfort, Eco, Away, Sleep, Boost, or Vacation.
    * **Schedule Transitions:** Automated 4-slot daily period changes.
    * **Presence & Errand Actions:** Errand grace timer start, auto-Away activations, and Welcome Home returns.
    * **Sensor Fallback Warnings:** Stale remote sensor warnings, failover to wall thermostat, recovery alerts, and Tier 3 emergency notifications.
  * **Target Service Selection:** Defaults to `notify.persistent_notification` (appears in HA's notification center), or route to your smartphone via `notify.mobile_app_phone` or `notify.notify`.
  * **Native Event Bus:** Simultaneously fires `smart_central_climate_notification` events for building custom automations.
* 🎛️ **Full UI Configuration & Options Flow:** Set up directly in the Home Assistant UI, and adjust any setpoint, schedule slot, swing, offset, timer, or notification trigger at any time under **Settings > Devices & Services > Configure**. Fully compatible with voice assistants and Lovelace power buttons via `climate.turn_on` and `climate.turn_off`.

---

## Best Practice: Setting Up Your Average House Temperature Helper

For the most reliable temperature tracking, create a **Min/Max (Mean) Helper** in Home Assistant:
1. Go to **Settings > Devices & Services > Helpers > Create Helper > Combine the state of several sensors (Min/Max)**.
2. Select **Statistical characteristic:** `Mean` (Average).
3. Select your room sensors (e.g. Living Room, Bedroom, Office).
4. **Important Best Practice:** Also include your **physical thermostat's temperature sensor** in this list!
   * Because your wall thermostat is hardwired to 24V power from your furnace/air handler C-wire, its sensor will never die.
   * If battery-powered room sensors drop offline, Home Assistant's `mean` helper automatically ignores the offline sensors and calculates the average from the remaining active ones. Your average helper will never drop offline!

---

## Installation via HACS

1. Open Home Assistant > **HACS** > **Integrations**.
2. Click the three dots in the top right > **Custom repositories**.
3. Paste your repository URL: `https://github.com/Tinkergnome621/smart_central_climate`.
4. Category: **Integration** > Click **Add**.
5. Find **Smart Central Climate** in HACS and click **Download** (select version `v1.4.0`).
6. Restart Home Assistant.

---

## Setup in Home Assistant

1. Go to **Settings** > **Devices & Services** > **Add Integration**.
2. Search for **Smart Central Climate**.
3. Select your entities:
   * **Physical Thermostat:** (e.g., `climate.hallway_thermostat`)
   * **Blower Fan Entity (Optional):** (e.g., `fan.hallway_thermostat`)
   * **Remote Temperature Sensor:** (e.g., `sensor.average_house_temperature`)
   * **Presence Sensor (Optional):** (e.g., `person.your_name`)
4. Confirm your default temperatures, swings, offsets, and vacation hold setpoints.
5. Set your **4 Weekday** and **4 Weekend** schedule slots.
6. Configure your **Notification Triggers & Target Service**.
7. Click **Submit**.

---

## Adjusting Schedules, Settings & Notifications Anytime

You never need to edit YAML or reinstall. In Home Assistant:
1. Go to **Settings** > **Devices & Services**.
2. Find **Smart Central Climate** and click **Configure**.
3. Choose what to modify:
   * **Temperature Presets, Swings & Offsets**
   * **Monday – Friday Schedule (4 Slots)**
   * **Saturday – Sunday Schedule (4 Slots)**
   * **Presence, Timers & Safety**
   * **Notification Triggers & Alerts**
4. Adjust and click **Submit**.

---

## 📋 Diagnostic Telemetry & State-Change Logging

To provide full visibility during testing and operation, the integration logs structured diagnostics at the `INFO` level. Because Home Assistant only records `WARNING` and above in the system logs by default, add the following to your `configuration.yaml` and restart Home Assistant to view them under **Settings > System > Logs**:

```yaml
logger:
  default: warning
  logs:
    custom_components.smart_central_climate: info
```

> **Tip:** You can also temporarily view detailed logs without editing YAML by navigating to **Settings > Devices & Services > Smart Central Climate**, clicking the three dots menu (**⋮**), and selecting **Enable debug logging**. When disabled, Home Assistant will prompt you to download the captured log file.

* **5-Minute Telemetry Snapshot (`[TEST LOG][5-MINUTE HEARTBEAT]`):**
  Logs effective room temperature, remote sensor reading, wall thermostat ambient probe, target setpoints, active dynamic offsets, system mode & action, physical hardware state, compressor run/dwell times, schedule slots, and presence timers.
* **State Change Rationale (`[TEST LOG][STATE CHANGE]`):**
  Every change to HVAC Mode, HVAC Action, Target Temperature, Preset, or Sensor Fallback logs both the old and new state along with the precise reason/trigger that caused the transition.
* **HVAC Start / Stop Events (`[TEST LOG][HVAC START]` & `[TEST LOG][HVAC STOP]`):**
  Explicitly logs when cooling or heating cycles start and stop, including active activation/satisfaction thresholds, cycle runtime durations, and setpoints.
* **Cycle Delays & Safety Guards (`[TEST LOG][CYCLE DELAY]` & `[FREEZE GUARD]`):**
  Logs when heating or cooling demand is held by anti-short-cycle dwell times or minimum runtime safety locks, as well as emergency shutdowns if room temperature drops below the hard safety limit (65.0°F).

---

## 🛡️ Emergency Freeze Protection & Dial Safety (v1.4.2+)

* **Hard Low-Temperature Freeze Cutoff:** If cooling is active and the room or average house temperature reaches **65.0°F (18.3°C)** or lower, cooling is unconditionally aborted immediately to protect household comfort and prevent frozen evaporator coils.
* **Dial Sync Echo Suppression:** Built-in 15-second command suppression window prevents physical thermostat echo loops from misinterpreting internal hardware offset targets as manual user adjustments.
* **Startup Safe Bounds Auto-Healing:** Target setpoints are strictly bounded between 60.0°F and 85.0°F. If an out-of-bounds setpoint was previously saved to Home Assistant storage, the integration automatically heals and restores it to safe preset defaults upon startup.
* **Manual Holds Preserved Across Restarts:** Full support for `PRESET_NONE` ensures hand-adjusted setpoints or wall-dial turns persist safely across reboots and option updates without being overridden by daily schedules.
* **Streamlined Notifications:** Preset change notifications default to disabled to prevent alert fatigue, duplicate notifications during presence/errand transitions are eliminated, and target services without the `notify.` prefix are auto-normalized with service registry validation.



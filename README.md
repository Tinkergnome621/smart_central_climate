# Smart Central Climate

A custom Home Assistant integration designed specifically for **Central A/C and Heat Pump Systems**. It wraps your physical smart thermostat (like Meross Matter, Nest, Ecobee, Honeywell, Z-Wave) and links it with remote room temperature sensors, smart presence grace periods, built-in 4-slot daily schedules, vacation mode, compressor protection, and HVAC-safe regulation.

---

## Key Features

* 🛡️ **Compressor Protection (Short-Cycle Prevention):** Enforces a configurable 5-minute minimum cycle run-time and off-time (`min_cycle_duration`). Protects compressor motors against premature wear and high head-pressure starts.
* 🌡️ **True 1-Sided A/C Hysteresis:** Unlike generic dual-sided swings that freeze your home, cooling activates at `Target + Swing` (e.g. 74°F) and turns off at the exact target setpoint (72°F).
* ⚡ **Heat Pump Safe (Aux Heat Prevention):** Applies a safe, dynamic $1.5^\circ\text{F}$ offset clamped to the thermostat's advertised min/max limits. Never commands large temperature jumps that would trigger expensive auxiliary electric resistance heat strips.
* 🛑 **Native HVAC Fan Management (Auto by Default):** Allows the HVAC air handler / furnace board to cycle the blower automatically with the compressor over the Y wire. When idle, ensures any separate fan entity (`fan.*`) is switched off so the blower is never stuck running 24/7.
* 🐕 **Safety Watchdog (Failsafe Protection):** Actively monitors your remote temperature sensor. If the sensor goes unavailable or stops reporting for more than 20 minutes while active, the integration automatically idles the HVAC system to prevent runaway cooling or heating.
* 📅 **Built-in 4-Slot Daily Schedules:**
  * **Monday – Friday (4 Periods):** e.g., Wake (06:30), Work/Day (08:30), Return/Pre-Cool (17:00), Night/Sleep (22:30).
  * **Saturday – Sunday (4 Periods):** e.g., Wake (08:00), Day (11:00), Evening (17:30), Night/Sleep (23:00).
  * Automatically catches up to the correct slot on startup, respects manual holds, and safely wraps around across midnight (including Friday night to Saturday morning transitions).
* ✈️ **Dedicated Vacation Mode:**
  * One-tap Vacation preset and dedicated toggle switch (`switch.vacation_mode`).
  * Suspends all schedules, presence triggers, and errand timers while maintaining deep energy-saving vacation hold temperatures (e.g. Cool: 82°F / Heat: 58°F). Turning it off automatically resumes the schedule slot for the current time of day.
* 🤝 **Two-Way Wall Dial Sync:** If someone physically turns the dial on the wall unit or flips the wall switch OFF, `smart_central_climate` catches the change and syncs its state without fighting back or misinterpreting routine idle states.
* ⏱️ **Smart Away (Errand Grace Period):** Leaving home starts a configurable grace timer (default: 60 minutes). Quick trips to the grocery store will not disrupt your A/C; only if you remain away does it shift to Away setpoints.
* 🛡️ **Pre-Cooling Schedule Immunity:** When your schedule triggers Comfort mode (e.g. at 17:00 / 5 PM), cooling engages and activates an Away Immunity Window (default: 60 minutes). Away presence checks are locked out so your home is chilled before you arrive.
* 🎛️ **Full UI Configuration & Options Flow:** Set up directly in the Home Assistant UI, and adjust any setpoint, schedule slot, swing, or timer at any time under **Settings > Devices & Services > Configure**. Survives restarts and reloads seamlessly via `RestoreEntity`.

---

## Installation via HACS

1. Open Home Assistant > **HACS** > **Integrations**.
2. Click the three dots in the top right > **Custom repositories**.
3. Paste your repository URL: `https://github.com/Tinkergnome621/smart_central_climate`.
4. Category: **Integration** > Click **Add**.
5. Find **Smart Central Climate** in HACS and click **Download** (select version `v1.2.0`).
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
4. Confirm your default temperatures, swings, and vacation hold setpoints.
5. Set your **4 Weekday** and **4 Weekend** schedule slots.
6. Click **Submit**.

---

## Adjusting Schedules & Settings Anytime

You never need to edit YAML or reinstall. In Home Assistant:
1. Go to **Settings** > **Devices & Services**.
2. Find **Smart Central Climate** and click **Configure**.
3. Choose what to modify:
   * **Temperature Presets, Swings & Vacation**
   * **Monday – Friday Schedule (4 Slots)**
   * **Saturday – Sunday Schedule (4 Slots)**
   * **Errand Grace Delay & Away Immunity**
4. Adjust and click **Submit**.

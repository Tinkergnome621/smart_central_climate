# Smart Central Climate

A custom Home Assistant integration designed specifically for **Central A/C and Heat Pump Systems**. It wraps your physical smart thermostat (like Meross Matter, Nest, Ecobee, Honeywell, Z-Wave) and links it with remote room temperature sensors, smart presence grace periods, built-in 4-slot daily schedules, vacation mode, and compressor-safe hysteresis.

---

## Key Features

* 🛑 **Guaranteed Blower Fan Shutoff:** When cooling or heating idles, both the thermostat and any paired blower fan entity (`fan.*`) are shut off, eliminating the common issue of blower fans running non-stop.
* 📅 **Built-in 4-Slot Daily Schedules:**
  * **Monday – Friday (4 Periods):** e.g., Wake (06:30), Work/Day (08:30), Return/Pre-Cool (17:00), Night/Sleep (22:30).
  * **Saturday – Sunday (4 Periods):** e.g., Wake (08:00), Day (11:00), Evening (17:30), Night/Sleep (23:00).
  * Set both the time and the preset (`comfort`, `eco`, `away`, `sleep`, `boost`) for each slot directly in the UI!
* ✈️ **Dedicated Vacation Mode:**
  * One-tap Vacation preset and dedicated toggle switch (`switch.<name>_vacation_mode`).
  * Suspends all schedules, presence triggers, and errand timers while maintaining deep energy-saving vacation hold temperatures (e.g. Cool: 82°F / Heat: 58°F).
* 🌡️ **Remote Temperature Follower:** Controls cooling and heating based on an external room sensor (e.g. `sensor.average_house_temperature`) instead of the wall thermostat's internal probe.
* 🔄 **Compressor-Safe Hysteresis:** Configurable activation and deactivation swings (e.g. 3.0°F) to ensure long, steady cycles that protect compressor life and properly dehumidify your home.
* 🤝 **Two-Way Wall Dial Sync:** If someone physically turns the dial on the wall unit, `smart_central_climate` catches the change and syncs its target setpoint without fighting back.
* ⏱️ **Smart Away (Errand Grace Period):** Leaving home starts a configurable grace timer (default: 60 minutes). Quick trips to the grocery store will not disrupt your A/C; only if you remain away does it shift to Away setpoints.
* 🛡️ **Pre-Cooling Schedule Immunity:** When your schedule triggers Comfort mode (e.g. at 17:00 / 5 PM), cooling engages and activates an Away Immunity Window (default: 60 minutes). Away presence checks are locked out so your home is chilled before you arrive.
* 🎛️ **Full UI Configuration & Options Flow:** Set up directly in the Home Assistant UI, and adjust any setpoint, schedule slot, swing, or timer at any time under **Settings > Devices & Services > Configure**.
* 🎨 **Universal Card Compatibility:** Works with the **Better Thermostat UI Card**, **Equinox Card**, and standard Home Assistant thermostat cards with one-tap **Home, Away, Comfort, Eco, Sleep, Boost, and Vacation** buttons.

---

## Installation via HACS

1. Open Home Assistant > **HACS** > **Integrations**.
2. Click the three dots in the top right > **Custom repositories**.
3. Paste your repository URL: `https://github.com/Tinkergnome621/smart_central_climate`.
4. Category: **Integration** > Click **Add**.
5. Find **Smart Central Climate** in HACS and click **Download**.
6. Restart Home Assistant.

---

## Setup in Home Assistant

1. Go to **Settings** > **Devices & Services** > **Add Integration**.
2. Search for **Smart Central Climate**.
3. Select your entities:
   * **Physical Thermostat:** (e.g., `climate.hallway_thermostat`)
   * **Blower Fan Entity (Optional):** (e.g., `fan.hallway_thermostat`)
   * **Remote Temperature Sensor:** (e.g., `sensor.average_house_temperature`)
   * **Presence Sensor (Optional):** (e.g., `person.mike_ratliff`)
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

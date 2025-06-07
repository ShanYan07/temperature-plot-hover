# Interactive Temperature Plot from Numbers

This repository provides:

- **iOS Shortcut** to periodically read a HomeKit temperature sensor and append timestamped readings to an iCloud Numbers document.
- **Python script** (`temperature_plot_with_hover.py`) to read that Numbers file, generate an interactive temperature-vs-time plot with:
  - 30‑minute major ticks on the x‑axis
  - Red dashed line at daily midnight (00:00)
  - Date labels centered above each day
  - Hover annotations showing timestamp, temperature (1 decimal), and estimated slope (°C/hour)

---

## Background

Apple’s Home app does not provide built‑in historical temperature curves. We use an **iOS Shortcut** to:

1. **Periodically** (every 30 minutes) poll a HomeKit temperature sensor.
2. **Append** readings (timestamp and temperature) into an iCloud Numbers spreadsheet.

The **Python script** then reads the Numbers file and renders an interactive plot on macOS.

---

## Requirements

- **iOS Device** (iPhone/iPad) on same Apple ID as macOS, **no lock‑screen passcode** to allow unlocked automations.
- **iCloud Numbers** document with a table containing two columns: `Time` and `Temp`.
- **macOS** with Python 3 and packages:
  ```bash
  pip3 install pandas matplotlib openpyxl numbers-parser
  ```

---

## iOS Shortcut Setup

1. **Create Numbers Document**
   - Path: `iCloud Drive › Numbers › temperature_chart.numbers`
   - Table 1 columns: `Time` (Text), `Temp` (Number).

2. **Configure Shortcut Automation**
   - In **Shortcuts** app → **Automation** → **Create Personal Automation** → **Time of Day**.
   - Trigger **Every Day**, at **00:00, 00:30, 01:00...** (add as needed).
   - **Disable** "Ask Before Running".

3. **Add Actions**
   1. **Get Sensor State**
      - Action: **Get State** → select your HomeKit temperature sensor → choose **Current Temperature**.
   2. **Get Current Date**
      - Action: **Get Current Date** → **Format**: `yyyyMMdd HH:mm:ss`.
   3. **Add Record to Numbers Table**
      - Action: **Add Row to Numbers Table** → select `temperature_chart.numbers` → Table 1.
      - Map `Time` to the formatted date, `Temp` to the sensor value.

4. **Test**
   - Manually run the automation to verify a row is appended.
   - The Numbers table should show entries like:
     | Time                   | Temp   |
     | -------------------- | ---- |
     | 2025年06月05日 16:52:00 | 23.4 |

---

## Python Script Usage

1. **Place Files Together**
   - Ensure your `.numbers` document (e.g., `temperature_chart.numbers`) and the `temperature_plot_with_hover.py` script reside in the **same folder**.  
   - For automatic iCloud synchronization, that folder can be your **iCloud Drive › Numbers** directory (e.g., `~/Library/Mobile Documents/com~apple~Numbers/Documents`).
2. **Open Terminal and Navigate**
   ```bash
   cd ~/Library/"Mobile Documents"/com~apple~Numbers/Documents
   ```
3. **Run the Script**
   ```bash
   python3 temperature_plot_with_hover.py temperature_chart.numbers
   ```

---

## License

This project is released under the [MIT License](LICENSE).



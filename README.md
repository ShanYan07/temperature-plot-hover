# Writing README.md to file for user to download
readme_content = """# Interactive Temperature Plot from Numbers

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
- **iCloud Numbers** document with a table containing two columns: `时间` and `温度`.
- **macOS** with Python 3 and packages:
  ```bash
  pip3 install pandas matplotlib openpyxl numbers-parser

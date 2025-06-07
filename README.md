# temperature-plot-hover
Interactive temperature-time plot from macOS Numbers with hover annotations (time, temperature, slope) and daily markers.
## Background

The stock Apple Home app does not provide built-in support for rendering historical temperature curves. To overcome this limitation, we leverage the iOS Shortcuts app to:

1. **Periodically** (e.g. every 30 minutes) poll temperature sensors in your HomeKit setup.  
2. **Append** each reading (timestamp + temperature) into a Numbers spreadsheet stored in iCloud.  

This repository contains a Python script that reads that Numbers file, generates an interactive temperature-vs-time plot (with hover annotations, daily markers, and slope information), and displays it on macOS.  

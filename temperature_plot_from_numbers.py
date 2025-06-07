#!/usr/bin/env python3
# temperature_plot_with_hover.py
#
# Functionality:
#   - Reads "Time" and "Temperature" columns from a Numbers file;
#   - Plots a time series line chart of temperature:
#       • Major ticks every 30 minutes;
#       • Red dashed line at 00:00 each day;
#       • Date labels centered above the x-axis;
#       • Tooltip on hover showing time, temperature, and slope (°C/hour).
#
# Usage:
#   pip3 install pandas matplotlib openpyxl numbers-parser
#   python3 temperature_plot_with_hover.py blank.numbers

import sys
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import matplotlib
matplotlib.use('TkAgg')  # Use TkAgg backend for interactivity

from numbers_parser import Document


def find_header_row(rows, max_scan=10):
    for i in range(min(max_scan, len(rows))):
        texts = [(c.value.strip() if c and isinstance(c.value, str) else c.value) for c in rows[i]]
        if any(t == "时间" for t in texts if isinstance(t, str)) and any("温度" in t for t in texts if isinstance(t, str)):
            return i, texts
    return None, None


def read_numbers(path):
    doc = Document(path)
    sheet = doc.sheets[0]
    table = sheet.tables[0]
    rows = table.rows()
    header_idx, headers = find_header_row(rows)
    if header_idx is None:
        raise RuntimeError('Header row containing "时间" and "温度" not found.')
    idx_time = headers.index("时间")
    idx_temp = next(i for i, h in enumerate(headers) if isinstance(h, str) and "温度" in h)
    data = []
    for r in rows[header_idx + 1:]:
        if r[idx_time] and r[idx_temp]:
            data.append((r[idx_time].value, r[idx_temp].value))
    if not data:
        raise RuntimeError("No data rows found.")
    return pd.DataFrame(data, columns=["Time", "Temperature"])


def format_annotation(ts, temp, slope):
    return f"{ts.strftime('%Y-%m-%d %H:%M:%S')}\nTemp: {temp:.1f}°C\nSlope: {slope:+.2f} °C/h"


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path to .numbers file>")
        sys.exit(1)
    path = sys.argv[1]

    # Read and preprocess data
    df = read_numbers(path)
    df = df.dropna().copy()
    try:
        df["Time"] = pd.to_datetime(df["Time"], format="%Y年%m月%d日 %H:%M")
    except:
        df["Time"] = pd.to_datetime(df["Time"])
    df["Temperature"] = df["Temperature"].astype(str).str.replace("°C", "", regex=False).astype(float)
    df = df.sort_values("Time").reset_index(drop=True)

    # Plotting settings
    plt.rcParams["font.sans-serif"] = ["Arial Unicode MS"]
    plt.rcParams["axes.unicode_minus"] = False

    fig, ax = plt.subplots(figsize=(12, 6))
    x_dates = df["Time"]
    y = df["Temperature"]
    x = mdates.date2num(x_dates)
    line = ax.plot(x, y, '-o', color="tab:blue", picker=5)[0]

    # Axis settings
    ax.set_ylim(17, 33)
    ax.set_yticks(np.arange(18, 32.1, 0.5))
    ax.set_ylabel("Temperature (°C)")
    tmin, tmax = x.min(), x.max()
    ax.set_xlim(tmin, tmax)
    ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=30))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    plt.xticks(rotation=45)

    # Red dashed line at 00:00 each day
    dates = df["Time"].dt.date.unique()
    for d in dates:
        mid = pd.to_datetime(f"{d} 00:00:00")
        num = mdates.date2num(mid)
        if tmin <= num <= tmax:
            ax.axvline(num, color="red", linewidth=2, linestyle="--")

    # Centered date labels above x-axis
    y_label_pos = 18.2
    for d, group in df.groupby(df["Time"].dt.date):
        start = mdates.date2num(group["Time"].iloc[0])
        end = mdates.date2num(group["Time"].iloc[-1])
        mid = start + (end - start) / 2
        ax.text(mid, y_label_pos, d.strftime("%Y-%m-%d"), ha="center", va="bottom", fontsize=9, backgroundcolor="white", clip_on=True)

    # Annotation box setup
    annot = ax.annotate("", xy=(0, 0), xytext=(10, 10), textcoords="offset points",
                        bbox=dict(boxstyle="round,pad=0.5", fc="w", ec="gray"),
                        arrowprops=dict(arrowstyle="->"))
    annot.set_visible(False)

    def compute_slope(idx):
        # Estimate slope (°C/hour) using central difference
        if idx <= 0:
            idx0, idx1 = 0, 1
        elif idx >= len(df) - 1:
            idx0, idx1 = len(df) - 2, len(df) - 1
        else:
            idx0, idx1 = idx - 1, idx + 1
        t0 = df["Time"].iloc[idx0]
        t1 = df["Time"].iloc[idx1]
        y0 = df["Temperature"].iloc[idx0]
        y1 = df["Temperature"].iloc[idx1]
        hours = (t1 - t0).total_seconds() / 3600
        if hours == 0:
            return 0.0
        return (y1 - y0) / hours

    def update_annot(ind):
        idx = ind["ind"][0]
        xx = x[idx]
        yy = y.iloc[idx]
        slope = compute_slope(idx)
        annot.xy = (xx, yy)
        txt = format_annotation(x_dates.iloc[idx], yy, slope)
        annot.set_text(txt)
        annot.get_bbox_patch().set_alpha(0.9)

    def hover(event):
        if event.inaxes == ax:
            cont, ind = line.contains(event)
            if cont:
                update_annot(ind)
                annot.set_visible(True)
                fig.canvas.draw_idle()
            else:
                if annot.get_visible():
                    annot.set_visible(False)
                    fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", hover)

    plt.title("Temperature Over Time (Hover to Show Details + Slope + Date + 00:00 Mark)")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# temperature_plot_with_hover.py
#
# 功能：
#   - 从 Numbers 文件读取“时间”和“温度”列；
#   - 绘制温度随时间变化折线图：
#       • 每 30 分钟主刻度；
#       • 每日 00:00 红色虚线标记；
#       • 横轴上方居中显示每天日期；
#       • 鼠标悬停采样点时显示对话气泡，包含时间、温度及当前斜率（°C/小时）。
#
# 使用：
#   pip3 install pandas matplotlib openpyxl numbers-parser
#   python3 temperature_plot_with_hover.py 空白.numbers

import sys
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import matplotlib
matplotlib.use('TkAgg')  # 使用 TkAgg 后端以支持交互

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
        raise RuntimeError("未找到包含“时间”和“温度”的表头行")
    idx_time = headers.index("时间")
    idx_temp = next(i for i, h in enumerate(headers) if isinstance(h, str) and "温度" in h)
    data = []
    for r in rows[header_idx + 1:]:
        if r[idx_time] and r[idx_temp]:
            data.append((r[idx_time].value, r[idx_temp].value))
    if not data:
        raise RuntimeError("数据行为空")
    return pd.DataFrame(data, columns=["时间", "温度"])


def format_annotation(ts, temp, slope):
    return f"{ts.strftime('%Y-%m-%d %H:%M:%S')}\n温度: {temp:.1f}°C\n斜率: {slope:+.2f} °C/h"


def main():
    if len(sys.argv) != 2:
        print(f"用法: {sys.argv[0]} <.numbers 文件路径>")
        sys.exit(1)
    path = sys.argv[1]

    # 读取并处理数据
    df = read_numbers(path)
    df = df.dropna().copy()
    try:
        df["时间"] = pd.to_datetime(df["时间"], format="%Y年%m月%d日 %H:%M")
    except:
        df["时间"] = pd.to_datetime(df["时间"])
    df["温度"] = df["温度"].astype(str).str.replace("°C", "", regex=False).astype(float)
    df = df.sort_values("时间").reset_index(drop=True)

    # 绘图设置
    plt.rcParams["font.sans-serif"] = ["Arial Unicode MS"]
    plt.rcParams["axes.unicode_minus"] = False

    fig, ax = plt.subplots(figsize=(12, 6))
    x_dates = df["时间"]
    y = df["温度"]
    x = mdates.date2num(x_dates)
    line = ax.plot(x, y, '-o', color="tab:blue", picker=5)[0]

    # 坐标轴设置
    ax.set_ylim(17, 33)
    ax.set_yticks(np.arange(18, 32.1, 0.5))
    ax.set_ylabel("温度 (°C)")
    tmin, tmax = x.min(), x.max()
    ax.set_xlim(tmin, tmax)
    # 恢复每 30 分钟一个主刻度
    ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=30))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    plt.xticks(rotation=45)

    # 每日 00:00 红虚线
    dates = df["时间"].dt.date.unique()
    for d in dates:
        mid = pd.to_datetime(f"{d} 00:00:00")
        num = mdates.date2num(mid)
        if tmin <= num <= tmax:
            ax.axvline(num, color="red", linewidth=2, linestyle="--")

    # 横轴上方居中显示每天日期
    y_label_pos = 18.2
    for d, group in df.groupby(df["时间"].dt.date):
        start = mdates.date2num(group["时间"].iloc[0])
        end = mdates.date2num(group["时间"].iloc[-1])
        mid = start + (end - start) / 2
        ax.text(mid, y_label_pos, d.strftime("%Y-%m-%d"), ha="center", va="bottom", fontsize=9, backgroundcolor="white", clip_on=True)

    # 注释框初始化
    annot = ax.annotate("", xy=(0, 0), xytext=(10, 10), textcoords="offset points",
                        bbox=dict(boxstyle="round,pad=0.5", fc="w", ec="gray"),
                        arrowprops=dict(arrowstyle="->"))
    annot.set_visible(False)

    def compute_slope(idx):
        # 使用中心差分估算斜率 (°C/h)
        if idx <= 0:
            idx0, idx1 = 0, 1
        elif idx >= len(df) - 1:
            idx0, idx1 = len(df) - 2, len(df) - 1
        else:
            idx0, idx1 = idx - 1, idx + 1
        t0 = df["时间"].iloc[idx0]
        t1 = df["时间"].iloc[idx1]
        y0 = df["温度"].iloc[idx0]
        y1 = df["温度"].iloc[idx1]
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

    plt.title("温度随时间变化（悬停显示详情 + 斜率 + 日期标注 + 00:00 标记）")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()

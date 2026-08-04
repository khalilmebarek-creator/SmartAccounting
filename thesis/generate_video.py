# -*- coding: utf-8 -*-
"""
Generate MP4 video from tutorial slides.
Each slide shows for 6 seconds with 1-second crossfade transitions.
Output: thesis/SmartAccounting_Tutorial.mp4
"""
import os
from moviepy import ImageClip, concatenate_videoclips

SLIDES_DIR = os.path.join("thesis", "video_slides")
OUTPUT = os.path.join("thesis", "SmartAccounting_Tutorial.mp4")

# Slide order and duration (seconds each)
slides = [
    ("slide_01_opening.png",      5),   # logo reveal
    ("slide_02_login.png",        7),   # login + getting started
    ("slide_03_navigation.png",   7),   # sidebar + shortcuts
    ("slide_04_data_entry.png",   8),   # data entry walkthrough
    ("slide_05_ratios.png",       7),   # dashboard + 20 ratios
    ("slide_06_advanced.png",     7),   # duPont + z-score + scenarios
    ("slide_07_tax.png",          9),   # 6 tax calculators + calendar
    ("slide_08_ai.png",           7),   # AI insights + forecasting
    ("slide_09_productivity.png", 7),   # cloud + import + export
    ("slide_10_security.png",     7),   # security + architecture + perf
    ("slide_11_closing.png",      5),   # closing + CTA
]

def build_video():
    clips = []
    for fname, duration in slides:
        path = os.path.join(SLIDES_DIR, fname)
        if not os.path.exists(path):
            print(f"  SKIP (not found): {fname}")
            continue
        clip = ImageClip(path).with_duration(duration)
        clips.append(clip)
        print(f"  Added: {fname} ({duration}s)")

    if not clips:
        print("No slides found!")
        return

    # concatenate with crossfade
    final = concatenate_videoclips(clips, method="compose")

    print(f"\nRendering video... ({final.duration:.0f}s total)")
    final.write_videofile(
        OUTPUT,
        fps=24,
        codec="libx264",
        audio=False,
        preset="medium",
        bitrate="5000k",
        logger="bar",
    )
    print(f"\nDone! Video saved to: {OUTPUT}")
    print(f"Duration: {final.duration:.0f} seconds")
    print(f"Size: {os.path.getsize(OUTPUT) / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    build_video()
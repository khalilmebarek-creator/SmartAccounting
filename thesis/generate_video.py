# -*- coding: utf-8 -*-
"""
Generate MP4 video from tutorial slides with background ambient music.
Each slide shows for several seconds with smooth transitions.
Output: thesis/SmartAccounting_Tutorial.mp4
"""
import os
import numpy as np
from moviepy import ImageClip, AudioArrayClip, concatenate_videoclips

SLIDES_DIR = os.path.join("thesis", "video_slides")
OUTPUT = os.path.join("thesis", "SmartAccounting_Tutorial.mp4")

slides = [
    ("slide_01_opening.png",      5),
    ("slide_02_login.png",        7),
    ("slide_03_navigation.png",   7),
    ("slide_04_data_entry.png",   8),
    ("slide_05_ratios.png",       7),
    ("slide_06_advanced.png",     7),
    ("slide_07_tax.png",          9),
    ("slide_08_ai.png",           7),
    ("slide_09_productivity.png", 7),
    ("slide_10_security.png",     7),
    ("slide_11_closing.png",      5),
]


def _generate_ambient_music(duration_s, sample_rate=44100):
    """Generate a calm ambient background track (soft pads + gentle arpeggios)."""
    t = np.linspace(0, duration_s, int(sample_rate * duration_s), endpoint=False)

    # warm pad chords (C major 7 voicing)
    pad = np.zeros_like(t)
    for freq in [130.81, 164.81, 196.00, 246.94]:
        pad += np.sin(2 * np.pi * freq * t) * 0.06
    # slow LFO for movement
    lfo = 0.5 + 0.5 * np.sin(2 * np.pi * 0.08 * t)
    pad *= lfo

    # high shimmer (octave up, very soft)
    shimmer = np.sin(2 * np.pi * 523.25 * t) * 0.015 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.12 * t))

    # gentle arpeggio (root-3rd-5th-octave cycling)
    arp_freqs = [261.63, 329.63, 392.00, 523.25]
    arp = np.zeros_like(t)
    cycle_len = 0.5  # seconds per note
    for i, freq in enumerate(arp_freqs):
        mask = np.zeros_like(t)
        start = i * cycle_len
        while start < duration_s:
            env = np.exp(-3.0 * (t - start) / cycle_len)
            env = np.clip(env, 0, 1)
            mask += env * (t >= start)
            start += len(arp_freqs) * cycle_len
        arp += np.sin(2 * np.pi * freq * t) * mask * 0.025

    mix = pad + shimmer + arp

    # fade in 2s, fade out 3s
    fade_in = np.clip(t / 2.0, 0, 1)
    fade_out = np.clip((duration_s - t) / 3.0, 0, 1)
    mix *= fade_in * fade_out

    # normalize
    peak = np.max(np.abs(mix))
    if peak > 0:
        mix = mix / peak * 0.35

    # stereo
    stereo = np.column_stack([mix, mix])
    return stereo, sample_rate


def build_video():
    clips = []
    total_duration = sum(d for _, d in slides)
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

    final = concatenate_videoclips(clips, method="compose")

    print(f"\nGenerating ambient music... ({total_duration}s)")
    audio_data, sr = _generate_ambient_music(total_duration + 1)
    audio_clip = AudioArrayClip(audio_data, fps=sr).with_duration(total_duration)

    print(f"Rendering video... ({final.duration:.0f}s total)")
    final.with_audio(audio_clip).write_videofile(
        OUTPUT,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        bitrate="5000k",
        preset="medium",
        logger="bar",
    )
    print(f"\nDone! Video saved to: {OUTPUT}")
    print(f"Duration: {final.duration:.0f} seconds")
    print(f"Size: {os.path.getsize(OUTPUT) / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    build_video()